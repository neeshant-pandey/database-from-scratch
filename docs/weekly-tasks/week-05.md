# Week 5: SQL Parser & Query Representation

**Focus**: Building a SQL parser and abstract syntax tree (AST)

---

## 🎯 Learning Objectives

- [ ] Understand lexical analysis and parsing
- [ ] Build a tokenizer for SQL
- [ ] Implement recursive descent parser
- [ ] Create AST node classes for SQL statements
- [ ] Validate and type-check queries
- [ ] Handle basic SQL: SELECT, INSERT, UPDATE, DELETE, CREATE TABLE

---

## 📚 Study & Research (6-7 hours)

### Core Concepts

**1. Parsing Fundamentals**
- [ ] Lexical analysis (tokenization)
- [ ] Syntax analysis (parsing)
- [ ] Context-free grammars
- [ ] Recursive descent parsing
- [ ] Abstract syntax trees vs parse trees
- [ ] Operator precedence

**2. SQL Grammar**
- [ ] SELECT statement structure
- [ ] FROM clause (table references)
- [ ] WHERE clause (predicates)
- [ ] JOIN operations
- [ ] GROUP BY / HAVING
- [ ] ORDER BY / LIMIT
- [ ] INSERT/UPDATE/DELETE/CREATE TABLE syntax

**3. Query Validation**
- [ ] Schema checking (table/column existence)
- [ ] Type checking (compatible operations)
- [ ] Aggregate function validation
- [ ] Alias resolution

### Required Reading

- [ ] "Compilers: Principles, Techniques, and Tools" (Dragon Book) - Chapter 2 & 4
- [ ] SQL-92 Grammar specification (subset)
- [ ] "Building a Simple SQL Parser" articles
- [ ] Study SQLite's parser architecture
- [ ] CMU 15-445 Lecture on Query Processing overview
- [ ] Python PLY (lex/yacc) or Lark parser libraries

### Discussion Questions

1. Why separate lexing from parsing?
2. What's the difference between AST and parse tree?
3. How do you handle operator precedence in expressions?
4. Why validate queries before execution?
5. Should parser depend on storage layer?

---

## 💻 Implementation Tasks (18-22 hours)

### Task 1: Implement Tokenizer (Lexer)

**What to Build:**
Convert SQL string into sequence of tokens

**Token Types:**
- [ ] Keywords: SELECT, FROM, WHERE, INSERT, CREATE, etc.
- [ ] Identifiers: table names, column names
- [ ] Literals: numbers, strings
- [ ] Operators: =, <, >, <=, >=, !=, AND, OR, NOT
- [ ] Punctuation: (, ), ,, ;, *, .
- [ ] Whitespace (skip)
- [ ] Comments (skip)

**Requirements:**
- [ ] Scan input character by character
- [ ] Recognize keywords (case-insensitive)
- [ ] Handle string literals with quotes
- [ ] Handle identifiers with backticks/quotes
- [ ] Track line and column numbers for errors
- [ ] Return list/iterator of tokens

**Token Class:**
- `type`: token type enum
- `value`: actual string value
- `line`: line number
- `column`: column number

**Deliverable:** `src/query/lexer.py`

### Task 2: Design AST Node Classes

**What to Build:**
Classes representing SQL statement components

**Statement Nodes:**
- [ ] `SelectStatement(columns, from_clause, where, group_by, order_by, limit)`
- [ ] `InsertStatement(table, columns, values)`
- [ ] `UpdateStatement(table, set_clauses, where)`
- [ ] `DeleteStatement(table, where)`
- [ ] `CreateTableStatement(table, columns, constraints)`

**Expression Nodes:**
- [ ] `ColumnRef(table, column)` - column reference
- [ ] `Literal(value, type)` - constant value
- [ ] `BinaryOp(left, op, right)` - e.g., a > 5
- [ ] `UnaryOp(op, operand)` - e.g., NOT x
- [ ] `FunctionCall(name, args)` - e.g., COUNT(*)
- [ ] `Wildcard()` - SELECT *

**Other Nodes:**
- [ ] `TableRef(name, alias)` - table in FROM
- [ ] `JoinClause(left, join_type, right, condition)`
- [ ] `OrderByClause(expr, direction)` - ASC/DESC
- [ ] `GroupByClause(columns)`

**Requirements:**
- [ ] All nodes inherit from base `ASTNode`
- [ ] Implement `__repr__` for debugging
- [ ] Optional: visitor pattern for traversal

**Deliverable:** `src/query/ast_nodes.py`

### Task 3: Implement Parser

**What to Build:**
Recursive descent parser that builds AST from tokens

**Parsing Methods (one per grammar rule):**
- [ ] `parse_statement()` - top-level (SELECT/INSERT/etc.)
- [ ] `parse_select()` - SELECT statement
- [ ] `parse_insert()` - INSERT statement
- [ ] `parse_create_table()` - CREATE TABLE
- [ ] `parse_expression()` - expressions with precedence
- [ ] `parse_where_clause()` - WHERE predicates
- [ ] `parse_from_clause()` - FROM with joins
- [ ] `parse_column_list()` - column references
- [ ] `parse_value_list()` - list of values

