# Week 2: Buffer Pool Manager & Slotted Pages

**Focus**: In-memory page caching and variable-length record storage

---

## 🎯 Learning Objectives

- [ ] Understand why databases need a buffer pool
- [ ] Implement LRU page replacement policy
- [ ] Handle concurrent access to pages
- [ ] Design slotted page structure for variable records
- [ ] Implement tuple insertion/deletion with slot directory

---

## 📚 Study & Research (5-6 hours)

### Core Concepts

**1. Buffer Pool**
- [ ] Why cache pages in memory?
- [ ] Pin/unpin semantics and reference counting
- [ ] Page replacement policies (LRU, Clock, LRU-K)
- [ ] Dirty page management and write-back
- [ ] How PostgreSQL and MySQL implement buffer pools

**2. Slotted Pages**
- [ ] Why variable-length records need special handling
- [ ] Slot directory structure
- [ ] Growing from both ends (slots from top, data from bottom)
- [ ] Page compaction/defragmentation
- [ ] Record IDs (RIDs): (page_id, slot_number)

**3. Concurrency Basics**
- [ ] Thread safety with locks
- [ ] When to lock pages vs buffer frames
- [ ] Reader-writer locks
- [ ] Deadlock prevention strategies

### Required Reading

- [ ] Database Internals - Chapter 4 (B-Trees intro, page formats)
- [ ] "The Design and Implementation of Modern Column-Oriented Database Systems" - Section on storage
- [ ] CMU 15-445 Lecture 5 (Buffer Pools)
- [ ] Research paper: "LRU-K page replacement algorithm"
- [ ] PostgreSQL documentation on buffer manager
- [ ] Python threading documentation

### Discussion Questions

1. What happens if buffer pool is too small?
2. Why is LRU better than FIFO for databases?
3. How do you prevent flushing a page that's being read?
4. Why does slotted page grow from both ends?
5. What is page fragmentation and how do you fix it?

---

## 💻 Implementation Tasks (14-16 hours)

### Task 1: Implement Buffer Pool Manager

**What to Build:**
An in-memory cache that manages pages and implements LRU replacement

**Requirements:**
- [ ] Fixed-size pool of page frames
- [ ] Hash table: page_id → frame_id lookup
- [ ] LRU replacement policy (doubly-linked list + hashmap OR use OrderedDict)
- [ ] Pin/unpin operations with reference counting
- [ ] Fetch page (from disk if not in pool)
- [ ] Flush page (write dirty pages to disk)
- [ ] Thread-safe with locks
- [ ] Evict unpinned pages when pool is full
- [ ] Track buffer pool statistics (hit rate, evictions, etc.)

**Key Methods:**
- `fetch_page(page_id)` - get page, load from disk if needed
- `unpin_page(page_id, is_dirty)` - release page
- `flush_page(page_id)` - force write to disk
- `flush_all_pages()` - write all dirty pages
- `new_page()` - allocate and pin new page
- `delete_page(page_id)` - remove page

**Deliverable:** `src/storage/buffer_pool_manager.py`

### Task 2: Implement Slotted Page

**What to Build:**
A page structure that stores variable-length tuples using a slot directory

**Page Layout:**
```
[Page Header]
[Slot Array] ← grows downward
   ...
[Free Space]
   ...
[Tuples] ← grows upward
```

**Requirements:**
- [ ] Slot array stores (offset, length) for each tuple
- [ ] Insert tuple and return slot number
- [ ] Delete tuple by slot number (mark as deleted)
- [ ] Update tuple (may require moving it)
- [ ] Get tuple by slot number
- [ ] Page compaction when fragmented
- [ ] Track free space correctly

**Key Methods:**
- `insert_tuple(data)` - insert and return slot_id
- `delete_tuple(slot_id)` - mark slot as deleted
- `get_tuple(slot_id)` - retrieve tuple data
- `update_tuple(slot_id, new_data)` - update in place or relocate
- `compact()` - defragment page
- `get_free_space()` - available space for new tuple

**Deliverable:** `src/storage/slotted_page.py`

