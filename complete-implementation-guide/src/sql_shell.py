"""
Interactive SQL shell for the database.
"""

import sys
import time
from .database import Database


class SQLShell:
    """Interactive SQL shell."""

    def __init__(self, db_path: str):
        self.db = Database(db_path)
        self.running = True

    def run(self) -> None:
        """Start the interactive shell."""
        print("=" * 60)
        print("Database From Scratch - SQL Shell")
        print("=" * 60)
        print(f"Connected to: {self.db.db_path}")
        print("Type '.help' for commands, '.exit' to quit")
        print()

        while self.running:
            try:
                # Read input
                query = input("db> ").strip()

                if not query:
                    continue

                # Handle special commands
                if query.startswith('.'):
                    self._handle_command(query)
                    continue

                # Execute SQL query
                start_time = time.time()
                results = self.db.execute(query)
                elapsed = time.time() - start_time

                # Display results
                if results:
                    self._display_results(results)
                else:
                    print("Query executed successfully")

                print(f"\n({elapsed:.3f} seconds)\n")

            except KeyboardInterrupt:
                print("\nInterrupted")
                continue
            except EOFError:
                print("\nExiting...")
                break
            except Exception as e:
                print(f"Error: {e}\n")

        self.db.close()

    def _handle_command(self, command: str) -> None:
        """Handle special shell commands."""
        cmd = command.lower()

        if cmd == '.exit' or cmd == '.quit':
            self.running = False

        elif cmd == '.help':
            self._show_help()

        elif cmd == '.stats':
            stats = self.db.get_stats()
            print("\nDatabase Statistics:")
            print("-" * 40)
            for category, data in stats.items():
                print(f"\n{category}:")
                if isinstance(data, dict):
                    for key, value in data.items():
                        print(f"  {key}: {value}")
                else:
                    print(f"  {data}")
            print()

        elif cmd == '.tables':
            print("\nTables:")
            for table_name in self.db.tables.keys():
                print(f"  {table_name}")
            print()

        else:
            print(f"Unknown command: {command}")
            print("Type '.help' for available commands\n")

    def _show_help(self) -> None:
        """Display help message."""
        print("\nAvailable Commands:")
        print("-" * 40)
        print("  .help       - Show this help message")
        print("  .exit       - Exit the shell")
        print("  .quit       - Exit the shell")
        print("  .stats      - Show database statistics")
        print("  .tables     - List all tables")
        print()
        print("SQL Commands:")
        print("-" * 40)
        print("  CREATE TABLE ...")
        print("  INSERT INTO ...")
        print("  SELECT ... FROM ...")
        print("  UPDATE ... SET ...")
        print("  DELETE FROM ...")
        print()

    def _display_results(self, results: list) -> None:
        """Display query results in table format."""
        if not results:
            return

        print()
        print(f"Returned {len(results)} row(s):")
        print("-" * 40)

        for i, row in enumerate(results, 1):
            print(f"{i}: {row}")


def main():
    """Main entry point."""
    if len(sys.argv) < 2:
        print("Usage: python sql_shell.py <database_file>")
        sys.exit(1)

    db_path = sys.argv[1]

    try:
        shell = SQLShell(db_path)
        shell.run()
    except Exception as e:
        print(f"Fatal error: {e}")
        sys.exit(1)


if __name__ == "__main__":
    main()
