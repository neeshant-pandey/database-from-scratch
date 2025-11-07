# Week 4: B+ Tree Modifications & Hash Index

**Focus**: Implementing insert/delete operations and building a hash index

---

## 🎯 Learning Objectives

- [ ] Implement B+ tree insert with node splitting
- [ ] Implement B+ tree delete with merging/redistribution
- [ ] Handle root node special cases
- [ ] Understand hash indexes and their use cases
- [ ] Implement extendible hashing for dynamic growth

---

## 📚 Study & Research (5-6 hours)

### Core Concepts

**1. B+ Tree Insert with Splitting**
- [ ] Leaf overflow → split leaf into two
- [ ] Middle key gets promoted to parent
- [ ] Parent overflow → recursive split up the tree
- [ ] Root split → new root created (tree grows in height)
- [ ] Maintaining sibling pointers after split

**2. B+ Tree Delete with Merging**
- [ ] Leaf underflow → try to redistribute from sibling
- [ ] If can't redistribute → merge with sibling
- [ ] Update parent after merge
- [ ] Recursive merging up the tree
- [ ] Root with one child → child becomes new root (tree shrinks)

**3. Hash Indexes**
- [ ] Hash function properties (uniform distribution)
- [ ] Static hashing limitations
- [ ] Extendible hashing (directory + buckets)
- [ ] Linear hashing (dynamic growth without directory)
- [ ] When to use hash vs B+ tree indexes

### Required Reading

- [ ] Database Internals - Chapter 2 (B-Tree Operations)
- [ ] "Extendible Hashing" paper by Fagin et al.
- [ ] CMU 15-445 Lecture 7 (Hash Tables)
- [ ] PostgreSQL hash index documentation
- [ ] Study split/merge algorithms in detail
- [ ] Watch B+ tree insertion/deletion visualizations

### Discussion Questions

1. Why does insert split nodes but not always merge on delete?
2. What's the minimum fill factor for B+ tree nodes?
3. When would you choose hash index over B+ tree?
4. What are disadvantages of hash indexes?
5. How does extendible hashing avoid full rehashing?

---

## 💻 Implementation Tasks (16-20 hours)

### Task 1: Implement B+ Tree Insert

**What to Build:**
Complete insert operation with node splitting

**Requirements:**

**Insert Algorithm:**
- [ ] Find correct leaf node for key
- [ ] If leaf has space → insert key and value
- [ ] If leaf is full → split leaf:
  - Create new leaf node
  - Redistribute keys (half stay, half move)
  - Update sibling pointers
  - Promote middle key to parent
- [ ] If parent is full → recursively split parent
- [ ] If root splits → create new root (special case)

**Helper Methods:**
- `_split_leaf(leaf_node, key, value)` - split full leaf
- `_split_internal(internal_node, key, child)` - split full internal
- `_insert_into_parent(left, key, right)` - promote key to parent
- `_insert_into_leaf(leaf, key, value)` - add to leaf
- `_insert_into_internal(node, key, child)` - add to internal

**Edge Cases:**
- [ ] Insert into empty tree (create root)
- [ ] Insert duplicate key (decide policy: allow, replace, or error)
- [ ] Root split (increase tree height)
- [ ] Insert ascending/descending keys

**Deliverable:** Complete `insert(key, value)` in `src/index/bptree.py`

### Task 2: Implement B+ Tree Delete

**What to Build:**
Complete delete operation with merging/redistribution

**Requirements:**

**Delete Algorithm:**
- [ ] Find leaf containing key
- [ ] Remove key from leaf
- [ ] If leaf has enough keys → done
- [ ] If leaf underflows → try to redistribute from sibling
- [ ] If can't redistribute → merge with sibling
  - Remove separator key from parent
  - If parent underflows → recursively handle parent
- [ ] If root becomes empty → child becomes new root

**Helper Methods:**
- `_delete_from_leaf(leaf, key)` - remove key
- `_redistribute_leaf(left, right, parent)` - borrow from sibling
- `_merge_leaves(left, right, parent)` - combine siblings
- `_delete_from_internal(node, key)` - remove from internal
- `_handle_underflow(node, parent)` - fix underflow

**Edge Cases:**
- [ ] Delete from single-node tree
- [ ] Delete causing root to have one child
- [ ] Delete non-existent key
- [ ] Delete all keys

**Deliverable:** Complete `delete(key)` in `src/index/bptree.py`

### Task 3: Implement Hash Index

**What to Build:**
Hash index using extendible hashing

**Requirements:**