### Task 3: Implement Record ID (RID)

**What to Build:**
A tuple identifier: (page_id, slot_id)

**Requirements:**
- [ ] Immutable tuple class or dataclass
- [ ] Can be used as dictionary key
- [ ] Serializable to bytes
- [ ] Human-readable string representation

**Deliverable:** `src/common/types.py` (add RID class)

### Task 4: Integrate Everything

**What to Build:**
High-level table heap using buffer pool + slotted pages

**Requirements:**
- [ ] Insert tuple (allocate page if needed)
- [ ] Delete tuple by RID
- [ ] Get tuple by RID
- [ ] Update tuple by RID
- [ ] Scan all tuples (iterator)
- [ ] Handle page full scenario (allocate new page)

**Deliverable:** `src/storage/table_heap.py`

### Task 5: Comprehensive Testing

**Buffer Pool Tests:**
- [ ] Page caching (second fetch hits cache)
- [ ] LRU eviction (least recently used evicted first)
- [ ] Pin prevents eviction
- [ ] Dirty pages written on eviction
- [ ] New page allocation
- [ ] Flush operations
- [ ] Concurrent access (multiple threads)
- [ ] Buffer pool full scenario

**Slotted Page Tests:**
- [ ] Insert single tuple
- [ ] Insert until full
- [ ] Delete tuple creates free space
- [ ] Insert after delete reuses space
- [ ] Update tuple (smaller, same size, larger)
- [ ] Page compaction works
- [ ] Get non-existent slot fails gracefully
- [ ] Variable-length tuples

**Integration Tests:**
- [ ] Insert 10,000 tuples across multiple pages
- [ ] Delete random tuples
- [ ] Scan all remaining tuples
- [ ] Close and reopen, verify persistence
- [ ] Update tuples and verify

**Deliverable:** Full test suite with >85% coverage

---

## 🧪 Experiments (3-4 hours)

### Experiment 1: Buffer Pool Size Impact

**Goal:** Understand cache performance

- [ ] Create workload: insert 1000 pages, then random reads
- [ ] Test with buffer pool sizes: 10, 50, 100, 500 pages
- [ ] Measure: hit rate, total time, disk I/O count
- [ ] Plot: buffer size vs hit rate
- [ ] Document findings

### Experiment 2: Page Replacement Policies

**Goal:** Compare LRU vs FIFO vs Clock

- [ ] Implement FIFO replacement
- [ ] Implement Clock algorithm (optional)
- [ ] Run same workload on each
- [ ] Compare hit rates
- [ ] Document which is best

### Experiment 3: Slotted Page Fragmentation

**Goal:** Understand fragmentation impact

- [ ] Insert 100 tuples
- [ ] Delete every other tuple
- [ ] Measure fragmentation (wasted space)
- [ ] Run compaction
- [ ] Measure space reclaimed
- [ ] Document findings

---

## 📝 Deliverables

### Code
- [ ] Buffer pool manager
- [ ] Slotted page implementation
- [ ] Table heap
- [ ] All tests passing (>85% coverage)
- [ ] Type hints and documentation

### Documentation
- [ ] Weekly notes with key learnings
- [ ] Buffer pool architecture diagram
- [ ] Slotted page layout diagram
- [ ] Experiment results with graphs
- [ ] Design decisions document

### Demo
- [ ] Script that:
  - Inserts 1000 tuples
  - Deletes 200 tuples
  - Updates 100 tuples
  - Scans all remaining tuples
  - Shows buffer pool statistics
  - Demonstrates persistence

---

## ✅ Success Criteria

- [ ] Buffer pool caches pages correctly
- [ ] LRU eviction works
- [ ] Can store thousands of variable-length tuples
- [ ] Slotted pages handle fragmentation
- [ ] All data persists across restarts
- [ ] Thread-safe operations
- [ ] Good test coverage

---

## ⏭️ Next Week Preview

**Week 3:** B+ Tree Implementation Part 1
- B+ tree structure and properties
- Leaf and internal nodes
- Search operation
- Sequential scan

**Estimated Time:** 22-26 hours
