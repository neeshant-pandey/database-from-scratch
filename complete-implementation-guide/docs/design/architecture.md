# Database Architecture

## System Overview

This database is built using a layered architecture, where each layer provides abstractions to the layer above it.

```
┌─────────────────────────────────────┐
│       SQL Shell / Application       │  User Interface
└─────────────────────────────────────┘
                  ↓
┌─────────────────────────────────────┐
│         Query Execution Layer       │  Operators, Planner
│    (Scan, Join, Filter, Project)    │  Optimizer
└─────────────────────────────────────┘
                  ↓
┌──────────────────┬──────────────────┐
│  Transaction Mgr │   Catalog Mgr    │  Transaction Control
│  Lock Manager    │   Schema Info    │  Metadata
└──────────────────┴──────────────────┘
                  ↓
┌──────────────────┬──────────────────┐
│   Table Heap     │   Index Layer    │  Data Access
│  (Slotted Pages) │  (B+ Tree, Hash) │  Methods
└──────────────────┴──────────────────┘
                  ↓
┌─────────────────────────────────────┐
│       Buffer Pool Manager           │  Memory Management
│          (LRU Caching)              │  Pin/Unpin
└─────────────────────────────────────┘
                  ↓
┌─────────────────────────────────────┐
│         Disk Manager                │  File I/O
│    (Page Read/Write, fsync)         │  Durability
└─────────────────────────────────────┘
                  ↓
┌─────────────────────────────────────┐
│          Database File              │  Persistent Storage
│         (4KB Pages)                 │  Disk
└─────────────────────────────────────┘
```

## Layer Descriptions

### 1. Storage Layer
**Components:** Disk Manager, Buffer Pool Manager, Page

**Responsibilities:**
- Manage database file on disk
- Handle page I/O operations
- Cache frequently-accessed pages in memory
- Implement LRU page replacement
- Ensure data durability with fsync()

**Key Abstractions:**
- **Page**: Fixed-size (4KB) unit of storage
- **Buffer Pool**: In-memory cache of pages
- **Disk Manager**: Interface to physical file

### 2. Data Access Layer
**Components:** Table Heap, Slotted Page, B+ Tree Index, Hash Index

**Responsibilities:**
- Store variable-length tuples efficiently
- Provide fast data access via indexes
- Support sequential scans and index lookups
- Handle page fragmentation

**Key Abstractions:**
- **Table Heap**: Collection of data pages
- **Slotted Page**: Variable-length tuple storage
- **RID (Record ID)**: Unique tuple identifier (page_id, slot_id)
- **Index**: Fast lookup data structure

### 3. Catalog Layer
**Components:** Catalog Manager, Schema

**Responsibilities:**
- Store table schemas (columns, types)
- Manage index definitions
- Provide schema lookup for query validation

### 4. Transaction Layer
**Components:** Transaction Manager, Lock Manager

**Responsibilities:**
- Implement ACID properties
- Manage transaction lifecycle
- Provide concurrency control with 2PL
- Detect and resolve deadlocks
- Support multiple isolation levels

**Key Abstractions:**
- **Transaction**: Unit of work
- **Lock**: Shared (read) or Exclusive (write)
- **2PL Protocol**: Two-phase locking for serializability

### 5. Recovery Layer
**Components:** Log Manager, Recovery Manager, Checkpoint Manager

**Responsibilities:**
- Implement Write-Ahead Logging (WAL)
- Support crash recovery (ARIES algorithm)
- Provide checkpointing to bound recovery time
- Ensure durability of committed transactions

**Key Abstractions:**
- **Log Record**: Capture of database operation
- **LSN**: Log Sequence Number
- **ARIES**: Recovery algorithm (Analysis, Redo, Undo)

### 6. Query Processing Layer
**Components:** Lexer, Parser, Planner, Optimizer, Executor

**Responsibilities:**
- Parse SQL into Abstract Syntax Tree (AST)
- Validate queries against schema
- Generate efficient execution plans
- Execute queries using iterator model
- Return results to user

**Key Abstractions:**
- **AST**: Abstract Syntax Tree
- **Operator**: Query execution unit (Scan, Join, etc.)
- **Iterator Model**: Pull-based execution

### 7. SQL Shell
**Components:** Interactive CLI

**Responsibilities:**
- Accept SQL commands from user
- Display query results
- Provide special commands (.help, .stats, etc.)
- Handle errors gracefully

