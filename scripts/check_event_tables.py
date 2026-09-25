import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

from sqlalchemy import inspect
from backend.app.db.database import engine

required = [
    "assets",
    "audit_logs",
    "sync_records",
    "events",
    "notifications",
    "automation_rules"
]

inspector = inspect(engine)
existing = inspector.get_table_names()

print("DATABASE TABLE CHECK")

missing = []

for table in required:
    if table in existing:
        print("OK:", table)
    else:
        print("MISSING:", table)
        missing.append(table)

if missing:
    print("MISSING_COUNT:", len(missing))
    raise SystemExit(2)

print("ALL_REQUIRED_TABLES_EXIST")
