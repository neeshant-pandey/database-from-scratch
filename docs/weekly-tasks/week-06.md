# Week 6: Query Planning & Execution Engine

**Focus**: Converting AST to execution plans and executing queries

---

## 🎯 Learning Objectives

- [ ] Understand the iterator/volcano execution model
- [ ] Implement physical operators (Scan, Filter, Project, Join, Aggregate)
- [ ] Convert AST to execution plan
- [ ] Implement basic query optimization
- [ ] Execute queries and return results

---

## 📚 Study & Research (6-7 hours)

### Core Concepts

**1. Query Execution Models**
- [ ] Volcano/Iterator model (pull-based)
- [ ] Vectorized execution (columnar batches)
- [ ] Compilation-based execution
- [ ] Why databases use iterator model

**2. Physical Operators**
- [ ] Sequential Scan (read all tuples from table)
- [ ] Index Scan (use B+ tree to find tuples)
- [ ] Filter (WHERE predicate)
- [ ] Projection (SELECT columns)
- [ ] Nested Loop Join
- [ ] Hash Join
- [ ] Sort (ORDER BY)
- [ ] Aggregation (GROUP BY, COUNT, SUM, etc.)
- [ ] Limit (LIMIT clause)

**3. Query Planning**
- [ ] Logical plan vs physical plan
- [ ] Query rewriting (algebraic optimization)
- [ ] Cost-based optimization
- [ ] Statistics for cost estimation
- [ ] Join order selection

**4. Execution Pipeline**
- [ ] Open-Next-Close protocol
- [ ] Pipelining vs materialization
- [ ] Operator implementation patterns

### Required Reading

- [ ] Database Internals - Chapter 6 (Query Execution)
- [ ] CMU 15-445 Lectures 11-13 (Query Execution, Join Algorithms, Query Optimization)
- [ ] "Volcano - An Extensible and Parallel Query Evaluation System"
- [ ] PostgreSQL query execution documentation
- [ ] "Access Path Selection in a Relational Database" (Selinger paper - System R)

### Discussion Questions

1. Why use iterator model instead of materializing results?
2. When is nested loop join better than hash join?
3. How do you estimate query cost?
4. Why is join order selection important?
5. What's the difference between logical and physical plans?

---

## 💻 Implementation Tasks (20-24 hours)

### Task 1: Implement Execution Operators

**What to Build:**
Base operator class and concrete operator implementations

**Base Operator (Abstract Class):**
```
Methods:
- init() - initialize operator
- next() - get next tuple (returns None when done)
- close() - cleanup resources
- get_schema() - return output schema
```

**Operators to Implement:**

**1. Sequential Scan Operator**
- [ ] Scan all tuples from a table heap
- [ ] Use table heap iterator
- [ ] Return tuples one by one

**2. Index Scan Operator**
- [ ] Use B+ tree index to find tuples
- [ ] Support point queries and range scans
- [ ] Fetch tuples using RIDs from index

**3. Filter Operator (Selection)**
- [ ] Take input from child operator
- [ ] Evaluate predicate on each tuple
- [ ] Return only tuples that match

**4. Projection Operator**
- [ ] Take input from child operator
- [ ] Extract specified columns
- [ ] Return projected tuples

**5. Nested Loop Join Operator**
- [ ] Two child operators (outer and inner)
- [ ] For each outer tuple, scan all inner tuples
- [ ] Evaluate join predicate
- [ ] Return matching tuple pairs

**6. Hash Join Operator**
- [ ] Build phase: hash inner tuples
- [ ] Probe phase: for each outer tuple, probe hash table
- [ ] Return matching tuples

**7. Aggregation Operator**
- [ ] Hash-based aggregation
- [ ] Support: COUNT, SUM, AVG, MIN, MAX
- [ ] Handle GROUP BY
- [ ] Handle HAVING clause

**8. Sort Operator**
- [ ] External merge sort for large datasets
- [ ] Support ORDER BY with ASC/DESC
- [ ] Multiple sort keys

