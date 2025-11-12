"""
Basic usage example for the database.
"""

import sys
import os

# Add parent directory to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

from src.database import Database


def main():
    """Demonstrate basic database operations."""

    print("=" * 60)
    print("Database From Scratch - Basic Usage Example")
    print("=" * 60)
    print()

    # Create/open database
    print("1. Opening database...")
    db = Database("example.db")
    print("   Database opened successfully")
    print()

    # Create table
    print("2. Creating table 'users'...")
    try:
        db.execute("CREATE TABLE users (id INT, name VARCHAR(50), age INT)")
        print("   Table created successfully")
    except ValueError as e:
        print(f"   Table might already exist: {e}")
    print()

    # Get statistics
    print("3. Database statistics:")
    stats = db.get_stats()
    for category, data in stats.items():
        print(f"   {category}: {data}")
    print()

    # Close database
    print("4. Closing database...")
    db.close()
    print("   Database closed successfully")
    print()

    print("=" * 60)
    print("Example completed!")
    print("=" * 60)


if __name__ == "__main__":
    main()
