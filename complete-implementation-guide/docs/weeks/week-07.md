# Week 7: Transaction Management & Concurrency Control

**Focus**: Implementing ACID properties and concurrency control mechanisms

---

## 🎯 Learning Objectives

- [ ] Understand ACID properties and their implementation
- [ ] Implement transaction manager
- [ ] Implement 2-phase locking (2PL) protocol
- [ ] Handle deadlock detection and prevention
- [ ] Support different isolation levels
- [ ] Implement lock manager
- [ ] (Bonus) Understand MVCC basics

---

## 📚 Study & Research (7-8 hours)

### Core Concepts

**1. ACID Properties**
- [ ] **Atomicity**: All-or-nothing execution
- [ ] **Consistency**: Database constraints maintained
- [ ] **Isolation**: Concurrent transactions don't interfere
- [ ] **Durability**: Committed changes survive crashes

**2. Concurrency Problems**
- [ ] Dirty reads (reading uncommitted data)
- [ ] Non-repeatable reads (data changes between reads)
- [ ] Phantom reads (new rows appear in range)
- [ ] Lost updates (concurrent writes overwrite each other)
- [ ] Write-write conflicts

**3. Locking Protocols**
- [ ] Shared locks (S) for reads
- [ ] Exclusive locks (X) for writes
- [ ] Lock compatibility matrix
- [ ] 2-Phase Locking (2PL): growing and shrinking phases
- [ ] Strict 2PL (hold locks until commit/abort)
- [ ] Lock granularity (tuple, page, table)

**4. Deadlock**
- [ ] Deadlock definition (circular wait)
- [ ] Detection (wait-for graph cycle detection)
- [ ] Prevention (wait-die, wound-wait)
- [ ] Resolution (abort victim transaction)

**5. Isolation Levels**
- [ ] Read Uncommitted
- [ ] Read Committed
- [ ] Repeatable Read
- [ ] Serializable
- [ ] How locks implement each level

**6. Transaction Log**
- [ ] Write-Ahead Logging (WAL) principles
- [ ] Log records (BEGIN, COMMIT, ABORT, UPDATE)
- [ ] LSN (Log Sequence Number)
- [ ] Connection to recovery (next week)

### Required Reading

- [ ] Database Internals - Chapter 5 (Transaction Processing)
- [ ] CMU 15-445 Lectures 15-17 (Concurrency Control, Two-Phase Locking, Timestamp Ordering)
- [ ] "Transaction Processing" by Jim Gray (Chapter on locking)
- [ ] SQL standard isolation levels (ANSI SQL-92)
- [ ] PostgreSQL locking documentation
- [ ] "A Critique of ANSI SQL Isolation Levels" paper

### Discussion Questions

1. Why do we need locks? What if we just run queries sequentially?
2. Why does 2PL guarantee serializability?
3. How does deadlock occur? Give a concrete example.
4. Which is better: deadlock detection or prevention?
5. What's the trade-off between isolation level and performance?

---

## 💻 Implementation Tasks (22-26 hours)

### Task 1: Implement Transaction Context

**What to Build:**
Transaction object that tracks transaction state

**Requirements:**
- [ ] Transaction ID (unique)
- [ ] Transaction state: RUNNING, COMMITTED, ABORTED
- [ ] Start timestamp
- [ ] Isolation level
- [ ] Set of acquired locks
- [ ] Undo log (for rollback)

**Transaction Manager:**
- [ ] Begin transaction (allocate txn_id)
- [ ] Commit transaction (release locks, write log)
- [ ] Abort transaction (rollback changes, release locks)
- [ ] Get transaction by ID
- [ ] Track active transactions

**Deliverable:** `src/transaction/transaction.py` and `src/transaction/transaction_manager.py`

### Task 2: Implement Lock Manager

**What to Build:**
Centralized lock manager for all transactions

**Requirements:**

**Lock Types:**
- [ ] Shared lock (S) - for reads
- [ ] Exclusive lock (X) - for writes

