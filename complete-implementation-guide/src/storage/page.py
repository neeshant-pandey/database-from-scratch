"""
Page class representing a fixed-size database page.
"""

import struct
import zlib
from typing import Optional
from ..common.types import PageId, LSN
from ..common.constants import PAGE_SIZE, INVALID_PAGE_ID, INVALID_LSN, PageType


class Page:
    """
    Represents a single database page (fixed size).

    Page Layout:
    [Header: 24 bytes]
    - page_id (4 bytes)
    - page_type (4 bytes)
    - lsn (8 bytes)
    - checksum (4 bytes)
    - pin_count (4 bytes) - not persisted
    [Data: PAGE_SIZE - 24 bytes]
    """

    HEADER_SIZE = 24

    def __init__(self, page_id: PageId = PageId(INVALID_PAGE_ID),
                 page_type: int = PageType.INVALID):
        self.page_id = page_id
        self.page_type = page_type
        self.lsn = LSN(INVALID_LSN)
        self.data = bytearray(PAGE_SIZE - self.HEADER_SIZE)
        self.is_dirty = False
        self.pin_count = 0
        self.checksum = 0

    def get_data(self) -> bytes:
        """Serialize page to bytes."""
        # Compute checksum over data
        self.checksum = zlib.crc32(bytes(self.data))

        # Pack header + data
        header = struct.pack('<IIqII',
                           self.page_id,
                           self.page_type,
                           self.lsn,
                           self.checksum,
                           0)  # pin_count not persisted

        return header + bytes(self.data)

    def set_data(self, raw_data: bytes) -> None:
        """Deserialize page from bytes."""
        if len(raw_data) != PAGE_SIZE:
            raise ValueError(f"Invalid page size: {len(raw_data)}, expected {PAGE_SIZE}")

        # Unpack header
        header = raw_data[:self.HEADER_SIZE]
        page_id, page_type, lsn, checksum, _ = struct.unpack('<IIqII', header)

        self.page_id = PageId(page_id)
        self.page_type = page_type
        self.lsn = LSN(lsn)
        self.checksum = checksum

        # Extract data
        self.data = bytearray(raw_data[self.HEADER_SIZE:])

        # Verify checksum
        if not self.verify_checksum():
            raise ValueError(f"Checksum mismatch for page {self.page_id}")

    def verify_checksum(self) -> bool:
        """Verify page data integrity."""
        computed = zlib.crc32(bytes(self.data))
        return computed == self.checksum

    def read_data(self, offset: int, length: int) -> bytes:
        """Read data from page at given offset."""
        if offset + length > len(self.data):
            raise ValueError("Read beyond page boundary")
        return bytes(self.data[offset:offset + length])

    def write_data(self, offset: int, data: bytes) -> None:
        """Write data to page at given offset."""
        if offset + len(data) > len(self.data):
            raise ValueError("Write beyond page boundary")
        self.data[offset:offset + len(data)] = data
        self.is_dirty = True

    def pin(self) -> None:
        """Increment pin count (page is in use)."""
        self.pin_count += 1

    def unpin(self) -> None:
        """Decrement pin count."""
        if self.pin_count > 0:
            self.pin_count -= 1

    def is_pinned(self) -> bool:
        """Check if page is pinned."""
        return self.pin_count > 0

    def reset(self) -> None:
        """Reset page to initial state."""
        self.page_id = PageId(INVALID_PAGE_ID)
        self.page_type = PageType.INVALID
        self.lsn = LSN(INVALID_LSN)
        self.data = bytearray(PAGE_SIZE - self.HEADER_SIZE)
        self.is_dirty = False
        self.pin_count = 0
        self.checksum = 0

    def __repr__(self) -> str:
        return (f"Page(id={self.page_id}, type={self.page_type}, "
                f"lsn={self.lsn}, dirty={self.is_dirty}, pins={self.pin_count})")
