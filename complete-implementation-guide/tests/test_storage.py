"""
Tests for storage layer components.
"""

import pytest
import os
import tempfile
from src.storage.page import Page
from src.storage.disk_manager import DiskManager
from src.storage.buffer_pool_manager import BufferPoolManager
from src.storage.slotted_page import SlottedPage
from src.common.types import PageId, SlotId
from src.common.constants import PageType


class TestPage:
    """Tests for Page class."""

    def test_page_initialization(self):
        page = Page(PageId(1), PageType.DATA)
        assert page.page_id == 1
        assert page.page_type == PageType.DATA
        assert not page.is_dirty
        assert page.pin_count == 0

    def test_page_serialization(self):
        page = Page(PageId(42), PageType.DATA)
        page.write_data(0, b"Hello, Database!")

        # Serialize
        raw_data = page.get_data()
        assert len(raw_data) == 4096  # PAGE_SIZE

        # Deserialize
        page2 = Page()
        page2.set_data(raw_data)

        assert page2.page_id == 42
        assert page2.page_type == PageType.DATA
        assert page2.read_data(0, 16) == b"Hello, Database!"

    def test_page_checksum(self):
        page = Page(PageId(1))
        page.write_data(0, b"Test data")

        # Get serialized data
        raw_data = page.get_data()

        # Should verify successfully
        page2 = Page()
        page2.set_data(raw_data)
        assert page2.verify_checksum()

        # Corrupt data should fail checksum
        corrupted = bytearray(raw_data)
        corrupted[100] = (corrupted[100] + 1) % 256
        page3 = Page()
        with pytest.raises(ValueError):
            page3.set_data(bytes(corrupted))

    def test_pin_unpin(self):
        page = Page(PageId(1))
        assert page.pin_count == 0
        assert not page.is_pinned()

        page.pin()
        assert page.pin_count == 1
        assert page.is_pinned()

        page.pin()
        assert page.pin_count == 2

        page.unpin()
        assert page.pin_count == 1
        assert page.is_pinned()

        page.unpin()
        assert page.pin_count == 0
        assert not page.is_pinned()


class TestDiskManager:
    """Tests for DiskManager."""

    def test_create_database(self):
        with tempfile.NamedTemporaryFile(delete=False) as tf:
            db_file = tf.name

        try:
            dm = DiskManager(db_file)
            assert dm.num_pages >= 1  # At least header page
            dm.close()
        finally:
            if os.path.exists(db_file):
                os.unlink(db_file)

    def test_allocate_page(self):
        with tempfile.NamedTemporaryFile(delete=False) as tf:
            db_file = tf.name

        try:
            dm = DiskManager(db_file)

            page_id = dm.allocate_page()
            assert page_id >= 1  # Page 0 is header

            page_id2 = dm.allocate_page()
            assert page_id2 > page_id

            dm.close()
        finally:
            if os.path.exists(db_file):
                os.unlink(db_file)

    def test_read_write_page(self):
        with tempfile.NamedTemporaryFile(delete=False) as tf:
            db_file = tf.name

        try:
            dm = DiskManager(db_file)

            # Allocate and write page
            page_id = dm.allocate_page()
            page = Page(page_id, PageType.DATA)
            page.write_data(0, b"Test data 123")

            dm.write_page(page)
            dm.flush()

            # Read page back
            page2 = dm.read_page(page_id)
            assert page2.page_id == page_id
            assert page2.read_data(0, 13) == b"Test data 123"

            dm.close()
        finally:
            if os.path.exists(db_file):
                os.unlink(db_file)


class TestBufferPoolManager:
    """Tests for Buffer Pool Manager."""

    def test_fetch_new_page(self):
        with tempfile.NamedTemporaryFile(delete=False) as tf:
            db_file = tf.name

        try:
            dm = DiskManager(db_file)
            bpm = BufferPoolManager(dm, pool_size=10)

            page = bpm.new_page()
            assert page is not None
            assert page.is_pinned()

            bpm.unpin_page(page.page_id, False)
            dm.close()
        finally:
            if os.path.exists(db_file):
                os.unlink(db_file)

    def test_buffer_pool_caching(self):
        with tempfile.NamedTemporaryFile(delete=False) as tf:
            db_file = tf.name

        try:
            dm = DiskManager(db_file)
            bpm = BufferPoolManager(dm, pool_size=10)

            # Create page
            page = bpm.new_page()
            page_id = page.page_id
            page.write_data(0, b"Cached data")
            bpm.unpin_page(page_id, True)

            # Fetch again - should be cached
            page2 = bpm.fetch_page(page_id)
            assert page2 is not None
            assert page2.read_data(0, 11) == b"Cached data"

            stats = bpm.get_stats()
            assert stats['num_hits'] > 0

            bpm.unpin_page(page_id, False)
            dm.close()
        finally:
            if os.path.exists(db_file):
                os.unlink(db_file)


class TestSlottedPage:
    """Tests for Slotted Page."""

    def test_insert_tuple(self):
        page = Page(PageId(1), PageType.DATA)
        slotted = SlottedPage(page)

        tuple_data = b"Hello, World!"
        slot_id = slotted.insert_tuple(tuple_data)

        assert slot_id is not None
        assert slotted.get_num_tuples() == 1

    def test_get_tuple(self):
        page = Page(PageId(1), PageType.DATA)
        slotted = SlottedPage(page)

        tuple_data = b"Test tuple"
        slot_id = slotted.insert_tuple(tuple_data)

        retrieved = slotted.get_tuple(slot_id)
        assert retrieved == tuple_data

    def test_delete_tuple(self):
        page = Page(PageId(1), PageType.DATA)
        slotted = SlottedPage(page)

        tuple_data = b"To be deleted"
        slot_id = slotted.insert_tuple(tuple_data)

        assert slotted.delete_tuple(slot_id)
        assert slotted.get_tuple(slot_id) is None

    def test_multiple_tuples(self):
        page = Page(PageId(1), PageType.DATA)
        slotted = SlottedPage(page)

        tuples = [b"Tuple 1", b"Tuple 2", b"Tuple 3"]
        slot_ids = []

        for t in tuples:
            slot_id = slotted.insert_tuple(t)
            assert slot_id is not None
            slot_ids.append(slot_id)

        assert slotted.get_num_tuples() == 3

        # Verify all tuples
        for i, slot_id in enumerate(slot_ids):
            assert slotted.get_tuple(slot_id) == tuples[i]
