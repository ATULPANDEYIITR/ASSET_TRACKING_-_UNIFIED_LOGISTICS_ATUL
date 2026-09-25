from datetime import datetime, timedelta

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from backend.app.db.database import get_db
from backend.app.models.event import Event
from backend.app.models.notification import Notification
from backend.app.models.automation_rule import AutomationRule

router = APIRouter(
    prefix="/api/v1/events",
    tags=["Events"]
)


def serialize_event(event):
    return {
        "id": event.id,
        "event_type": event.event_type,
        "title": event.title,
        "message": event.message,
        "severity": event.severity,
        "status": event.status,
        "source": event.source,
        "asset_id": event.asset_id,
        "asset_code": event.asset_code,
        "event_data": event.event_data,
        "acknowledged": event.acknowledged,
        "acknowledged_at": event.acknowledged_at,
        "resolved": event.resolved,
        "resolved_at": event.resolved_at,
        "created_at": event.created_at,
        "updated_at": event.updated_at
    }


def serialize_notification(notification):
    return {
        "id": notification.id,
        "event_id": notification.event_id,
        "notification_type": notification.notification_type,
        "title": notification.title,
        "message": notification.message,
        "severity": notification.severity,
        "read": notification.read,
        "read_at": notification.read_at,
        "notification_data": notification.notification_data,
        "created_at": notification.created_at
    }


def serialize_rule(rule):
    return {
        "id": rule.id,
        "name": rule.name,
        "description": rule.description,
        "event_type": rule.event_type,
        "condition": rule.condition,
        "action": rule.action,
        "severity": rule.severity,
        "enabled": rule.enabled,
        "execution_count": rule.execution_count,
        "last_executed_at": rule.last_executed_at,
        "created_at": rule.created_at,
        "updated_at": rule.updated_at
    }


def condition_matches(event, condition):
    if not condition:
        return True

    if not isinstance(condition, dict):
        return False

    for key, expected in condition.items():
        actual = getattr(event, key, None)

        if actual is None and isinstance(event.event_data, dict):
            actual = event.event_data.get(key)

        if actual != expected:
            return False

    return True


def execute_automation_rules(db, event):
    rules = (
        db.query(AutomationRule)
        .filter(AutomationRule.enabled.is_(True))
        .order_by(AutomationRule.id)
        .all()
    )

    executed = []
    notifications_created = []

    for rule in rules:
        if rule.event_type not in ("*", event.event_type):
            continue

        if not condition_matches(event, rule.condition):
            continue

        action = rule.action or {}
        action_type = action.get("type", "notification")

        rule.execution_count = (rule.execution_count or 0) + 1
        rule.last_executed_at = datetime.utcnow()

        if action_type == "notification":
            notification = Notification(
                event_id=event.id,
                notification_type=action.get("channel", "in_app"),
                title=action.get("title", event.title),
                message=action.get("message", event.message or ""),
                severity=rule.severity or event.severity,
                notification_data={
                    "rule_id": rule.id,
                    "rule_name": rule.name,
                    "event_type": event.event_type
                }
            )

            db.add(notification)
            db.flush()

            notifications_created.append(
                serialize_notification(notification)
            )

        executed.append({
            "rule_id": rule.id,
            "rule_name": rule.name,
            "action": action_type
        })

    return executed, notifications_created


@router.get("")
def list_events(
    limit: int = 100,
    offset: int = 0,
    severity: str | None = None,
    status: str | None = None,
    event_type: str | None = None,
    source: str | None = None,
    asset_code: str | None = None,
    db: Session = Depends(get_db)
):
    limit = max(1, min(limit, 500))
    offset = max(0, offset)

    query = db.query(Event)

    if severity:
        query = query.filter(Event.severity == severity)

    if status:
        query = query.filter(Event.status == status)

    if event_type:
        query = query.filter(Event.event_type == event_type)

    if source:
        query = query.filter(Event.source == source)

    if asset_code:
        query = query.filter(Event.asset_code == asset_code)

    total = query.count()

    rows = (
        query
        .order_by(Event.created_at.desc())
        .offset(offset)
        .limit(limit)
        .all()
    )

    return {
        "status": "online",
        "total": total,
        "offset": offset,
        "limit": limit,
        "events": [serialize_event(event) for event in rows]
    }


