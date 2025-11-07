# Week 1: Database Fundamentals & Storage Layer

**Focus**: Understanding database architecture, Python setup, and building the disk manager

---

## 🎯 Learning Objectives

By end of week, you should understand:
- [ ] How databases are structured (layers and components)
- [ ] Why databases use page-based storage
- [ ] File I/O operations and durability guarantees
- [ ] Page structure and serialization
- [ ] How to manage free space in database files

---

## 📚 Study & Research (6-8 hours)

### Core Concepts to Learn

**1. Database Architecture**
- [ ] Study the layered architecture of databases
- [ ] Understand role of: storage manager, buffer pool, query executor, transaction manager
- [ ] Draw a complete architecture diagram
- [ ] Compare architectures of SQLite, PostgreSQL, MySQL

**2. Page-Based Storage**
- [ ] Why pages instead of individual records?
- [ ] Typical page sizes and trade-offs (4KB vs 8KB vs 16KB)
- [ ] Page header components (page_id, LSN, free space, etc.)
- [ ] Page types (header, data, index, free list)

**3. File Organization**
- [ ] Database file structure (header page, data pages)
- [ ] Free space management strategies (bitmap, linked list)
- [ ] File growth strategies (pre-allocation vs on-demand)

**4. Durability & Consistency**
- [ ] What is fsync() and why is it critical?
- [ ] Difference between flush() and fsync()
- [ ] Checksums for data integrity (CRC32, etc.)

### Required Reading

- [ ] Database Internals (Alex Petrov) - Chapters 1, 3
- [ ] SQLite Architecture: https://www.sqlite.org/arch.html
- [ ] SQLite File Format: https://www.sqlite.org/fileformat.html
- [ ] CMU 15-445 Lectures 3 & 4 (Storage)
- [ ] Python struct module documentation
- [ ] Research: "What Every Programmer Should Know About Memory"

### Discussion Questions (Answer in your notes)

1. Why do databases use fixed-size pages?
2. What are trade-offs between large and small page sizes?
3. How does a database ensure data survives a crash?
4. What happens if you don't call fsync()?
5. Why use checksums on every page?

---

## 💻 Implementation Tasks (12-15 hours)

### Setup Tasks

- [ ] Set up Python virtual environment (venv)
- [ ] Install dependencies: pytest, black, mypy, pylint
- [ ] Create project structure (src/, tests/, docs/)
- [ ] Configure pytest with coverage reporting
- [ ] Set up git with proper .gitignore
- [ ] Create requirements.txt

### Task 1: Define Core Types & Constants

**What to Build:**
- [ ] Create type definitions (PageId, LSN, TxnId, etc.)
- [ ] Define constants (PAGE_SIZE, MAGIC_NUMBER, PAGE_TYPES)
- [ ] Create configuration dataclass for database settings
- [ ] Add type hints throughout

**Deliverable:** `src/common/types.py` and `src/common/constants.py`

### Task 2: Implement Page Class

**What to Build:**
A Page class that represents a single database page

**Requirements:**
- [ ] Fixed size of PAGE_SIZE (4096 bytes)
- [ ] Store page header fields (page_id, page_type, LSN, etc.)
- [ ] Serialize/deserialize page to/from bytes
- [ ] Implement checksum calculation and verification
- [ ] Track dirty flag and pin count (for buffer pool later)
- [ ] Methods to read/write data at offsets

**Key Methods to Implement:**
- `__init__()` - initialize empty page
- `get_data()` - serialize page to bytes
- `set_data(bytes)` - deserialize from bytes
- `compute_checksum()` - calculate CRC32
- `verify_checksum()` - check integrity
- `write_data(offset, data)` - write at position
- `read_data(offset, length)` - read from position
- `pin()` / `unpin()` - reference counting

**Deliverable:** `src/storage/page.py` with full test coverage

### Task 3: Implement Disk Manager

**What to Build:**
A DiskManager class that handles all file I/O