**Lock Manager Methods:**
- [ ] `lock_shared(txn_id, rid)` - acquire S lock
- [ ] `lock_exclusive(txn_id, rid)` - acquire X lock
- [ ] `unlock(txn_id, rid)` - release lock
- [ ] `upgrade_lock(txn_id, rid)` - S → X upgrade
- [ ] Check lock compatibility
- [ ] Wait queue for blocked transactions
- [ ] Deadlock detection

**Lock Table Structure:**
- [ ] Map: RID → list of (txn_id, lock_mode)
- [ ] Track which transactions hold which locks
- [ ] Track which transactions are waiting

**Deliverable:** `src/transaction/lock_manager.py`

### Task 3: Implement Deadlock Detection

**What to Build:**
Detect deadlock cycles using wait-for graph

**Requirements:**
- [ ] Build wait-for graph (transaction → transaction edges)
- [ ] Detect cycles using DFS
- [ ] Choose victim transaction (youngest, lowest priority, etc.)
- [ ] Abort victim and release locks
- [ ] Run detection periodically (background thread) or on lock request

**Deliverable:** `src/transaction/deadlock_detector.py`

### Task 4: Integrate Transactions with Executors

**What to Build:**
Add transaction support to query execution

**Requirements:**

**Modify Executors:**
- [ ] All operators take transaction context
- [ ] Acquire S locks on reads (seq scan, index scan)
- [ ] Acquire X locks on writes (insert, update, delete)
- [ ] Lock wait if lock unavailable
- [ ] Release locks on commit/abort

**Modify Buffer Pool:**
- [ ] Track which transaction modified each page
- [ ] Prevent reading uncommitted changes (dirty pages)

**Transaction API for Users:**
```python
txn = transaction_manager.begin()
try:
    executor.execute("INSERT INTO users VALUES (...)", txn)
    executor.execute("UPDATE accounts SET balance = balance - 100", txn)
    transaction_manager.commit(txn)
except:
    transaction_manager.abort(txn)
```

**Deliverable:** Updated executors and transaction integration

### Task 5: Implement Isolation Levels

**What to Build:**
Support different SQL isolation levels

**Requirements:**

**Read Uncommitted:**
- [ ] No S locks acquired (dirty reads allowed)
- [ ] X locks still acquired for writes

**Read Committed:**
- [ ] Acquire S locks but release immediately after read
- [ ] Hold X locks until commit

**Repeatable Read:**
- [ ] Hold S locks until commit
- [ ] Hold X locks until commit
- [ ] Prevents dirty and non-repeatable reads

**Serializable:**
- [ ] Strict 2PL (hold all locks until commit)
- [ ] Additional predicate locks or range locks for phantoms

**Deliverable:** Isolation level support in lock manager and executors

### Task 6: Implement Basic Write-Ahead Log

**What to Build:**
Simple transaction log for durability (full recovery next week)

**Requirements:**
- [ ] Log file on disk
- [ ] Log record types: BEGIN, COMMIT, ABORT, UPDATE
- [ ] Each UPDATE log: txn_id, RID, old_value, new_value
- [ ] Assign LSN to each log record
- [ ] Flush log before committing transaction
- [ ] (Recovery implementation next week)

**Log Record Structure:**
```python
class LogRecord:
    lsn: LSN
    txn_id: TxnId
    type: LogType  # BEGIN, COMMIT, ABORT, UPDATE
    rid: RID  # for UPDATE
    old_value: bytes  # for UPDATE
    new_value: bytes  # for UPDATE
```

**Deliverable:** `src/recovery/log_manager.py`

### Task 7: Comprehensive Testing

**Transaction Tests:**
- [ ] Begin, commit, abort transactions
- [ ] Transaction ID allocation
- [ ] Transaction state tracking

**Lock Manager Tests:**
- [ ] Acquire S lock
- [ ] Acquire X lock
- [ ] Lock compatibility (S-S compatible, S-X incompatible, X-X incompatible)
- [ ] Lock wait queue
- [ ] Lock upgrade (S → X)
- [ ] Release locks

