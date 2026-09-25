import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

from backend.app.db.database import engine, Base

import backend.app.models.asset
import backend.app.models.audit_log
import backend.app.models.sync_record
import backend.app.models.event
import backend.app.models.notification
import backend.app.models.automation_rule

Base.metadata.create_all(bind=engine)

print("DATABASE TABLE CREATION: OK")

from sqlalchemy import inspect

inspector = inspect(engine)

required = [
    "assets",
    "audit_logs",
    "sync_records",
    "events",
    "notifications",
    "automation_rules"
]

tables = inspector.get_table_names()

for table in required:
    if table in tables:
        print("OK:", table)
    else:
        print("MISSING:", table)

missing = [table for table in required if table not in tables]

if missing:
    print("TABLE CREATION FAILED")
    print("MISSING:", missing)
    raise SystemExit(2)

print("ALL_EVENT_TABLES_READY")