@router.post("")
def create_event(
    payload: dict,
    db: Session = Depends(get_db)
):
    if not payload.get("event_type"):
        raise HTTPException(
            status_code=400,
            detail="event_type is required"
        )

    if not payload.get("title"):
        raise HTTPException(
            status_code=400,
            detail="title is required"
        )

    event = Event(
        event_type=payload["event_type"],
        title=payload["title"],
        message=payload.get("message"),
        severity=payload.get("severity", "info"),
        status=payload.get("status", "open"),
        source=payload.get("source"),
        asset_id=payload.get("asset_id"),
        asset_code=payload.get("asset_code"),
        event_data=payload.get("event_data") or {}
    )

    try:
        db.add(event)
        db.flush()

        executed, notifications_created = execute_automation_rules(
            db,
            event
        )

        db.commit()
        db.refresh(event)

        return {
            "status": "created",
            "event": serialize_event(event),
            "automation_rules_executed": executed,
            "notifications_created": notifications_created
        }

    except Exception:
        db.rollback()
        raise


@router.get("/summary")
def event_summary(
    db: Session = Depends(get_db)
):
    total_events = db.query(Event).count()

    unread_notifications = (
        db.query(Notification)
        .filter(Notification.read.is_(False))
        .count()
    )

    unresolved_events = (
        db.query(Event)
        .filter(Event.resolved.is_(False))
        .count()
    )

    critical_events = (
        db.query(Event)
        .filter(Event.severity == "critical")
        .count()
    )

    error_events = (
        db.query(Event)
        .filter(Event.severity == "error")
        .count()
    )

    warning_events = (
        db.query(Event)
        .filter(Event.severity == "warning")
        .count()
    )

    info_events = (
        db.query(Event)
        .filter(Event.severity == "info")
        .count()
    )

    acknowledged_events = (
        db.query(Event)
        .filter(Event.acknowledged.is_(True))
        .count()
    )

    resolved_events = (
        db.query(Event)
        .filter(Event.resolved.is_(True))
        .count()
    )

    cutoff = datetime.utcnow() - timedelta(hours=24)

    events_last_24_hours = (
        db.query(Event)
        .filter(Event.created_at >= cutoff)
        .count()
    )

    notifications_total = db.query(Notification).count()

    automation_rules = db.query(AutomationRule).count()

    enabled_automation_rules = (
        db.query(AutomationRule)
        .filter(AutomationRule.enabled.is_(True))
        .count()
    )

    return {
        "status": "online",
        "total_events": total_events,
        "unread_notifications": unread_notifications,
        "unresolved_events": unresolved_events,
        "critical_events": critical_events,
        "error_events": error_events,
        "warning_events": warning_events,
        "info_events": info_events,
        "acknowledged_events": acknowledged_events,
        "resolved_events": resolved_events,
        "events_last_24_hours": events_last_24_hours,
        "notifications_total": notifications_total,
        "automation_rules": automation_rules,
        "enabled_automation_rules": enabled_automation_rules
    }


@router.get("/notifications")
def list_notifications(
    limit: int = 100,
    unread_only: bool = False,
    db: Session = Depends(get_db)
):
    limit = max(1, min(limit, 500))

    query = db.query(Notification)

    if unread_only:
        query = query.filter(Notification.read.is_(False))

    total = query.count()

    rows = (
        query
        .order_by(Notification.created_at.desc())
        .limit(limit)
        .all()
    )

    return {
        "status": "online",
        "total": total,
        "notifications": [
            serialize_notification(notification)
            for notification in rows
        ]
    }


