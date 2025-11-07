# Week 3: B+ Tree Implementation - Part 1

**Focus**: Understanding B+ trees and implementing search/scan operations

---

## 🎯 Learning Objectives

- [ ] Understand why B+ trees are used in databases
- [ ] Implement B+ tree node structures (leaf and internal)
- [ ] Implement search operation
- [ ] Implement sequential scan (range queries)
- [ ] Handle node splits conceptually (implement next week)

---

## 📚 Study & Research (6-7 hours)

### Core Concepts

**1. Why B+ Trees?**
- [ ] Compared to binary search trees
- [ ] Why balanced trees matter for disk access
- [ ] How B+ trees minimize disk I/O
- [ ] Difference between B-tree and B+ tree
- [ ] Time complexity: O(log_m N) where m is fanout

**2. B+ Tree Structure**
- [ ] Internal nodes: only keys + child pointers
- [ ] Leaf nodes: keys + data (or RIDs) + sibling pointers
- [ ] All leaves at same level
- [ ] Keys in leaf nodes are in sorted order
- [ ] Leaf nodes linked for sequential access

**3. B+ Tree Properties**
- [ ] Maximum keys per node (order/fanout)
- [ ] Minimum keys per node (for balance)
- [ ] Root exceptions (can have fewer keys)
- [ ] Invariant: leaves are linked for range scans

**4. Operations**
- [ ] **Search:** traverse from root to leaf
- [ ] **Range scan:** find start key, follow sibling pointers
- [ ] **Insert:** find leaf, add key, split if overflow (next week)
- [ ] **Delete:** find leaf, remove key, merge if underflow (next week)

### Required Reading

- [ ] Database Internals - Chapter 2 (B-Tree Basics)
- [ ] "The Ubiquitous B-Tree" (Douglas Comer paper)
- [ ] CMU 15-445 Lecture 6 & 7 (Tree Indexes)
- [ ] Visualize B+ trees: https://www.cs.usfca.edu/~galles/visualization/BPlusTree.html
- [ ] SQLite B-tree implementation overview
- [ ] Study PostgreSQL's btree implementation (nbtree)

### Discussion Questions

1. Why do B+ trees have better range query performance than B-trees?
2. What's the relationship between node size and disk page size?
3. How does fanout affect tree height?
4. Why store only keys (not data) in internal nodes?
5. What happens if you don't keep the tree balanced?

---

## 💻 Implementation Tasks (15-18 hours)

### Task 1: Design B+ Tree Node Structure

**What to Build:**
Classes for internal and leaf nodes

**Requirements:**

**Internal Node:**
- [ ] Array of keys (sorted)
- [ ] Array of child page pointers (n+1 children for n keys)
- [ ] Current number of keys
- [ ] Page type marker
- [ ] Methods: `find_child(key)`, `insert_key()`, `is_full()`

**Leaf Node:**
- [ ] Array of keys (sorted)
- [ ] Array of values/RIDs
- [ ] Pointer to next leaf (page_id)
- [ ] Pointer to previous leaf (page_id)
- [ ] Current number of keys
- [ ] Methods: `find_key(key)`, `insert_key()`, `delete_key()`, `is_full()`

**Key Design Decisions:**
- [ ] Choose max keys per node (e.g., based on 4KB page size)
- [ ] Key type (int for now, generic later)
- [ ] Value type (RID or actual data?)
- [ ] How to serialize nodes to pages

**Deliverable:** `src/index/bptree_node.py`

### Task 2: Implement B+ Tree Page Layout

**What to Build:**
Serialize/deserialize B+ tree nodes to/from pages

**Page Layout for Internal Node:**
```
[Header: node_type, num_keys, is_leaf, parent_page_id]
[Keys array]
[Child pointers array]
```

**Page Layout for Leaf Node:**
```
[Header: node_type, num_keys, is_leaf, next_page_id, prev_page_id]
[Keys array]
[Values/RIDs array]
```

**Requirements:**
- [ ] Pack node data into PAGE_SIZE bytes
- [ ] Use struct module for serialization
- [ ] Handle endianness
- [ ] Validate deserialization

**Deliverable:** Node serialization methods in `bptree_node.py`

### Task 3: Implement B+ Tree Index

**What to Build:**
B+ tree index structure with search and scan operations