## Data Flow Examples

### Example 1: SELECT Query

```
User: SELECT * FROM users WHERE age > 25

1. SQL Shell receives query string
2. Lexer tokenizes SQL into tokens
3. Parser builds AST
4. Validator checks schema (users table exists, age column exists)
5. Planner generates execution plan:
   - SeqScan(users) → Filter(age > 25)
6. Executor runs plan:
   - Fetch pages from buffer pool
   - Scan tuples, apply filter
   - Return matching tuples
7. Results displayed to user
```

### Example 2: INSERT with Transaction

```
User: INSERT INTO users VALUES (1, 'Alice', 30)

1. Transaction begins (if auto mode)
2. SQL parsed and validated
3. Executor allocates RID, writes tuple
4. Acquire exclusive lock on new tuple
5. Write UPDATE log record to WAL
6. Mark page as dirty in buffer pool
7. Transaction commits:
   - Flush WAL to disk
   - Release locks
8. Eventually, dirty page written to disk
```

### Example 3: Crash Recovery

```
System crashes unexpectedly

1. Database reopens
2. Recovery Manager runs:
   a. Analysis: Determine which transactions were active
   b. Redo: Replay all logged operations
   c. Undo: Rollback uncommitted transactions
3. Database returns to consistent state
4. Normal operation resumes
```

## Design Decisions

### 1. Fixed-Size Pages
**Decision:** Use 4KB pages
**Rationale:**
- Matches OS page size for efficiency
- Standard in many databases (PostgreSQL, MySQL)
- Good balance between I/O and overhead

### 2. Buffer Pool with LRU
**Decision:** LRU eviction policy
**Rationale:**
- Simple to implement
- Good hit rates for typical workloads
- Better than FIFO or random

### 3. Slotted Pages
**Decision:** Use slot directory for variable-length tuples
**Rationale:**
- Supports variable-length records efficiently
- Allows in-place deletion (mark slot as free)
- Industry standard (PostgreSQL uses this)

### 4. B+ Trees for Indexes
**Decision:** B+ trees as primary index structure
**Rationale:**
- Balanced tree guarantees O(log N) operations
- Supports range queries (linked leaves)
- Cache-friendly (high fanout)
- Well-studied and proven

### 5. 2-Phase Locking (2PL)
**Decision:** Use strict 2PL for concurrency control
**Rationale:**
- Guarantees serializability
- Simpler than MVCC for learning
- Used in many production databases

### 6. ARIES Recovery
**Decision:** Implement ARIES-style recovery
**Rationale:**
- Industry standard (used in DB2, SQL Server)
- Supports steal/no-force buffer management
- Well-documented algorithm

### 7. Volcano Execution Model
**Decision:** Iterator-based query execution
**Rationale:**
- Allows pipelining (low memory usage)
- Composable operators
- Easy to understand and implement
- Used in many databases

## Performance Characteristics

### Storage
- Page I/O: ~1ms per page (HDD), ~0.1ms (SSD)
- Buffer pool hit rate: 80-95% (typical workloads)

### Indexing
- B+ tree search: O(log N) I/Os
- B+ tree insert: O(log N) I/Os
- Hash index: O(1) I/O (on average)

### Transactions
- Lock acquisition: O(1)
- Deadlock detection: O(N²) worst case
- Transaction throughput: 1,000-10,000 TPS (depends on workload)

### Recovery
- Recovery time: O(log size) with checkpoints
- WAL overhead: ~10-20% performance impact

## Limitations

### Current Limitations
1. **No query optimization:** Uses simple heuristics
2. **Single-machine only:** No distributed support
3. **Limited SQL support:** Subset of SQL-92
4. **No crash during recovery:** Assumes recovery completes
5. **Simple lock granularity:** Tuple-level only

### Future Enhancements
1. **MVCC:** Multi-version concurrency control
2. **Query compilation:** JIT compilation
3. **Parallel execution:** Multi-threaded queries
4. **Replication:** Master-slave replication
5. **Columnar storage:** For analytical workloads
6. **Advanced indexes:** GiST, GIN, BRIN
7. **Partitioning:** Table and index partitioning

## References

- **Database Internals** by Alex Petrov
- **Transaction Processing** by Jim Gray
- **ARIES Paper** by Mohan et al.
- **PostgreSQL Documentation:** https://www.postgresql.org/docs/
- **CMU 15-445:** Database Systems course
