import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

from sqlalchemy import inspect
from backend.app.db.database import engine

inspector = inspect(engine)

expected = {
    "events": [
        "id",
        "event_type",
        "title",
        "message",
        "severity",
        "status",
        "source",
        "asset_id",
        "asset_code",
        "event_data",
        "acknowledged",
        "acknowledged_at",
        "resolved",
        "resolved_at",
        "created_at",
        "updated_at"
    ],
    "notifications": [
        "id",
        "event_id",
        "notification_type",
        "title",
        "message",
        "severity",
        "read",
        "read_at",
        "notification_data",
        "created_at"
    ],
    "automation_rules": [
        "id",
        "name",
        "description",
        "event_type",
        "condition",
        "action",
        "severity",
        "enabled",
        "execution_count",
        "last_executed_at",
        "created_at",
        "updated_at"
    ]
}

failed = False

for table, columns in expected.items():
    actual = [column["name"] for column in inspector.get_columns(table)]

    print("")
    print("TABLE:", table)

    for column in columns:
        if column in actual:
            print(" OK:", column)
        else:
            print(" MISSING:", column)
            failed = True

if failed:
    print("")
    print("COLUMN VERIFICATION FAILED")
    raise SystemExit(2)

print("")
print("COLUMN VERIFICATION: OK")
