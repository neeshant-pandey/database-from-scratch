"""
Main Database class: high-level API for the database system.
"""

from typing import Optional, List, Any
from .common.config import DatabaseConfig
from .storage.disk_manager import DiskManager
from .storage.buffer_pool_manager import BufferPoolManager
from .storage.table_heap import TableHeap
from .index.bptree import BPTreeIndex
from .transaction.transaction_manager import TransactionManager, Transaction, IsolationLevel
from .transaction.lock_manager import LockManager


class Database:
    """
    Main database class providing high-level API.

    This integrates all components: storage, indexing, transactions, etc.
    """

    def __init__(self, db_path: str, config: Optional[DatabaseConfig] = None):
        """
        Initialize database. Creates new database file or opens existing one.

        Args:
            db_path: Path to database file
            config: Database configuration (uses defaults if None)
        """
        self.db_path = db_path
        self.config = config if config is not None else DatabaseConfig.default()

        # Initialize storage layer
        self.disk_manager = DiskManager(db_path)
        self.buffer_pool = BufferPoolManager(
            self.disk_manager,
            pool_size=self.config.buffer_pool_size
        )

        # Initialize transaction management
        self.transaction_manager = TransactionManager()
        self.lock_manager = LockManager()

        # Initialize catalog (simplified: in-memory for now)
        self.tables = {}  # table_name -> TableHeap
        self.indexes = {}  # index_name -> BPTreeIndex

        # Auto-transaction mode (each query is its own transaction)
        self.auto_transaction = True

    def execute(self, sql: str, txn: Optional[Transaction] = None) -> List[Any]:
        """
        Execute a SQL statement.

        Args:
            sql: SQL query string
            txn: Optional transaction context (uses auto-transaction if None)

        Returns:
            List of result tuples for SELECT, empty list for other statements
        """
        # Create transaction if not provided and auto mode enabled
        if txn is None and self.auto_transaction:
            txn = self.transaction_manager.begin()
            auto_commit = True
        else:
            auto_commit = False

        try:
            # TODO: Parse SQL, plan query, execute
            # For now, this is a placeholder

            # Example: Handle simple CREATE TABLE
            if sql.upper().startswith("CREATE TABLE"):
                table_name = self._parse_table_name(sql)
                self._create_table(table_name)
                result = []

            # Example: Handle simple INSERT
            elif sql.upper().startswith("INSERT"):
                # Simplified INSERT parsing
                result = []

            # Example: Handle simple SELECT
            elif sql.upper().startswith("SELECT"):
                # Simplified SELECT
                result = []

            else:
                raise ValueError(f"Unsupported SQL: {sql}")

            # Auto-commit if needed
            if auto_commit:
                self.transaction_manager.commit(txn)

            return result

        except Exception as e:
            # Auto-abort on error
            if auto_commit:
                self.transaction_manager.abort(txn)
            raise e

    def begin_transaction(self, isolation_level: IsolationLevel = IsolationLevel.READ_COMMITTED) -> Transaction:
        """
        Begin a new user-managed transaction.

        Args:
            isolation_level: Transaction isolation level

        Returns:
            Transaction object
        """
        return self.transaction_manager.begin(isolation_level)

    def commit(self, txn: Transaction) -> bool:
        """
        Commit a transaction.

        Args:
            txn: Transaction to commit

        Returns:
            True if successful, False otherwise
        """
        success = self.transaction_manager.commit(txn)
        if success:
            # Release all locks
            self.lock_manager.unlock_all(txn.txn_id)
        return success

    def abort(self, txn: Transaction) -> bool:
        """
        Abort a transaction and rollback changes.

        Args:
            txn: Transaction to abort

        Returns:
            True if successful, False otherwise
        """
        success = self.transaction_manager.abort(txn)
        if success:
            # Release all locks
            self.lock_manager.unlock_all(txn.txn_id)
        return success

    def _create_table(self, table_name: str) -> None:
        """Create a new table."""
        if table_name in self.tables:
            raise ValueError(f"Table {table_name} already exists")

        table_heap = TableHeap(self.buffer_pool)
        self.tables[table_name] = table_heap

    def _parse_table_name(self, sql: str) -> str:
        """Extract table name from CREATE TABLE statement (simplified)."""
        tokens = sql.split()
        if len(tokens) >= 3 and tokens[0].upper() == "CREATE" and tokens[1].upper() == "TABLE":
            return tokens[2].replace("(", "").replace(";", "")
        raise ValueError("Invalid CREATE TABLE syntax")

    def get_stats(self) -> dict:
        """
        Get database statistics.

        Returns:
            Dictionary with various statistics
        """
        return {
            'disk_manager': self.disk_manager.get_stats(),
            'buffer_pool': self.buffer_pool.get_stats(),
            'num_tables': len(self.tables),
            'num_indexes': len(self.indexes),
            'active_transactions': len(self.transaction_manager.get_active_transactions())
        }

    def close(self) -> None:
        """
        Close database and flush all data to disk.
        """
        # Flush all dirty pages
        self.buffer_pool.flush_all_pages()

        # Close disk manager
        self.disk_manager.close()

    def __enter__(self):
        """Context manager support."""
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        """Context manager cleanup."""
        self.close()
        return False
