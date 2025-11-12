"""
B+ Tree Node structures (leaf and internal nodes).
"""

import struct
from typing import List, Optional, Tuple
from ..common.types import PageId, RID
from ..common.constants import INVALID_PAGE_ID, BPTREE_LEAF_MAX_SIZE, BPTREE_INTERNAL_MAX_SIZE
from ..storage.page import Page


class BPTreeNode:
    """Base class for B+ tree nodes."""

    def __init__(self, page: Page, is_leaf: bool, max_size: int):
        self.page = page
        self.is_leaf = is_leaf
        self.max_size = max_size
        self.size = 0  # Number of keys
        self.parent_page_id = PageId(INVALID_PAGE_ID)

    def is_full(self) -> bool:
        return self.size >= self.max_size

    def is_underflow(self) -> bool:
        return self.size < self.max_size // 2

    def is_empty(self) -> bool:
        return self.size == 0


class BPTreeLeafNode(BPTreeNode):
    """
    B+ Tree Leaf Node.

    Layout on page:
    [Header: 20 bytes]
    - is_leaf (1 byte)
    - size (4 bytes)
    - next_page_id (4 bytes)
    - prev_page_id (4 bytes)
    - parent_page_id (4 bytes)
    - padding (3 bytes)
    [Key array: size * 8 bytes (assuming int keys)]
    [RID array: size * 8 bytes]
    """

    HEADER_SIZE = 20

    def __init__(self, page: Page, max_size: int = BPTREE_LEAF_MAX_SIZE):
        super().__init__(page, True, max_size)
        self.keys: List[int] = []
        self.rids: List[RID] = []
        self.next_page_id = PageId(INVALID_PAGE_ID)
        self.prev_page_id = PageId(INVALID_PAGE_ID)

    def serialize(self) -> None:
        """Write node data to page."""
        # Write header
        header = struct.pack('<B I I I I xxx',
                           1,  # is_leaf
                           self.size,
                           self.next_page_id,
                           self.prev_page_id,
                           self.parent_page_id)

        offset = 0
        self.page.write_data(offset, header)
        offset += self.HEADER_SIZE

        # Write keys
        for key in self.keys:
            self.page.write_data(offset, struct.pack('<q', key))
            offset += 8

        # Write RIDs
        for rid in self.rids:
            self.page.write_data(offset, rid.to_bytes())
            offset += 8

    def deserialize(self) -> None:
        """Read node data from page."""
        # Read header
        header = self.page.read_data(0, self.HEADER_SIZE)
        is_leaf, size, next_page_id, prev_page_id, parent_page_id = struct.unpack('<B I I I I xxx', header)

        self.size = size
        self.next_page_id = PageId(next_page_id)
        self.prev_page_id = PageId(prev_page_id)
        self.parent_page_id = PageId(parent_page_id)

        offset = self.HEADER_SIZE

        # Read keys
        self.keys = []
        for _ in range(self.size):
            key_data = self.page.read_data(offset, 8)
            key = struct.unpack('<q', key_data)[0]
            self.keys.append(key)
            offset += 8

        # Read RIDs
        self.rids = []
        for _ in range(self.size):
            rid_data = self.page.read_data(offset, 8)
            rid = RID.from_bytes(rid_data)
            self.rids.append(rid)
            offset += 8

    def find_index(self, key: int) -> int:
        """Binary search to find index for key."""
        left, right = 0, self.size
        while left < right:
            mid = (left + right) // 2
            if self.keys[mid] < key:
                left = mid + 1
            else:
                right = mid
        return left

    def insert(self, key: int, rid: RID) -> bool:
        """Insert key-value pair. Returns False if full."""
        if self.is_full():
            return False

        idx = self.find_index(key)
        self.keys.insert(idx, key)
        self.rids.insert(idx, rid)
        self.size += 1
        self.serialize()
        return True

    def search(self, key: int) -> Optional[RID]:
        """Search for key, return RID if found."""
        idx = self.find_index(key)
        if idx < self.size and self.keys[idx] == key:
            return self.rids[idx]
        return None


class BPTreeInternalNode(BPTreeNode):
    """
    B+ Tree Internal Node.

    Layout:
    [Header: 16 bytes]
    - is_leaf (1 byte)
    - size (4 bytes)
    - parent_page_id (4 bytes)
    - padding (7 bytes)
    [Key array: (size-1) * 8 bytes]
    [Child pointer array: size * 4 bytes]

    Note: Internal node has n keys and n+1 children
    """

    HEADER_SIZE = 16

    def __init__(self, page: Page, max_size: int = BPTREE_INTERNAL_MAX_SIZE):
        super().__init__(page, False, max_size)
        self.keys: List[int] = []
        self.children: List[PageId] = []

    def serialize(self) -> None:
        """Write node data to page."""
        # Write header
        header = struct.pack('<B I I xxxxxxx',
                           0,  # is_leaf = False
                           self.size,
                           self.parent_page_id)

        offset = 0
        self.page.write_data(offset, header)
        offset += self.HEADER_SIZE

        # Write keys (size - 1 keys for size children)
        for i in range(self.size - 1):
            self.page.write_data(offset, struct.pack('<q', self.keys[i]))
            offset += 8

        # Write children
        for child_id in self.children:
            self.page.write_data(offset, struct.pack('<I', child_id))
            offset += 4

    def deserialize(self) -> None:
        """Read node data from page."""
        # Read header
        header = self.page.read_data(0, self.HEADER_SIZE)
        is_leaf, size, parent_page_id = struct.unpack('<B I I xxxxxxx', header)

        self.size = size
        self.parent_page_id = PageId(parent_page_id)

        offset = self.HEADER_SIZE

        # Read keys
        self.keys = []
        for _ in range(self.size - 1):
            key_data = self.page.read_data(offset, 8)
            key = struct.unpack('<q', key_data)[0]
            self.keys.append(key)
            offset += 8

        # Read children
        self.children = []
        for _ in range(self.size):
            child_data = self.page.read_data(offset, 4)
            child_id = struct.unpack('<I', child_data)[0]
            self.children.append(PageId(child_id))
            offset += 4

    def find_child(self, key: int) -> int:
        """Find which child to follow for given key."""
        # Binary search in keys
        idx = 0
        for i, k in enumerate(self.keys):
            if key >= k:
                idx = i + 1
        return idx

    def insert_child(self, key: int, child_page_id: PageId) -> bool:
        """Insert key and right child. Returns False if full."""
        if self.is_full():
            return False

        # Find insertion point
        idx = 0
        while idx < len(self.keys) and self.keys[idx] < key:
            idx += 1

        self.keys.insert(idx, key)
        self.children.insert(idx + 1, child_page_id)
        self.size += 1
        self.serialize()
        return True