@router.patch("/notifications/{notification_id}/read")
def mark_notification_read(
    notification_id: int,
    db: Session = Depends(get_db)
):
    notification = db.get(
        Notification,
        notification_id
    )

    if notification is None:
        raise HTTPException(
            status_code=404,
            detail="Notification not found"
        )

    notification.read = True
    notification.read_at = datetime.utcnow()

    db.commit()

    return {
        "status": "read",
        "notification_id": notification_id
    }


@router.post("/{event_id}/acknowledge")
def acknowledge_event(
    event_id: int,
    db: Session = Depends(get_db)
):
    event = db.get(Event, event_id)

    if event is None:
        raise HTTPException(
            status_code=404,
            detail="Event not found"
        )

    event.acknowledged = True
    event.acknowledged_at = datetime.utcnow()

    if event.status == "open":
        event.status = "acknowledged"

    db.commit()

    return {
        "status": "acknowledged",
        "event_id": event_id
    }


@router.post("/{event_id}/resolve")
def resolve_event(
    event_id: int,
    db: Session = Depends(get_db)
):
    event = db.get(Event, event_id)

    if event is None:
        raise HTTPException(
            status_code=404,
            detail="Event not found"
        )

    event.resolved = True
    event.resolved_at = datetime.utcnow()
    event.status = "resolved"

    db.commit()

    return {
        "status": "resolved",
        "event_id": event_id
    }


@router.get("/rules")
def list_rules(
    db: Session = Depends(get_db)
):
    rows = (
        db.query(AutomationRule)
        .order_by(AutomationRule.id)
        .all()
    )

    return {
        "status": "online",
        "total": len(rows),
        "rules": [serialize_rule(rule) for rule in rows]
    }


@router.post("/rules")
def create_rule(
    payload: dict,
    db: Session = Depends(get_db)
):
    if not payload.get("name"):
        raise HTTPException(
            status_code=400,
            detail="name is required"
        )

    existing = (
        db.query(AutomationRule)
        .filter(
            AutomationRule.name == payload["name"]
        )
        .first()
    )

    if existing:
        raise HTTPException(
            status_code=409,
            detail="Rule already exists"
        )

    rule = AutomationRule(
        name=payload["name"],
        description=payload.get("description"),
        event_type=payload.get("event_type", "*"),
        condition=payload.get("condition") or {},
        action=payload.get(
            "action",
            {
                "type": "notification",
                "channel": "in_app"
            }
        ),
        severity=payload.get("severity", "info"),
        enabled=payload.get("enabled", True)
    )

    try:
        db.add(rule)
        db.commit()
        db.refresh(rule)

        return {
            "status": "created",
            "rule": serialize_rule(rule)
        }

    except Exception:
        db.rollback()
        raise


@router.patch("/rules/{rule_id}")
def update_rule(
    rule_id: int,
    payload: dict,
    db: Session = Depends(get_db)
):
    rule = db.get(
        AutomationRule,
        rule_id
    )

    if rule is None:
        raise HTTPException(
            status_code=404,
            detail="Rule not found"
        )

    allowed = [
        "name",
        "description",
        "event_type",
        "condition",
        "action",
        "severity",
        "enabled"
    ]

    for field in allowed:
        if field in payload:
            setattr(rule, field, payload[field])

    try:
        db.commit()
        db.refresh(rule)

        return {
            "status": "updated",
            "rule": serialize_rule(rule)
        }

    except Exception:
        db.rollback()
        raise


@router.delete("/rules/{rule_id}")
def delete_rule(
    rule_id: int,
    db: Session = Depends(get_db)
):
    rule = db.get(
        AutomationRule,
        rule_id
    )

    if rule is None:
        raise HTTPException(
            status_code=404,
            detail="Rule not found"
        )

    db.delete(rule)
    db.commit()

    return {
        "status": "deleted",
        "rule_id": rule_id
    }
