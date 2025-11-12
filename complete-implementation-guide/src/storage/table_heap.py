"""
Table Heap: manages table data using slotted pages.
"""

from typing import Iterator, Optional, List
from ..common.types import RID, PageId, SlotId
from ..common.constants import PageType
from .buffer_pool_manager import BufferPoolManager
from .slotted_page import SlottedPage


class TableHeap:
    """
    Table heap stores tuples across multiple slotted pages.
    """

    def __init__(self, buffer_pool: BufferPoolManager, first_page_id: Optional[PageId] = None):
        self.buffer_pool = buffer_pool
        self.first_page_id = first_page_id

        if self.first_page_id is None:
            # Create first page
            page = self.buffer_pool.new_page()
            if page is None:
                raise RuntimeError("Failed to allocate first page for table")
            page.page_type = PageType.DATA
            self.first_page_id = page.page_id
            self.buffer_pool.unpin_page(page.page_id, True)

    def insert_tuple(self, tuple_data: bytes) -> Optional[RID]:
        """
        Insert a tuple into the table.
        Returns RID of inserted tuple, or None on failure.
        """
        # Try to find a page with enough space
        page_id = self.first_page_id

        while page_id is not None:
            page = self.buffer_pool.fetch_page(page_id)
            if page is None:
                break

            slotted_page = SlottedPage(page)
            slot_id = slotted_page.insert_tuple(tuple_data)

            if slot_id is not None:
                # Success
                rid = RID(page_id, slot_id)
                self.buffer_pool.unpin_page(page_id, True)
                return rid

            # Page is full, try next page
            # For simplicity, we don't track next page here
            # In real implementation, would maintain linked list of pages
            self.buffer_pool.unpin_page(page_id, False)
            break

        # No page with space found, allocate new page
        new_page = self.buffer_pool.new_page()
        if new_page is None:
            return None

        new_page.page_type = PageType.DATA
        slotted_page = SlottedPage(new_page)
        slot_id = slotted_page.insert_tuple(tuple_data)

        if slot_id is None:
            self.buffer_pool.unpin_page(new_page.page_id, False)
            return None

        rid = RID(new_page.page_id, slot_id)
        self.buffer_pool.unpin_page(new_page.page_id, True)
        return rid

    def get_tuple(self, rid: RID) -> Optional[bytes]:
        """Get tuple data by RID."""
        page = self.buffer_pool.fetch_page(rid.page_id)
        if page is None:
            return None

        slotted_page = SlottedPage(page)
        tuple_data = slotted_page.get_tuple(rid.slot_id)

        self.buffer_pool.unpin_page(rid.page_id, False)
        return tuple_data

    def delete_tuple(self, rid: RID) -> bool:
        """Delete tuple by RID."""
        page = self.buffer_pool.fetch_page(rid.page_id)
        if page is None:
            return False

        slotted_page = SlottedPage(page)
        success = slotted_page.delete_tuple(rid.slot_id)

        self.buffer_pool.unpin_page(rid.page_id, success)
        return success

    def update_tuple(self, rid: RID, new_data: bytes) -> bool:
        """Update tuple by RID."""
        page = self.buffer_pool.fetch_page(rid.page_id)
        if page is None:
            return False

        slotted_page = SlottedPage(page)
        success = slotted_page.update_tuple(rid.slot_id, new_data)

        self.buffer_pool.unpin_page(rid.page_id, success)
        return success

    def scan(self) -> Iterator[tuple]:
        """
        Scan all tuples in the table.
        Yields (RID, tuple_data) for each tuple.
        """
        # Simplified: only scan first page
        # Real implementation would scan all pages
        page_id = self.first_page_id

        while page_id is not None:
            page = self.buffer_pool.fetch_page(page_id)
            if page is None:
                break

            slotted_page = SlottedPage(page)
            num_slots, _ = slotted_page._read_header()

            for slot_id in range(num_slots):
                tuple_data = slotted_page.get_tuple(SlotId(slot_id))
                if tuple_data is not None:
                    yield (RID(page_id, SlotId(slot_id)), tuple_data)

            self.buffer_pool.unpin_page(page_id, False)
            break  # For simplicity, only scan first page
