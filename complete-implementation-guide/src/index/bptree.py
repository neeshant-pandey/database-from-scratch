"""
B+ Tree Index implementation.
"""

from typing import Optional, Iterator, Tuple
from ..common.types import PageId, RID
from ..common.constants import PageType, INVALID_PAGE_ID
from ..storage.buffer_pool_manager import BufferPoolManager
from .bptree_node import BPTreeLeafNode, BPTreeInternalNode


class BPTreeIndex:
    """
    B+ Tree index for fast key lookups and range scans.
    """

    def __init__(self, buffer_pool: BufferPoolManager, root_page_id: Optional[PageId] = None):
        self.buffer_pool = buffer_pool
        self.root_page_id = root_page_id

        if self.root_page_id is None:
            # Create root as leaf page
            root_page = self.buffer_pool.new_page()
            if root_page is None:
                raise RuntimeError("Failed to create B+ tree root")

            root_page.page_type = PageType.BPTREE_LEAF
            self.root_page_id = root_page.page_id

            # Initialize as leaf
            leaf = BPTreeLeafNode(root_page)
            leaf.serialize()

            self.buffer_pool.unpin_page(root_page.page_id, True)

    def search(self, key: int) -> Optional[RID]:
        """
        Search for a key in the B+ tree.
        Returns RID if found, None otherwise.
        """
        leaf_page = self._find_leaf(key)
        if leaf_page is None:
            return None

        leaf = BPTreeLeafNode(leaf_page)
        leaf.deserialize()

        rid = leaf.search(key)

        self.buffer_pool.unpin_page(leaf_page.page_id, False)
        return rid

    def insert(self, key: int, rid: RID) -> bool:
        """
        Insert a key-value pair into the B+ tree.
        """
        leaf_page = self._find_leaf(key)
        if leaf_page is None:
            return False

        leaf = BPTreeLeafNode(leaf_page)
        leaf.deserialize()

        # Try to insert into leaf
        if leaf.insert(key, rid):
            self.buffer_pool.unpin_page(leaf_page.page_id, True)
            return True

        # Leaf is full - need to split (simplified, not implemented here)
        self.buffer_pool.unpin_page(leaf_page.page_id, False)
        return False  # For now, fail if page is full

    def range_scan(self, start_key: int, end_key: int) -> Iterator[Tuple[int, RID]]:
        """
        Range scan: yield all (key, rid) pairs where start_key <= key <= end_key.
        """
        # Find leaf with start_key
        leaf_page = self._find_leaf(start_key)
        if leaf_page is None:
            return

        current_page_id = leaf_page.page_id
        self.buffer_pool.unpin_page(current_page_id, False)

        # Scan leaves following sibling pointers
        while current_page_id != INVALID_PAGE_ID:
            page = self.buffer_pool.fetch_page(current_page_id)
            if page is None:
                break

            leaf = BPTreeLeafNode(page)
            leaf.deserialize()

            # Yield keys in this leaf
            for i in range(leaf.size):
                key = leaf.keys[i]
                if key > end_key:
                    self.buffer_pool.unpin_page(current_page_id, False)
                    return
                if key >= start_key:
                    yield (key, leaf.rids[i])

            # Move to next leaf
            next_page_id = leaf.next_page_id
            self.buffer_pool.unpin_page(current_page_id, False)
            current_page_id = next_page_id

    def _find_leaf(self, key: int) -> Optional['Page']:
        """
        Traverse tree from root to find leaf page for given key.
        Returns pinned page (caller must unpin).
        """
        current_page_id = self.root_page_id

        while current_page_id != INVALID_PAGE_ID:
            page = self.buffer_pool.fetch_page(current_page_id)
            if page is None:
                return None

            # Check if leaf
            if page.page_type == PageType.BPTREE_LEAF:
                return page  # Return pinned leaf page

            # Internal node - find next child
            internal = BPTreeInternalNode(page)
            internal.deserialize()

            child_idx = internal.find_child(key)
            next_page_id = internal.children[child_idx]

            self.buffer_pool.unpin_page(current_page_id, False)
            current_page_id = next_page_id

        return None