**Requirements:**
- [ ] Create or open database file
- [ ] Write file header with magic number and version
- [ ] Allocate new pages (grow file)
- [ ] Read page by page_id
- [ ] Write page by page_id
- [ ] Track free pages for reuse
- [ ] Thread-safe operations (use locks)
- [ ] Flush data to disk with fsync()
- [ ] Track I/O statistics

**Key Methods to Implement:**
- `__init__(filename)` - open/create database
- `read_page(page_id)` - read page from disk
- `write_page(page)` - write page to disk
- `allocate_page()` - get new page_id
- `deallocate_page(page_id)` - mark page as free
- `flush()` - force write to disk
- `close()` - cleanup and close file
- `get_stats()` - return I/O metrics

**Deliverable:** `src/storage/disk_manager.py` with full test coverage

### Task 4: Write Comprehensive Tests

**Test Coverage Required:**

**Page Tests:**
- [ ] Page initialization
- [ ] Serialization/deserialization (roundtrip)
- [ ] Checksum computation and verification
- [ ] Checksum detects corruption
- [ ] Pin/unpin operations
- [ ] Dirty flag management
- [ ] Data read/write operations
- [ ] Boundary conditions (write beyond page size)

**DiskManager Tests:**
- [ ] Create new database file
- [ ] Open existing database
- [ ] Allocate pages (IDs are unique)
- [ ] Deallocate and reuse pages
- [ ] Write and read pages
- [ ] Multiple pages persist across close/open
- [ ] Invalid page_id raises error
- [ ] Thread-safety (concurrent access)
- [ ] Statistics tracking

**Deliverable:** `tests/test_page.py` and `tests/test_disk_manager.py` with >80% coverage

---

## 🧪 Experiments (3-4 hours)

### Experiment 1: File I/O Benchmarks

**Goal:** Understand performance characteristics

- [ ] Write script to benchmark sequential writes (1000 pages)
- [ ] Benchmark random writes
- [ ] Compare with/without fsync()
- [ ] Test different page sizes (4KB, 8KB, 16KB)
- [ ] Measure throughput (MB/s)
- [ ] Document results with graphs

### Experiment 2: Study SQLite Files

**Goal:** Learn from real database implementation

- [ ] Create SQLite database with sample data
- [ ] Read file header using Python
- [ ] Use hex editor to examine raw bytes
- [ ] Identify page boundaries
- [ ] Understand SQLite's page format
- [ ] Document findings with screenshots

### Experiment 3: Checksum Algorithms

**Goal:** Choose the right checksum

- [ ] Implement CRC32, xxHash, MD5
- [ ] Benchmark each on 4KB pages
- [ ] Compare speed vs collision resistance
- [ ] Document which is best for databases

---

## 📝 Deliverables

### Code Deliverables
- [ ] Complete Python project structure
- [ ] All source files with type hints
- [ ] All tests passing
- [ ] Code coverage ≥ 80%
- [ ] Passes black, mypy, pylint

### Documentation Deliverables
- [ ] `docs/week-01-notes.md` - your learning notes
- [ ] Architecture diagram
- [ ] Design decisions document
- [ ] Benchmark results
- [ ] Answers to discussion questions
- [ ] Weekly report

### Demo Deliverable
- [ ] Create demo script that:
  - Creates a database
  - Allocates 10 pages
  - Writes data to each page
  - Closes and reopens database
  - Reads and verifies all pages
  - Prints statistics

---

## ✅ Success Criteria

Before Week 2:
- [ ] Can explain database architecture to someone
- [ ] All tests pass
- [ ] Database file persists data across restarts
- [ ] Checksums detect corrupted pages
- [ ] Code is clean and documented
- [ ] Completed all reading
- [ ] Written weekly report

---

## ⏭️ Next Week Preview

**Week 2:** Buffer Pool Manager & Slotted Pages
- In-memory caching of pages
- LRU replacement policy
- Variable-length record storage
- Slot directory for tuples

**Prep:**
- [ ] Study LRU cache implementations
- [ ] Review Python threading concepts
- [ ] Read about variable-length records

---

**Estimated Time:** 20-25 hours total
- Reading: 6-8 hours
- Coding: 12-15 hours
- Testing & Experiments: 3-4 hours
- Documentation: 2-3 hours
