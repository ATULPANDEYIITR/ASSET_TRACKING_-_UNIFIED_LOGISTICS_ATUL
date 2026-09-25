import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

from backend.app.db.database import SessionLocal
from backend.app.models.event import Event
from backend.app.models.notification import Notification
from backend.app.models.automation_rule import AutomationRule

db = SessionLocal()

try:
    print("EVENT COUNT:", db.query(Event).count())
    print("NOTIFICATION COUNT:", db.query(Notification).count())
    print("RULE COUNT:", db.query(AutomationRule).count())
    print("DIRECT DATABASE ACCESS: OK")
finally:
    db.close()
