# Database From Scratch

A hands-on learning project to build a database system from the ground up and gain deep insights into how databases work internally.

## 🎯 Project Goals

- Understand database internals by implementing core components
- Learn through weekly collaborative tasks with friends
- Gain practical knowledge of data structures, storage engines, query processing, and transactions
- Build a working database system step by step

## 📚 What We'll Build

This project aims to implement fundamental database components:

- [ ] **Storage Engine**: File I/O, page management, buffer pool
- [ ] **Data Structures**: B+ trees, hash indexes, LSM trees
- [ ] **Query Parser**: SQL parsing and validation
- [ ] **Query Planner**: Query optimization and execution plans
- [ ] **Execution Engine**: Query execution and result generation
- [ ] **Transaction Manager**: ACID properties, concurrency control
- [ ] **Recovery System**: Write-ahead logging, crash recovery
- [ ] **Indexing**: Primary and secondary indexes

## 🗓️ Weekly Tasks

Each week, we tackle a specific component or feature. Documentation and progress tracking for weekly tasks will be maintained in the `/docs/weekly-tasks/` directory.

### Suggested Roadmap

1. **Week 1-2**: Basic storage layer and page management
2. **Week 3-4**: B+ tree implementation
3. **Week 5-6**: Simple query parser
4. **Week 7-8**: Query execution engine
5. **Week 9-10**: Transaction support
6. **Week 11-12**: Recovery and logging
7. **Beyond**: Advanced features (replication, optimization, etc.)

## 📁 Project Structure

```
database-from-scratch/
├── src/                    # Source code
│   ├── storage/           # Storage engine implementation
│   ├── index/             # Index structures (B+ tree, hash, etc.)
│   ├── query/             # Query parser and planner
│   ├── execution/         # Query execution engine
│   ├── transaction/       # Transaction management
│   └── recovery/          # Recovery system
├── tests/                 # Unit and integration tests
├── docs/                  # Documentation
│   ├── weekly-tasks/      # Weekly task tracking
│   ├── design/            # Design documents
│   └── research/          # Research notes and references
├── examples/              # Example usage and demos
└── benchmarks/            # Performance benchmarks

```

## 🚀 Getting Started

```bash
# Clone the repository
git clone <your-repo-url>
cd database-from-scratch

# Setup will be added as we progress
```

## 🤝 Contributing

This is a collaborative learning project. All team members should:

- Document their learning and insights
- Write tests for implemented features
- Review each other's code
- Share resources and research findings

## 📖 Learning Resources

- [Database Internals by Alex Petrov](https://www.databass.dev/)
- [CMU Database Systems Course](https://15445.courses.cs.cmu.edu/)
- [SQLite Architecture](https://www.sqlite.org/arch.html)
- [Let's Build a Simple Database](https://cstack.github.io/db_tutorial/)

## 📝 License

This is an educational project. Feel free to use and learn from it.

---

**Current Status**: 🌱 Just getting started!
