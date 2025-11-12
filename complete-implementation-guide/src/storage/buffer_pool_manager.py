"""
Buffer Pool Manager: manages in-memory page caching with LRU replacement.
"""

import threading
from collections import OrderedDict
from typing import Optional, Dict
from ..common.types import PageId
from ..common.constants import INVALID_PAGE_ID
from .page import Page
from .disk_manager import DiskManager


class BufferPoolManager:
    """
    Manages a pool of pages in memory with LRU eviction policy.

    Uses OrderedDict for O(1) LRU operations.
    """

    def __init__(self, disk_manager: DiskManager, pool_size: int = 100):
        self.disk_manager = disk_manager
        self.pool_size = pool_size

        # Page table: page_id -> Page
        self.pages: Dict[PageId, Page] = {}

        # LRU tracking using OrderedDict (insertion order = access order)
        self.lru_order: OrderedDict[PageId, None] = OrderedDict()

        # Free frames (available slots in buffer pool)
        self.free_frames = pool_size

        # Lock for thread-safety
        self.lock = threading.RLock()

        # Statistics
        self.num_hits = 0
        self.num_misses = 0
        self.num_evictions = 0

    def fetch_page(self, page_id: PageId) -> Optional[Page]:
        """
        Fetch a page from buffer pool. Load from disk if not in pool.
        Page is pinned on return.
        """
        with self.lock:
            # Page already in buffer pool
            if page_id in self.pages:
                page = self.pages[page_id]
                page.pin()
                self._update_lru(page_id)
                self.num_hits += 1
                return page

            # Page not in buffer pool - need to load from disk
            self.num_misses += 1

            # Find a free frame or evict a page
            if self.free_frames == 0:
                evicted_page_id = self._evict_page()
                if evicted_page_id is None:
                    # No page can be evicted (all pinned)
                    return None
            else:
                self.free_frames -= 1

            # Read page from disk
            page = self.disk_manager.read_page(page_id)
            page.pin()

            # Add to buffer pool
            self.pages[page_id] = page
            self._update_lru(page_id)

            return page

    def unpin_page(self, page_id: PageId, is_dirty: bool) -> bool:
        """
        Unpin a page. If is_dirty=True, mark page as dirty.
        Returns False if page not in buffer pool.
        """
        with self.lock:
            if page_id not in self.pages:
                return False

            page = self.pages[page_id]
            page.unpin()

            if is_dirty:
                page.is_dirty = True

            return True

    def flush_page(self, page_id: PageId) -> bool:
        """
        Flush a specific page to disk if dirty.
        """
        with self.lock:
            if page_id not in self.pages:
                return False

            page = self.pages[page_id]
            if page.is_dirty:
                self.disk_manager.write_page(page)
                page.is_dirty = False

            return True

    def flush_all_pages(self) -> None:
        """Flush all dirty pages to disk."""
        with self.lock:
            for page in self.pages.values():
                if page.is_dirty:
                    self.disk_manager.write_page(page)
                    page.is_dirty = False

    def new_page(self) -> Optional[Page]:
        """
        Allocate a new page. Returns pinned page.
        """
        with self.lock:
            # Find free frame or evict
            if self.free_frames == 0:
                evicted_page_id = self._evict_page()
                if evicted_page_id is None:
                    return None
            else:
                self.free_frames -= 1

            # Allocate new page on disk
            page_id = self.disk_manager.allocate_page()

            # Create new page
            page = Page(page_id)
            page.pin()

            # Add to buffer pool
            self.pages[page_id] = page
            self._update_lru(page_id)

            return page

    def delete_page(self, page_id: PageId) -> bool:
        """
        Delete a page from buffer pool and disk.
        Page must be unpinned.
        """
        with self.lock:
            if page_id in self.pages:
                page = self.pages[page_id]
                if page.is_pinned():
                    return False

                # Remove from buffer pool
                del self.pages[page_id]
                if page_id in self.lru_order:
                    del self.lru_order[page_id]
                self.free_frames += 1

            # Deallocate on disk
            self.disk_manager.deallocate_page(page_id)
            return True

    def _evict_page(self) -> Optional[PageId]:
        """
        Evict a page using LRU policy.
        Returns page_id of evicted page, or None if no page can be evicted.
        """
        # Find oldest unpinned page
        for page_id in list(self.lru_order.keys()):
            page = self.pages[page_id]
            if not page.is_pinned():
                # Flush if dirty
                if page.is_dirty:
                    self.disk_manager.write_page(page)

                # Remove from buffer pool
                del self.pages[page_id]
                del self.lru_order[page_id]
                self.num_evictions += 1

                return page_id

        # No page can be evicted (all pinned)
        return None

    def _update_lru(self, page_id: PageId) -> None:
        """Update LRU order (move to end = most recently used)."""
        if page_id in self.lru_order:
            self.lru_order.move_to_end(page_id)
        else:
            self.lru_order[page_id] = None

    def get_stats(self) -> Dict[str, any]:
        """Return buffer pool statistics."""
        total_accesses = self.num_hits + self.num_misses
        hit_rate = self.num_hits / total_accesses if total_accesses > 0 else 0.0

        return {
            'pool_size': self.pool_size,
            'pages_in_pool': len(self.pages),
            'free_frames': self.free_frames,
            'num_hits': self.num_hits,
            'num_misses': self.num_misses,
            'num_evictions': self.num_evictions,
            'hit_rate': hit_rate
        }