**9. Limit Operator**
- [ ] Return first N tuples from child
- [ ] Stop early (don't fetch all)

**10. Insert Executor**
- [ ] Insert tuples into table heap
- [ ] Update indexes

**11. Update Executor**
- [ ] Find tuples to update
- [ ] Modify tuples
- [ ] Update indexes

**12. Delete Executor**
- [ ] Find tuples to delete
- [ ] Remove from table
- [ ] Update indexes

**Deliverable:** `src/execution/operators.py` (or split into multiple files)

### Task 2: Implement Planner

**What to Build:**
Convert AST to physical execution plan

**Requirements:**
- [ ] Walk AST and build operator tree
- [ ] Choose access method (seq scan vs index scan)
- [ ] Decide join algorithm (nested loop vs hash)
- [ ] Insert necessary operators (filter, project)
- [ ] Handle ORDER BY with sort operator
- [ ] Handle GROUP BY with aggregation operator

**Planner Methods:**
- `plan(ast_node)` - main planning entry
- `plan_select(select_stmt)` - plan SELECT
- `plan_insert(insert_stmt)` - plan INSERT
- `plan_update(update_stmt)` - plan UPDATE
- `plan_delete(delete_stmt)` - plan DELETE
- `choose_scan(table, predicate)` - seq vs index scan
- `choose_join(join_type)` - join algorithm selection

**Deliverable:** `src/execution/planner.py`

### Task 3: Implement Query Optimizer (Basic)

**What to Build:**
Simple rule-based and cost-based optimizations

**Rule-Based Optimizations:**
- [ ] Predicate pushdown (apply filters early)
- [ ] Projection pushdown (fetch only needed columns)
- [ ] Constant folding (evaluate constant expressions)
- [ ] Remove redundant operators

**Cost-Based Optimizations:**
- [ ] Collect table statistics (tuple count, column cardinalities)
- [ ] Estimate operator costs
- [ ] Choose index scan when selective predicate
- [ ] Join order selection (dynamic programming for small joins)

**Deliverable:** `src/execution/optimizer.py`

### Task 4: Implement Executor Engine

**What to Build:**
Main query executor that runs the plan

**Requirements:**
- [ ] Take query string as input
- [ ] Lex, parse, validate
- [ ] Generate execution plan
- [ ] Optimize plan
- [ ] Execute plan
- [ ] Return results (list of tuples)
- [ ] Handle errors gracefully

**Executor Class:**
```
Methods:
- execute_query(sql) - run SQL and return results
- execute_plan(plan) - execute operator tree
- fetch_all(operator) - get all results from operator
- fetch_one(operator) - get single result
```

**Deliverable:** `src/execution/executor.py`

### Task 5: Build Interactive SQL Shell

**What to Build:**
Command-line interface to execute SQL

**Requirements:**
- [ ] REPL loop (Read-Eval-Print-Loop)
- [ ] Accept SQL statements
- [ ] Display results in table format
- [ ] Show execution time
- [ ] Special commands: `.exit`, `.tables`, `.schema`, `.explain`
- [ ] Pretty-print results with column alignment

**Deliverable:** `src/sql_shell.py`

### Task 6: Comprehensive Testing

**Operator Tests:**
- [ ] Sequential scan returns all tuples
- [ ] Index scan with predicate
- [ ] Filter operator applies predicate correctly
- [ ] Projection extracts correct columns
- [ ] Nested loop join produces correct results
- [ ] Hash join produces correct results
- [ ] Aggregation with GROUP BY
- [ ] Sort operator orders correctly
- [ ] Limit operator stops early

**End-to-End Query Tests:**
- [ ] SELECT * FROM table
- [ ] SELECT col1, col2 FROM table WHERE col1 > 10
- [ ] SELECT COUNT(*) FROM table
- [ ] SELECT AVG(price) FROM products GROUP BY category
- [ ] SELECT * FROM users JOIN orders ON users.id = orders.user_id
- [ ] INSERT INTO table VALUES (...)
- [ ] UPDATE table SET col = value WHERE condition
- [ ] DELETE FROM table WHERE condition
- [ ] Complex query with multiple joins, filters, aggregates

**Performance Tests:**
- [ ] Query with 100K tuples
- [ ] Join two tables with 10K tuples each
- [ ] Measure query execution time

**Deliverable:** Comprehensive test suite

---

## 🧪 Experiments (4-5 hours)

### Experiment 1: Join Algorithm Performance

**Goal:** Compare nested loop vs hash join

- [ ] Create two tables (1K and 10K tuples)
- [ ] Measure join time with nested loop
- [ ] Measure join time with hash join
- [ ] Vary table sizes
- [ ] Plot results
- [ ] Document when each is better

### Experiment 2: Index vs Sequential Scan

**Goal:** Understand when indexes help

- [ ] Table with 100K tuples
- [ ] Query with high selectivity (1% match)
- [ ] Query with low selectivity (50% match)
- [ ] Measure time with seq scan vs index scan
- [ ] Document crossover point

### Experiment 3: Query Optimization Impact

**Goal:** Measure optimization effectiveness

- [ ] Complex query: joins + filters + aggregation
- [ ] Execute without optimization
- [ ] Execute with predicate pushdown
- [ ] Execute with join reordering
- [ ] Measure time difference
- [ ] Document optimizations that helped most

### Experiment 4: TPC-H Style Queries

**Goal:** Test on realistic workload

- [ ] Create simplified TPC-H schema (customers, orders, lineitems)
- [ ] Load sample data
- [ ] Run TPC-H style analytical queries
- [ ] Measure execution time
- [ ] Document query complexity your system can handle

---

## 📝 Deliverables

### Code
- [ ] All execution operators
- [ ] Query planner
- [ ] Basic optimizer
- [ ] Executor engine
- [ ] Interactive SQL shell
- [ ] All tests passing

### Documentation
- [ ] Weekly notes
- [ ] Execution operator diagram
- [ ] Query plan examples (with visualizations)
- [ ] Optimization rules documented
- [ ] Experiment results with analysis
- [ ] SQL shell user guide

### Demo
- [ ] Record video/demo showing:
  - Creating tables via SQL
  - Inserting data
  - Running SELECT queries
  - Using joins and aggregates
  - Showing execution plans with `.explain`
  - Performance comparison

---

## ✅ Success Criteria

- [ ] Can execute SELECT, INSERT, UPDATE, DELETE
- [ ] Supports WHERE, JOIN, GROUP BY, ORDER BY, LIMIT
- [ ] Query optimizer improves performance
- [ ] Interactive SQL shell works
- [ ] Can handle 100K+ tuple queries
- [ ] All tests pass
- [ ] Ready for transactions (next week)

---

## ⏭️ Next Week Preview

**Week 7:** Transaction Management & Concurrency Control
- ACID properties implementation
- Locking protocols (2PL)
- Deadlock detection/prevention
- Isolation levels
- MVCC (if time permits)

**Prep:**
- [ ] Study transaction concepts
- [ ] Read about 2-phase locking
- [ ] Understand deadlock detection

**Estimated Time:** 28-32 hours
