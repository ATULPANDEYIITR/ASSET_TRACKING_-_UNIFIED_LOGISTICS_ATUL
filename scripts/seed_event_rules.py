import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

from backend.app.db.database import SessionLocal
from backend.app.models.automation_rule import AutomationRule

rules = [
    {
        "name": "Critical Event Alert",
        "description": "Generate an in-app notification for critical events.",
        "event_type": "*",
        "condition": {"severity": "critical"},
        "action": {
            "type": "notification",
            "channel": "in_app",
            "title": "Critical ATUL Alert",
            "message": "A critical event requires attention."
        },
        "severity": "critical"
    },
    {
        "name": "Asset Status Change",
        "description": "Monitor asset status changes.",
        "event_type": "asset.status_changed",
        "condition": {},
        "action": {
            "type": "notification",
            "channel": "in_app",
            "title": "Asset Status Changed",
            "message": "An asset status has changed."
        },
        "severity": "warning"
    },
    {
        "name": "Asset Created",
        "description": "Monitor newly created assets.",
        "event_type": "asset.created",
        "condition": {},
        "action": {
            "type": "notification",
            "channel": "in_app",
            "title": "New Asset Created",
            "message": "A new asset has been added to ATUL."
        },
        "severity": "info"
    },
    {
        "name": "Asset Updated",
        "description": "Monitor asset modifications.",
        "event_type": "asset.updated",
        "condition": {},
        "action": {
            "type": "notification",
            "channel": "in_app",
            "title": "Asset Updated",
            "message": "An asset record has been updated."
        },
        "severity": "info"
    },
    {
        "name": "Asset Deleted",
        "description": "Monitor asset deletion.",
        "event_type": "asset.deleted",
        "condition": {},
        "action": {
            "type": "notification",
            "channel": "in_app",
            "title": "Asset Deleted",
            "message": "An asset record has been deleted."
        },
        "severity": "warning"
    },
    {
        "name": "Synchronization Failure",
        "description": "Monitor failed synchronizations.",
        "event_type": "sync.failed",
        "condition": {},
        "action": {
            "type": "notification",
            "channel": "in_app",
            "title": "Synchronization Failed",
            "message": "An external synchronization failed."
        },
        "severity": "error"
    },
    {
        "name": "Source Offline",
        "description": "Monitor unavailable external sources.",
        "event_type": "source.offline",
        "condition": {},
        "action": {
            "type": "notification",
            "channel": "in_app",
            "title": "External Source Offline",
            "message": "A connected source is unavailable."
        },
        "severity": "error"
    },
    {
        "name": "Data Quality Warning",
        "description": "Monitor data quality problems.",
        "event_type": "data_quality.warning",
        "condition": {},
        "action": {
            "type": "notification",
            "channel": "in_app",
            "title": "Data Quality Warning",
            "message": "ATUL detected a data quality issue."
        },
        "severity": "warning"
    }
]

db = SessionLocal()

try:
    created = 0

    for item in rules:
        existing = (
            db.query(AutomationRule)
            .filter(
                AutomationRule.name == item["name"]
            )
            .first()
        )

        if existing is None:
            db.add(AutomationRule(**item))
            created += 1

    db.commit()

    total = db.query(AutomationRule).count()

    print("DEFAULT RULES CREATED:", created)
    print("TOTAL RULES:", total)

finally:
    db.close()