**Requirements:**
- [ ] Lookahead tokens to decide parse path
- [ ] Handle operator precedence (AND before OR, etc.)
- [ ] Provide helpful error messages
- [ ] Recover from syntax errors where possible

**Helper Methods:**
- `peek()` - look at current token without consuming
- `advance()` - consume current token
- `expect(type)` - consume token or error
- `match(type)` - check if current token matches

**Deliverable:** `src/query/parser.py`

### Task 4: Implement Catalog & Schema

**What to Build:**
System catalog storing table schemas

**Requirements:**
- [ ] Store table definitions (name, columns)
- [ ] Store column definitions (name, type, constraints)
- [ ] CRUD operations on catalog
- [ ] Persist catalog to disk (use special pages)
- [ ] Lookup table by name
- [ ] Lookup columns by table

**TableSchema Class:**
- `name`: table name
- `columns`: list of Column objects
- `primary_key`: primary key column(s)

**Column Class:**
- `name`: column name
- `type`: data type (INT, VARCHAR, etc.)
- `nullable`: bool
- `default`: default value

**Deliverable:** `src/catalog/schema.py` and `src/catalog/catalog_manager.py`

### Task 5: Implement Query Validator

**What to Build:**
Validate AST against catalog schema

**Validation Checks:**
- [ ] Table exists in catalog
- [ ] All referenced columns exist
- [ ] Column types are compatible in operations
- [ ] Aggregate functions used correctly
- [ ] GROUP BY columns match SELECT
- [ ] No ambiguous column references

**Requirements:**
- [ ] Walk AST and check each node
- [ ] Provide clear error messages with positions
- [ ] Return validated AST (possibly annotated with types)

**Deliverable:** `src/query/validator.py`

### Task 6: Comprehensive Testing

**Lexer Tests:**
- [ ] Tokenize simple SELECT statement
- [ ] Handle keywords (case insensitive)
- [ ] Parse string literals with quotes
- [ ] Handle operators and punctuation
- [ ] Skip whitespace and comments
- [ ] Error on invalid characters

**Parser Tests:**
- [ ] Parse: `SELECT * FROM users`
- [ ] Parse: `SELECT id, name FROM users WHERE age > 18`
- [ ] Parse: `SELECT COUNT(*) FROM orders GROUP BY customer_id`
- [ ] Parse: `INSERT INTO users (id, name) VALUES (1, 'Alice')`
- [ ] Parse: `UPDATE users SET name = 'Bob' WHERE id = 1`
- [ ] Parse: `DELETE FROM users WHERE age < 18`
- [ ] Parse: `CREATE TABLE users (id INT, name VARCHAR(50))`
- [ ] Parse complex expressions with precedence
- [ ] Error on syntax errors with helpful messages

**Validator Tests:**
- [ ] Accept valid query
- [ ] Reject non-existent table
- [ ] Reject non-existent column
- [ ] Reject type mismatch in WHERE
- [ ] Reject invalid aggregate usage
- [ ] Reject ambiguous column references

**Deliverable:** Comprehensive test suite

---

## 🧪 Experiments (3-4 hours)

### Experiment 1: Parser Performance

**Goal:** Understand parsing overhead

- [ ] Generate queries of increasing complexity
- [ ] Measure parsing time
- [ ] Compare recursive descent vs parser library (PLY/Lark)
- [ ] Plot: query complexity vs parse time
- [ ] Document findings

### Experiment 2: Error Recovery

**Goal:** Provide better error messages

- [ ] Create queries with common syntax errors
- [ ] Test error messages from parser
- [ ] Improve error messages for clarity
- [ ] Document patterns for good error reporting

### Experiment 3: SQL Dialect Comparison

**Goal:** Understand SQL variations

- [ ] Compare PostgreSQL, MySQL, SQLite SQL syntax
- [ ] Document key differences
- [ ] Decide which features to support
- [ ] Create your SQL dialect specification

---

## 📝 Deliverables

### Code
- [ ] Lexer (tokenizer)
- [ ] AST node classes
- [ ] Parser (recursive descent)
- [ ] Catalog and schema management
- [ ] Query validator
- [ ] All tests passing

### Documentation
- [ ] Weekly notes
- [ ] SQL grammar specification you support
- [ ] AST node class diagram
- [ ] Parser architecture diagram
- [ ] Example queries with AST visualizations
- [ ] Error handling guide

### Demo
- [ ] Interactive SQL shell that:
  - Accepts SQL statements
  - Parses and prints AST
  - Validates against catalog
  - Shows helpful errors
  - Supports: SELECT, INSERT, CREATE TABLE

---

## ✅ Success Criteria

- [ ] Can parse common SQL statements
- [ ] Generates correct AST
- [ ] Validates queries against schema
- [ ] Provides helpful error messages
- [ ] Handles operator precedence
- [ ] All tests pass
- [ ] Ready to execute queries (next week)

---

## ⏭️ Next Week Preview

**Week 6:** Query Planning & Execution Engine
- Convert AST to execution plan
- Implement operators: Scan, Filter, Project, Join
- Query optimization basics
- Execute queries and return results

**Prep:**
- [ ] Study iterator model (volcano model)
- [ ] Read about query plans
- [ ] Understand join algorithms

**Estimated Time:** 26-30 hours
