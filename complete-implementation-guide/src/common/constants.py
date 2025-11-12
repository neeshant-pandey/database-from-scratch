"""
System-wide constants for the database.
"""

# Page settings
PAGE_SIZE = 4096  # 4KB pages (standard for most systems)
INVALID_PAGE_ID = -1

# Database file settings
MAGIC_NUMBER = 0xDEADBEEF  # Magic number to identify our database files
DB_VERSION = 1

# Buffer pool settings
DEFAULT_BUFFER_POOL_SIZE = 100  # Number of pages to cache

# B+ Tree settings
BPTREE_INTERNAL_MAX_SIZE = 200  # Max keys in internal node
BPTREE_LEAF_MAX_SIZE = 200      # Max keys in leaf node

# Transaction settings
INVALID_TXN_ID = -1
INVALID_LSN = -1

# Hash index settings
HASH_INITIAL_GLOBAL_DEPTH = 2
HASH_BUCKET_SIZE = 50  # Max entries per bucket
