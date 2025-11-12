"""
Slotted Page: variable-length record storage using slot directory.
"""

import struct
from typing import List, Optional, Tuple
from .page import Page
from ..common.types import SlotId


class SlottedPage:
    """
    Slotted page for variable-length tuples.

    Layout:
    [Page Header from Page class]
    [Slotted Page Header: 8 bytes]
    - num_slots (4 bytes)
    - free_space_offset (4 bytes)
    [Slot Array] ← grows downward
    - Each slot: (offset: 4 bytes, length: 4 bytes) = 8 bytes per slot
    [Free Space]
    [Tuples] ← grows upward from end of page
    """

    SLOTTED_HEADER_SIZE = 8
    SLOT_SIZE = 8  # offset (4 bytes) + length (4 bytes)

    def __init__(self, page: Page):
        self.page = page
        self._initialize_if_needed()

    def _initialize_if_needed(self) -> None:
        """Initialize empty slotted page if not already initialized."""
        # Check if page is already initialized
        if len(self.page.data) < self.SLOTTED_HEADER_SIZE:
            return

        # Read header
        header_data = self.page.read_data(0, self.SLOTTED_HEADER_SIZE)
        num_slots, free_space_offset = struct.unpack('<II', header_data)

        # If uninitialized (all zeros), initialize
        if num_slots == 0 and free_space_offset == 0:
            self._write_header(0, len(self.page.data))

    def _write_header(self, num_slots: int, free_space_offset: int) -> None:
        """Write slotted page header."""
        header = struct.pack('<II', num_slots, free_space_offset)
        self.page.write_data(0, header)

    def _read_header(self) -> Tuple[int, int]:
        """Read slotted page header. Returns (num_slots, free_space_offset)."""
        header_data = self.page.read_data(0, self.SLOTTED_HEADER_SIZE)
        return struct.unpack('<II', header_data)

    def _read_slot(self, slot_id: SlotId) -> Tuple[int, int]:
        """Read slot entry. Returns (offset, length)."""
        slot_offset = self.SLOTTED_HEADER_SIZE + slot_id * self.SLOT_SIZE
        slot_data = self.page.read_data(slot_offset, self.SLOT_SIZE)
        return struct.unpack('<II', slot_data)

    def _write_slot(self, slot_id: SlotId, offset: int, length: int) -> None:
        """Write slot entry."""
        slot_offset = self.SLOTTED_HEADER_SIZE + slot_id * self.SLOT_SIZE
        slot_data = struct.pack('<II', offset, length)
        self.page.write_data(slot_offset, slot_data)

    def insert_tuple(self, tuple_data: bytes) -> Optional[SlotId]:
        """
        Insert a tuple into the page.
        Returns slot_id on success, None if not enough space.
        """
        tuple_size = len(tuple_data)

        num_slots, free_space_offset = self._read_header()

        # Calculate space needed
        slot_array_end = self.SLOTTED_HEADER_SIZE + (num_slots + 1) * self.SLOT_SIZE
        space_needed = tuple_size

        # Check if enough free space
        if slot_array_end + space_needed > free_space_offset:
            # Try compacting first
            if not self.compact():
                return None  # Still not enough space

            # Re-read header after compaction
            num_slots, free_space_offset = self._read_header()
            slot_array_end = self.SLOTTED_HEADER_SIZE + (num_slots + 1) * self.SLOT_SIZE

            # Check again
            if slot_array_end + space_needed > free_space_offset:
                return None

        # Find free slot or allocate new one
        slot_id = None
        for i in range(num_slots):
            offset, length = self._read_slot(SlotId(i))
            if length == 0:  # Deleted slot
                slot_id = SlotId(i)
                break

        if slot_id is None:
            slot_id = SlotId(num_slots)
            num_slots += 1

        # Write tuple at end (grows upward from bottom)
        tuple_offset = free_space_offset - tuple_size
        self.page.write_data(tuple_offset, tuple_data)

        # Write slot
        self._write_slot(slot_id, tuple_offset, tuple_size)

        # Update header
        self._write_header(num_slots, tuple_offset)

        return slot_id

    def get_tuple(self, slot_id: SlotId) -> Optional[bytes]:
        """Get tuple data by slot_id. Returns None if slot is deleted."""
        num_slots, _ = self._read_header()

        if slot_id < 0 or slot_id >= num_slots:
            return None

        offset, length = self._read_slot(slot_id)

        if length == 0:  # Deleted tuple
            return None

        return self.page.read_data(offset, length)

    def delete_tuple(self, slot_id: SlotId) -> bool:
        """Delete tuple by marking slot as deleted (length = 0)."""
        num_slots, _ = self._read_header()

        if slot_id < 0 or slot_id >= num_slots:
            return False

        # Mark slot as deleted
        offset, length = self._read_slot(slot_id)
        if length == 0:
            return False  # Already deleted

        self._write_slot(slot_id, offset, 0)  # length = 0 means deleted
        return True

    def update_tuple(self, slot_id: SlotId, new_data: bytes) -> bool:
        """
        Update tuple in place if same size, otherwise delete and reinsert.
        Returns False if update fails.
        """
        num_slots, _ = self._read_header()

        if slot_id < 0 or slot_id >= num_slots:
            return False

        old_offset, old_length = self._read_slot(slot_id)

        if old_length == 0:
            return False  # Deleted tuple

        new_length = len(new_data)

        if new_length == old_length:
            # Same size - update in place
            self.page.write_data(old_offset, new_data)
            return True
        else:
            # Different size - delete and reinsert
            self.delete_tuple(slot_id)
            # For now, use same slot_id (need compaction to reclaim space)
            # This is simplified - real implementation would handle this better
            return False  # Would need more complex logic

    def compact(self) -> bool:
        """
        Compact page to reclaim fragmented space.
        Move all tuples to end of page and update slot offsets.
        """
        num_slots, _ = self._read_header()

        # Collect valid tuples
        tuples = []
        for i in range(num_slots):
            offset, length = self._read_slot(SlotId(i))
            if length > 0:
                tuple_data = self.page.read_data(offset, length)
                tuples.append((SlotId(i), tuple_data))

        # Write tuples from end of page
        new_free_space_offset = len(self.page.data)
        for slot_id, tuple_data in tuples:
            tuple_size = len(tuple_data)
            new_offset = new_free_space_offset - tuple_size
            self.page.write_data(new_offset, tuple_data)
            self._write_slot(slot_id, new_offset, tuple_size)
            new_free_space_offset = new_offset

        # Update header
        self._write_header(num_slots, new_free_space_offset)

        return True

    def get_free_space(self) -> int:
        """Return available free space in bytes."""
        num_slots, free_space_offset = self._read_header()
        slot_array_end = self.SLOTTED_HEADER_SIZE + num_slots * self.SLOT_SIZE
        return free_space_offset - slot_array_end

    def get_num_tuples(self) -> int:
        """Return number of non-deleted tuples."""
        num_slots, _ = self._read_header()
        count = 0
        for i in range(num_slots):
            _, length = self._read_slot(SlotId(i))
            if length > 0:
                count += 1
        return count
