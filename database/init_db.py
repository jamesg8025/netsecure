"""Create an empty database without overwriting an existing one."""
from pathlib import Path
import sqlite3

root = Path(__file__).resolve().parent
path = root / "netsecure.db"
if path.exists():
    raise SystemExit("netsecure.db already exists; no changes made.")

try:
    with sqlite3.connect(path) as db:
        db.executescript((root / "schema.sql").read_text())
finally:
    if "db" in locals():
        db.close()
print("Created", path)
