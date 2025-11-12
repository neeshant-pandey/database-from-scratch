"""
Common type definitions for the database system.
"""

from typing import NewType, Tuple
from dataclasses import dataclass

# Basic type definitions
PageId = NewType('PageId', int)
LSN = NewType('LSN', int)  # Log Sequence Number
TxnId = NewType('TxnId', int)  # Transaction ID
SlotId = NewType('SlotId', int)


@dataclass(frozen=True)
class RID:
    """
    Record Identifier: uniquely identifies a tuple by (page_id, slot_id).
    Frozen (immutable) so it can be used as dict keys.
    """
    page_id: PageId
    slot_id: SlotId

    def __repr__(self) -> str:
        return f"RID(page={self.page_id}, slot={self.slot_id})"

    def to_bytes(self) -> bytes:
        """Serialize RID to bytes (8 bytes total: 4 for page_id, 4 for slot_id)."""
        import struct
        return struct.pack('<II', self.page_id, self.slot_id)

    @staticmethod
    def from_bytes(data: bytes) -> 'RID':
        """Deserialize RID from bytes."""
        import struct
        page_id, slot_id = struct.unpack('<II', data)
        return RID(PageId(page_id), SlotId(slot_id))


# Page type constants
class PageType:
    """Different types of pages in the database."""
    INVALID = 0
    HEADER = 1        # Database header page
    DATA = 2          # Table data page (slotted page)
    BPTREE_INTERNAL = 3  # B+ tree internal node
    BPTREE_LEAF = 4   # B+ tree leaf node
    HASH_BUCKET = 5   # Hash index bucket page
    FREE_LIST = 6     # Free page list
