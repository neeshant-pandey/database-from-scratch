"""
Database configuration.
"""

from dataclasses import dataclass
from .constants import *


@dataclass
class DatabaseConfig:
    """Configuration for the database system."""

    # Storage settings
    page_size: int = PAGE_SIZE
    buffer_pool_size: int = DEFAULT_BUFFER_POOL_SIZE

    # B+ Tree settings
    bptree_internal_max_size: int = BPTREE_INTERNAL_MAX_SIZE
    bptree_leaf_max_size: int = BPTREE_LEAF_MAX_SIZE

    # Logging settings
    enable_logging: bool = True
    log_buffer_size: int = 100  # Number of log records to buffer

    # Checkpointing settings
    checkpoint_interval: int = 60  # Seconds between checkpoints

    # Concurrency settings
    deadlock_detection_interval: int = 1  # Seconds between deadlock checks

    # Isolation level
    default_isolation_level: str = "READ_COMMITTED"

    @staticmethod
    def default() -> 'DatabaseConfig':
        """Return default configuration."""
        return DatabaseConfig()
