"""
Disk Manager: handles all file I/O operations.
"""

import os
import struct
import threading
from typing import Optional, Dict
from ..common.types import PageId
from ..common.constants import PAGE_SIZE, MAGIC_NUMBER, DB_VERSION, INVALID_PAGE_ID
from .page import Page


class DiskManager:
    """
    Manages all disk I/O for the database.

    File Layout:
    - Page 0: Header page (metadata)
    - Page 1+: Data pages
    """

    def __init__(self, db_file: str):
        self.db_file = db_file
        self.file_handle: Optional[int] = None
        self.lock = threading.RLock()
        self.num_pages = 0
        self.free_pages = []  # List of freed page IDs

        # Statistics
        self.num_reads = 0
        self.num_writes = 0
        self.num_flushes = 0

        self._open_db_file()

    def _open_db_file(self) -> None:
        """Open or create database file."""
        is_new_db = not os.path.exists(self.db_file)

        # Open file in binary read/write mode
        self.file_handle = os.open(
            self.db_file,
            os.O_RDWR | os.O_CREAT,
            0o644
        )

        if is_new_db:
            self._write_header_page()
            self.num_pages = 1
        else:
            self._read_header_page()

    def _write_header_page(self) -> None:
        """Write database header to page 0."""
        header = struct.pack('<III',
                           MAGIC_NUMBER,
                           DB_VERSION,
                           self.num_pages)

        # Pad to page size
        header_page = header + b'\x00' * (PAGE_SIZE - len(header))

        with self.lock:
            os.lseek(self.file_handle, 0, os.SEEK_SET)
            os.write(self.file_handle, header_page)
            os.fsync(self.file_handle)

    def _read_header_page(self) -> None:
        """Read database header from page 0."""
        with self.lock:
            os.lseek(self.file_handle, 0, os.SEEK_SET)
            header_data = os.read(self.file_handle, PAGE_SIZE)

            magic, version, num_pages = struct.unpack('<III', header_data[:12])

            if magic != MAGIC_NUMBER:
                raise ValueError(f"Invalid database file: magic number mismatch")

            if version != DB_VERSION:
                raise ValueError(f"Unsupported database version: {version}")

            self.num_pages = num_pages

    def read_page(self, page_id: PageId) -> Page:
        """Read page from disk."""
        if page_id < 0 or page_id >= self.num_pages:
            raise ValueError(f"Invalid page_id: {page_id}")

        page = Page(page_id)

        with self.lock:
            offset = page_id * PAGE_SIZE
            os.lseek(self.file_handle, offset, os.SEEK_SET)
            raw_data = os.read(self.file_handle, PAGE_SIZE)

            if len(raw_data) != PAGE_SIZE:
                raise IOError(f"Failed to read complete page {page_id}")

            page.set_data(raw_data)
            self.num_reads += 1

        return page

    def write_page(self, page: Page) -> None:
        """Write page to disk."""
        if page.page_id < 0:
            raise ValueError(f"Invalid page_id: {page.page_id}")

        # Extend file if necessary
        if page.page_id >= self.num_pages:
            self.num_pages = page.page_id + 1
            self._write_header_page()

        with self.lock:
            offset = page.page_id * PAGE_SIZE
            os.lseek(self.file_handle, offset, os.SEEK_SET)
            os.write(self.file_handle, page.get_data())
            self.num_writes += 1

    def allocate_page(self) -> PageId:
        """Allocate a new page, returns page_id."""
        with self.lock:
            # Reuse freed page if available
            if self.free_pages:
                return PageId(self.free_pages.pop())

            # Otherwise allocate new page
            page_id = PageId(self.num_pages)
            self.num_pages += 1
            self._write_header_page()
            return page_id

    def deallocate_page(self, page_id: PageId) -> None:
        """Mark page as free for reuse."""
        if page_id < 0 or page_id >= self.num_pages:
            raise ValueError(f"Invalid page_id: {page_id}")

        with self.lock:
            self.free_pages.append(page_id)

    def flush(self) -> None:
        """Force all buffered writes to disk."""
        with self.lock:
            if self.file_handle is not None:
                os.fsync(self.file_handle)
                self.num_flushes += 1

    def close(self) -> None:
        """Close the database file."""
        with self.lock:
            if self.file_handle is not None:
                self._write_header_page()
                os.fsync(self.file_handle)
                os.close(self.file_handle)
                self.file_handle = None

    def get_stats(self) -> Dict[str, int]:
        """Return I/O statistics."""
        return {
            'num_pages': self.num_pages,
            'num_reads': self.num_reads,
            'num_writes': self.num_writes,
            'num_flushes': self.num_flushes,
            'free_pages': len(self.free_pages)
        }

    def __del__(self):
        """Cleanup on destruction."""
        if self.file_handle is not None:
            self.close()
