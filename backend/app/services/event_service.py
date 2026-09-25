from datetime import datetime
from sqlalchemy.orm import Session

from backend.app.models.system_event import SystemEvent
from backend.app.models.notification import Notification
from backend.app.models.automation_rule import AutomationRule


SEVERITIES = {
    "debug": 10,
    "info": 20,
    "success": 25,
    "warning": 30,
    "error": 40,
    "critical": 50,
}


def create_event(
    db: Session,
    event_type: str,
    title: str,
    message: str | None = None,
    severity: str = "info",
    entity_type: str | None = None,
    entity_id: int | None = None,
    asset_code: str | None = None,
    source: str = "ATUL",
    event_data: dict | None = None,
):
    event = SystemEvent(
        event_type=event_type,
        severity=severity,
        entity_type=entity_type,
        entity_id=entity_id,
        asset_code=asset_code,
        source=source,
        title=title,
        message=message,
        event_data=event_data or {},
    )

    db.add(event)
    db.flush()

    notification = Notification(
        notification_type="event",
        severity=severity,
        title=title,
        message=message or title,
        channel="in_app",
        event_id=event.id,
        notification_data=event_data or {},
    )

    db.add(notification)
    db.commit()
    db.refresh(event)

    return event


def acknowledge_event(db: Session, event_id: int):
    event = db.get(SystemEvent, event_id)

    if event is None:
        return None

    event.acknowledged = True
    db.commit()
    db.refresh(event)

    return event


def resolve_event(db: Session, event_id: int):
    event = db.get(SystemEvent, event_id)

    if event is None:
        return None

    event.resolved = True
    event.resolved_at = datetime.utcnow()

    db.commit()
    db.refresh(event)

    return event


def mark_notification_read(db: Session, notification_id: int):
    notification = db.get(Notification, notification_id)

    if notification is None:
        return None

    notification.read = True
    notification.read_at = datetime.utcnow()

    db.commit()
    db.refresh(notification)

    return notification


def condition_matches(event, condition):
    if not condition:
        return True

    if "severity" in condition:
        minimum = SEVERITIES.get(str(condition["severity"]).lower(), 20)
        current = SEVERITIES.get(str(event.severity).lower(), 20)

        if current < minimum:
            return False

    if "asset_code" in condition:
        if event.asset_code != condition["asset_code"]:
            return False

    if "source" in condition:
        if event.source != condition["source"]:
            return False

    return True


def execute_rule(db: Session, rule: AutomationRule, event):
    if not rule.enabled:
        return False

    if rule.event_type != event.event_type:
        return False

    if not condition_matches(event, rule.condition):
        return False

    action = rule.action or {}
    action_type = action.get("type", "notification")

    if action_type == "notification":
        notification = Notification(
            notification_type="automation",
            severity=rule.severity,
            title=action.get("title", rule.name),
            message=action.get(
                "message",
                f"Automation rule '{rule.name}' matched event {event.id}."
            ),
            channel=action.get("channel", "in_app"),
            event_id=event.id,
            notification_data={
                "rule_id": rule.id,
                "rule_name": rule.name,
                "event_id": event.id,
            },
        )

        db.add(notification)

    if action_type == "acknowledge":
        event.acknowledged = True

    if action_type == "resolve":
        event.resolved = True
        event.resolved_at = datetime.utcnow()

    rule.execution_count += 1
    rule.last_executed_at = datetime.utcnow()

    db.commit()

    return True


def process_event_rules(db: Session, event):
    rules = (
        db.query(AutomationRule)
        .filter(AutomationRule.enabled.is_(True))
        .all()
    )

    executed = 0

    for rule in rules:
        if execute_rule(db, rule, event):
            executed += 1

    return executed