**Deadlock Tests:**
- [ ] Create deadlock scenario (T1 waits for T2, T2 waits for T1)
- [ ] Detect deadlock
- [ ] Abort victim transaction
- [ ] Verify other transaction proceeds

**Concurrency Tests:**
- [ ] Two transactions read same tuple (both succeed)
- [ ] Two transactions write same tuple (one waits)
- [ ] Transaction reads tuple written by uncommitted transaction (waits or dirty read depending on isolation level)
- [ ] Lost update prevented
- [ ] Dirty read test (Read Uncommitted allows, others prevent)

**Isolation Level Tests:**
- [ ] Test each isolation level with appropriate anomalies
- [ ] Verify Read Uncommitted allows dirty reads
- [ ] Verify Read Committed prevents dirty reads
- [ ] Verify Repeatable Read prevents non-repeatable reads
- [ ] Verify Serializable prevents phantoms

**Integration Tests:**
- [ ] Bank transfer example (withdraw from A, deposit to B)
- [ ] Concurrent inserts
- [ ] Concurrent updates
- [ ] Abort transaction and verify rollback
- [ ] Stress test: 100 concurrent transactions

**Deliverable:** Comprehensive test suite including concurrency tests

---

## 🧪 Experiments (4-5 hours)

### Experiment 1: Lock Granularity Impact

**Goal:** Understand tuple vs page vs table locking

- [ ] Implement tuple-level locking
- [ ] Implement page-level locking
- [ ] Run concurrent workload
- [ ] Measure throughput and lock contention
- [ ] Document trade-offs

### Experiment 2: Isolation Level Performance

**Goal:** Measure isolation overhead

- [ ] Run workload with each isolation level
- [ ] Measure: throughput, latency, abort rate
- [ ] Plot: isolation level vs performance
- [ ] Document when to use each level

### Experiment 3: Deadlock Frequency

**Goal:** Understand deadlock conditions

- [ ] Generate workload with varying contention
- [ ] Measure deadlock frequency
- [ ] Test detection vs prevention strategies
- [ ] Document findings

### Experiment 4: Transaction Throughput

**Goal:** Measure transaction processing capacity

- [ ] Simple transaction: read-modify-write
- [ ] Run with 1, 10, 50, 100 concurrent transactions
- [ ] Measure: transactions/sec, average latency
- [ ] Identify bottlenecks (locking, disk I/O, etc.)
- [ ] Plot results

---

## 📝 Deliverables

### Code
- [ ] Transaction manager
- [ ] Lock manager
- [ ] Deadlock detector
- [ ] Transaction integration in executors
- [ ] Isolation level support
- [ ] Basic WAL implementation
- [ ] All tests passing

### Documentation
- [ ] Weekly notes with key learnings
- [ ] Lock compatibility matrix
- [ ] Deadlock detection algorithm explanation
- [ ] Transaction state diagram
- [ ] Isolation level comparison table
- [ ] Experiment results and analysis

### Demo
- [ ] Demo showing:
  - Two concurrent transactions
  - Lock waiting
  - Deadlock detection and resolution
  - Transaction abort and rollback
  - Different isolation levels
  - Bank transfer example (atomicity demonstration)

---

## ✅ Success Criteria

- [ ] Transactions guarantee ACID properties
- [ ] 2PL ensures serializability
- [ ] Deadlock detection works
- [ ] All isolation levels supported
- [ ] Concurrent transactions don't corrupt data
- [ ] All tests pass
- [ ] Ready for recovery implementation

---

## ⏭️ Next Week Preview

**Week 8:** Write-Ahead Logging, Recovery & Final Integration
- Complete WAL implementation
- ARIES-style recovery
- Crash recovery (redo/undo)
- Checkpointing
- Final system integration and testing
- Performance benchmarks
- Project documentation

**Prep:**
- [ ] Study ARIES recovery algorithm
- [ ] Read about crash recovery
- [ ] Understand redo vs undo logging

**Estimated Time:** 30-35 hours
