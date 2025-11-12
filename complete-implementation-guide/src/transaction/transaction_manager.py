"""
Transaction Manager: manages transaction lifecycle and ACID properties.
"""

import threading
from enum import Enum
from dataclasses import dataclass, field
from typing import Dict, Set, Optional
from ..common.types import TxnId, LSN, RID
from ..common.constants import INVALID_TXN_ID, INVALID_LSN


class TransactionState(Enum):
    """Transaction states."""
    RUNNING = 1
    COMMITTED = 2
    ABORTED = 3


class IsolationLevel(Enum):
    """SQL isolation levels."""
    READ_UNCOMMITTED = 1
    READ_COMMITTED = 2
    REPEATABLE_READ = 3
    SERIALIZABLE = 4


@dataclass
class Transaction:
    """Represents a single transaction."""
    txn_id: TxnId
    state: TransactionState = TransactionState.RUNNING
    isolation_level: IsolationLevel = IsolationLevel.READ_COMMITTED

    # Lock tracking
    shared_locks: Set[RID] = field(default_factory=set)
    exclusive_locks: Set[RID] = field(default_factory=set)

    # Undo log for rollback
    undo_log: list = field(default_factory=list)

    # Logging
    first_lsn: LSN = LSN(INVALID_LSN)
    last_lsn: LSN = LSN(INVALID_LSN)

    def is_running(self) -> bool:
        return self.state == TransactionState.RUNNING

    def is_committed(self) -> bool:
        return self.state == TransactionState.COMMITTED

    def is_aborted(self) -> bool:
        return self.state == TransactionState.ABORTED


class TransactionManager:
    """
    Manages all transactions in the system.
    """

    def __init__(self):
        self.next_txn_id = 0
        self.transactions: Dict[TxnId, Transaction] = {}
        self.lock = threading.RLock()

    def begin(self, isolation_level: IsolationLevel = IsolationLevel.READ_COMMITTED) -> Transaction:
        """Begin a new transaction."""
        with self.lock:
            txn_id = TxnId(self.next_txn_id)
            self.next_txn_id += 1

            txn = Transaction(
                txn_id=txn_id,
                isolation_level=isolation_level
            )

            self.transactions[txn_id] = txn
            return txn

    def commit(self, txn: Transaction) -> bool:
        """
        Commit a transaction.
        Releases all locks and marks transaction as committed.
        """
        with self.lock:
            if not txn.is_running():
                return False

            # TODO: Write COMMIT log record and flush WAL

            # Release all locks (handled by lock manager)
            txn.state = TransactionState.COMMITTED

            return True

    def abort(self, txn: Transaction) -> bool:
        """
        Abort a transaction.
        Rolls back changes, releases locks, marks as aborted.
        """
        with self.lock:
            if not txn.is_running():
                return False

            # Rollback changes from undo log
            for undo_entry in reversed(txn.undo_log):
                # Apply undo operation
                # TODO: Implement actual undo logic
                pass

            # TODO: Write ABORT log record

            # Release all locks (handled by lock manager)
            txn.state = TransactionState.ABORTED

            return True

    def get_transaction(self, txn_id: TxnId) -> Optional[Transaction]:
        """Get transaction by ID."""
        with self.lock:
            return self.transactions.get(txn_id)

    def get_active_transactions(self) -> list:
        """Get all active (running) transactions."""
        with self.lock:
            return [txn for txn in self.transactions.values() if txn.is_running()]