**Extendible Hashing Components:**
- [ ] Directory (array of bucket pointers)
- [ ] Buckets (pages storing key-value pairs)
- [ ] Global depth (directory size = 2^global_depth)
- [ ] Local depth per bucket
- [ ] Hash function (e.g., Python's hash() modulo 2^depth)

**Operations:**
- [ ] `insert(key, value)` - hash key, insert into bucket
  - If bucket full → split bucket and update directory
  - May need to double directory size
- [ ] `search(key)` - hash key, lookup in bucket
- [ ] `delete(key)` - hash key, remove from bucket
  - Optionally merge buckets if they become too empty

**Bucket Page Structure:**
- [ ] Array of (key, value) pairs
- [ ] Count of entries
- [ ] Local depth
- [ ] Overflow handling (chaining or just fail)

**Deliverable:** `src/index/hash_index.py`

### Task 4: Comprehensive Testing

**B+ Tree Insert Tests:**
- [ ] Insert into empty tree
- [ ] Insert in ascending order (worst case)
- [ ] Insert in random order
- [ ] Insert causing leaf split
- [ ] Insert causing internal split
- [ ] Insert causing root split
- [ ] Insert 10,000 keys, verify tree structure
- [ ] Insert duplicate keys (test your policy)

**B+ Tree Delete Tests:**
- [ ] Delete from leaf with enough keys
- [ ] Delete causing redistribution
- [ ] Delete causing merge
- [ ] Delete causing root removal
- [ ] Delete all keys from tree
- [ ] Insert 1000, delete 500, verify integrity

**Hash Index Tests:**
- [ ] Insert and search single key
- [ ] Insert causing bucket split
- [ ] Insert causing directory doubling
- [ ] Search non-existent key
- [ ] Delete key
- [ ] Insert 10,000 keys, search all
- [ ] Hash collision handling

**Integration Tests:**
- [ ] Build B+ tree with 100,000 keys
- [ ] Verify all searches work
- [ ] Perform range scan
- [ ] Delete 50,000 keys
- [ ] Verify tree is still balanced
- [ ] Compare B+ tree vs hash index performance

**Deliverable:** Comprehensive test suite

---

## 🧪 Experiments (4-5 hours)

### Experiment 1: B+ Tree Performance

**Goal:** Understand B+ tree scaling

- [ ] Measure insert time for 1K, 10K, 100K, 1M keys
- [ ] Sequential vs random inserts
- [ ] Measure search time at each scale
- [ ] Plot: n vs time (should be O(log n))
- [ ] Measure tree height at each scale
- [ ] Document findings

### Experiment 2: Hash vs B+ Tree

**Goal:** Compare index performance

**Workload:**
- [ ] Insert 100,000 keys
- [ ] 10,000 point queries (search by exact key)
- [ ] 1,000 range queries (only B+ tree supports)
- [ ] Measure time for each operation
- [ ] Compare disk I/O counts
- [ ] Document when each index type excels

### Experiment 3: Delete Performance

**Goal:** Understand delete complexity

- [ ] Insert 10,000 keys
- [ ] Delete in different patterns:
  - Sequential (1, 2, 3, ...)
  - Reverse (10000, 9999, ...)
  - Random
- [ ] Measure time and tree structure after each
- [ ] Check if tree remains balanced
- [ ] Document findings

### Experiment 4: Hash Directory Growth

**Goal:** Understand extendible hashing behavior

- [ ] Start with global depth = 2
- [ ] Insert keys and track directory doublings
- [ ] Measure: insertions between doublings
- [ ] Plot: inserts vs directory size
- [ ] Document growth pattern

---

## 📝 Deliverables

### Code
- [ ] Complete B+ tree with insert/delete
- [ ] Hash index implementation
- [ ] All tests passing (>85% coverage)
- [ ] Performance benchmarks

### Documentation
- [ ] Weekly notes with key learnings
- [ ] Insert/delete algorithm explanations
- [ ] Diagrams showing split/merge operations
- [ ] Hash index architecture diagram
- [ ] Experiment results with graphs
- [ ] Comparison: B+ tree vs hash index

### Demo
- [ ] Script that:
  - Creates B+ tree index
  - Inserts 10,000 keys
  - Performs searches and range scans
  - Deletes 5,000 keys
  - Visualizes final tree structure
  - Creates hash index
  - Compares performance

---

## ✅ Success Criteria

- [ ] B+ tree insert works correctly
- [ ] B+ tree delete works correctly
- [ ] Tree remains balanced after operations
- [ ] Can index 100,000+ keys
- [ ] Hash index works for point queries
- [ ] Understand trade-offs between index types
- [ ] All tests pass

---

## ⏭️ Next Week Preview

**Week 5:** SQL Parser & Query Representation
- Tokenizer/lexer for SQL
- Parser for SELECT/INSERT/UPDATE/DELETE
- Abstract syntax tree (AST)
- Query validation

**Prep:**
- [ ] Review parsing techniques (recursive descent)
- [ ] Study SQL grammar
- [ ] Read about AST design

**Estimated Time:** 26-30 hours
