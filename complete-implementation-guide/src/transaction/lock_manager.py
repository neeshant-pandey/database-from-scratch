"""
Lock Manager: manages locks for concurrency control using 2PL.
"""

import threading
from enum import Enum
from dataclasses import dataclass
from typing import Dict, Set, List, Optional
from ..common.types import TxnId, RID


class LockMode(Enum):
    """Lock modes."""
    SHARED = 1    # Read lock
    EXCLUSIVE = 2  # Write lock


@dataclass
class LockRequest:
    """Represents a lock request."""
    txn_id: TxnId
    lock_mode: LockMode
    granted: bool = False


class LockManager:
    """
    Manages locks for all transactions using 2-Phase Locking (2PL).
    """

    def __init__(self):
        # Lock table: RID -> list of lock requests
        self.lock_table: Dict[RID, List[LockRequest]] = {}

        # Transaction lock sets (for quick lookup and deadlock detection)
        self.txn_locks: Dict[TxnId, Set[RID]] = {}

        # Wait-for graph for deadlock detection
        self.wait_for: Dict[TxnId, Set[TxnId]] = {}

        self.lock = threading.RLock()

    def lock_shared(self, txn_id: TxnId, rid: RID) -> bool:
        """
        Acquire shared (read) lock.
        Compatible with other shared locks, incompatible with exclusive locks.
        """
        with self.lock:
            # Check if already have compatible lock
            if self._has_lock(txn_id, rid):
                return True

            # Check if can grant lock
            if self._can_grant_shared(rid):
                self._grant_lock(txn_id, rid, LockMode.SHARED)
                return True

            # Need to wait (simplified: just fail for now)
            # Real implementation would block and wait
            return False

    def lock_exclusive(self, txn_id: TxnId, rid: RID) -> bool:
        """
        Acquire exclusive (write) lock.
        Incompatible with all other locks.
        """
        with self.lock:
            # Check if already have exclusive lock
            if self._has_exclusive_lock(txn_id, rid):
                return True

            # Check if can grant lock
            if self._can_grant_exclusive(rid, txn_id):
                # If have shared lock, upgrade to exclusive
                if self._has_shared_lock(txn_id, rid):
                    self._upgrade_lock(txn_id, rid)
                else:
                    self._grant_lock(txn_id, rid, LockMode.EXCLUSIVE)
                return True

            # Need to wait (simplified: just fail for now)
            return False

    def unlock(self, txn_id: TxnId, rid: RID) -> bool:
        """Release lock."""
        with self.lock:
            if rid not in self.lock_table:
                return False

            # Find and remove lock request
            requests = self.lock_table[rid]
            for i, req in enumerate(requests):
                if req.txn_id == txn_id and req.granted:
                    requests.pop(i)

                    # Remove from transaction lock set
                    if txn_id in self.txn_locks:
                        self.txn_locks[txn_id].discard(rid)

                    # Clean up empty entries
                    if not requests:
                        del self.lock_table[rid]

                    # TODO: Wake up waiting transactions
                    return True

            return False

    def unlock_all(self, txn_id: TxnId) -> None:
        """Release all locks held by transaction."""
        with self.lock:
            if txn_id not in self.txn_locks:
                return

            # Get copy of RIDs (since we'll modify the set)
            rids = list(self.txn_locks[txn_id])

            for rid in rids:
                self.unlock(txn_id, rid)

            # Clean up
            if txn_id in self.txn_locks:
                del self.txn_locks[txn_id]

    def _has_lock(self, txn_id: TxnId, rid: RID) -> bool:
        """Check if transaction has any lock on RID."""
        if txn_id not in self.txn_locks:
            return False
        return rid in self.txn_locks[txn_id]

    def _has_shared_lock(self, txn_id: TxnId, rid: RID) -> bool:
        """Check if transaction has shared lock on RID."""
        if rid not in self.lock_table:
            return False

        for req in self.lock_table[rid]:
            if req.txn_id == txn_id and req.lock_mode == LockMode.SHARED and req.granted:
                return True
        return False

    def _has_exclusive_lock(self, txn_id: TxnId, rid: RID) -> bool:
        """Check if transaction has exclusive lock on RID."""
        if rid not in self.lock_table:
            return False

        for req in self.lock_table[rid]:
            if req.txn_id == txn_id and req.lock_mode == LockMode.EXCLUSIVE and req.granted:
                return True
        return False

    def _can_grant_shared(self, rid: RID) -> bool:
        """Check if shared lock can be granted (no exclusive locks)."""
        if rid not in self.lock_table:
            return True

        for req in self.lock_table[rid]:
            if req.lock_mode == LockMode.EXCLUSIVE and req.granted:
                return False
        return True

    def _can_grant_exclusive(self, rid: RID, txn_id: TxnId) -> bool:
        """Check if exclusive lock can be granted (no other locks)."""
        if rid not in self.lock_table:
            return True

        for req in self.lock_table[rid]:
            if req.txn_id != txn_id and req.granted:
                return False
        return True

    def _grant_lock(self, txn_id: TxnId, rid: RID, mode: LockMode) -> None:
        """Grant lock to transaction."""
        if rid not in self.lock_table:
            self.lock_table[rid] = []

        request = LockRequest(txn_id, mode, granted=True)
        self.lock_table[rid].append(request)

        # Track in transaction lock set
        if txn_id not in self.txn_locks:
            self.txn_locks[txn_id] = set()
        self.txn_locks[txn_id].add(rid)

    def _upgrade_lock(self, txn_id: TxnId, rid: RID) -> None:
        """Upgrade shared lock to exclusive."""
        for req in self.lock_table[rid]:
            if req.txn_id == txn_id and req.lock_mode == LockMode.SHARED:
                req.lock_mode = LockMode.EXCLUSIVE
                break