**Requirements:**

**Initialization:**
- [ ] Create root page (initially a leaf)
- [ ] Track root page_id
- [ ] Configure max keys per node

**Search Operation:**
- [ ] Start at root
- [ ] Binary search to find next child (internal) or key (leaf)
- [ ] Traverse down to leaf
- [ ] Return value if found, None otherwise
- [ ] Use buffer pool manager to fetch pages

**Range Scan Operation:**
- [ ] Find start key using search
- [ ] Follow next pointers in leaf level
- [ ] Yield all keys in range [start, end]
- [ ] Stop when end key reached or no more leaves

**Helper Methods:**
- `_is_leaf(page)` - check if page is leaf
- `_find_leaf(key)` - traverse to leaf containing key
- `_binary_search_internal(node, key)` - find child index
- `_binary_search_leaf(node, key)` - find key index

**Deliverable:** `src/index/bptree.py` with search/scan only

### Task 4: Comprehensive Testing

**Node Tests:**
- [ ] Create internal and leaf nodes
- [ ] Serialize and deserialize nodes
- [ ] Binary search in internal nodes
- [ ] Binary search in leaf nodes
- [ ] Node capacity limits

**B+ Tree Tests:**
- [ ] Create empty tree
- [ ] Search in empty tree returns None
- [ ] Insert single key manually (no split logic yet)
- [ ] Search returns correct value
- [ ] Range scan returns correct keys in order
- [ ] Range scan with no matches
- [ ] Range scan across multiple leaves (manual setup)

**Note:** Full insert/delete testing comes next week

**Deliverable:** `tests/test_bptree.py`

### Task 5: Visualization Tool (Optional but Recommended)

**What to Build:**
Tool to print B+ tree structure

**Requirements:**
- [ ] Print tree level by level
- [ ] Show keys in each node
- [ ] Show leaf linkages
- [ ] ASCII art or simple text format

**Deliverable:** `src/index/bptree_viz.py`

---

## 🧪 Experiments (3-4 hours)

### Experiment 1: Node Capacity Analysis

**Goal:** Determine optimal node size

- [ ] Calculate how many keys fit in 4KB page
- [ ] For different key sizes (4, 8, 16 bytes)
- [ ] For different value sizes (8, 16 bytes)
- [ ] Account for header overhead
- [ ] Document findings

### Experiment 2: Tree Height Analysis

**Goal:** Understand scalability

- [ ] Calculate tree height for different fanouts
- [ ] For database sizes: 1K, 1M, 1B records
- [ ] Fanouts: 10, 50, 100, 200, 500
- [ ] Plot: records vs tree height vs fanout
- [ ] Understand I/O cost of search

### Experiment 3: Binary Search Performance

**Goal:** Compare search algorithms

- [ ] Implement linear search in node
- [ ] Implement binary search in node
- [ ] Benchmark on nodes with 10, 50, 100, 200 keys
- [ ] Measure time per search
- [ ] Document when binary search wins

---

## 📝 Deliverables

### Code
- [ ] B+ tree node classes
- [ ] Node serialization
- [ ] B+ tree with search/scan operations
- [ ] Tests for nodes and search
- [ ] Visualization tool

### Documentation
- [ ] Weekly notes
- [ ] B+ tree structure diagram
- [ ] Node layout diagrams
- [ ] Analysis of fanout vs tree height
- [ ] Design decisions document

### Demo
- [ ] Script that:
  - Creates B+ tree
  - Manually inserts keys into nodes
  - Demonstrates search operation
  - Demonstrates range scan
  - Visualizes tree structure

---

## ✅ Success Criteria

- [ ] Can search for keys in B+ tree
- [ ] Range scan works across leaves
- [ ] Nodes serialize/deserialize correctly
- [ ] Tree structure is sound
- [ ] Understand why splits are needed (implement next week)
- [ ] All tests pass

---

## ⏭️ Next Week Preview

**Week 4:** B+ Tree Insert/Delete & Hash Index
- Implement insert with node splitting
- Implement delete with merging/redistribution
- Handle root splitting
- Bonus: Hash index implementation

**Prep:**
- [ ] Study node splitting algorithms
- [ ] Understand merge vs redistribute
- [ ] Think through edge cases

**Estimated Time:** 24-28 hours
