from datetime import datetime, timedelta
from sqlalchemy import func
from backend.app.models.asset import Asset
from backend.app.models.audit_log import AuditLog
from backend.app.models.sync_record import SyncRecord


def build_dashboard(db):
    total_assets = db.query(func.count(Asset.id)).scalar() or 0

    active_assets = (
        db.query(func.count(Asset.id))
        .filter(Asset.status == "active")
        .scalar()
        or 0
    )

    maintenance_assets = (
        db.query(func.count(Asset.id))
        .filter(Asset.status == "maintenance")
        .scalar()
        or 0
    )

    inactive_assets = (
        db.query(func.count(Asset.id))
        .filter(Asset.status == "inactive")
        .scalar()
        or 0
    )

    locations = (
        db.query(func.count(func.distinct(Asset.location)))
        .filter(Asset.location.isnot(None))
        .scalar()
        or 0
    )

    owners = (
        db.query(func.count(func.distinct(Asset.owner)))
        .filter(Asset.owner.isnot(None))
        .scalar()
        or 0
    )

    types = (
        db.query(func.count(func.distinct(Asset.asset_type)))
        .filter(Asset.asset_type.isnot(None))
        .scalar()
        or 0
    )

    purchase_value = (
        db.query(func.coalesce(func.sum(Asset.purchase_value), 0))
        .scalar()
        or 0
    )

    current_value = (
        db.query(func.coalesce(func.sum(Asset.current_value), 0))
        .scalar()
        or 0
    )

    audit_total = db.query(func.count(AuditLog.id)).scalar() or 0
    sync_total = db.query(func.count(SyncRecord.id)).scalar() or 0

    sync_success = (
        db.query(func.count(SyncRecord.id))
        .filter(SyncRecord.status.in_(["success", "completed", "complete"]))
        .scalar()
        or 0
    )

    sync_failed = (
        db.query(func.count(SyncRecord.id))
        .filter(SyncRecord.status.in_(["failed", "error"]))
        .scalar()
        or 0
    )

    sync_running = (
        db.query(func.count(SyncRecord.id))
        .filter(SyncRecord.status.in_(["running", "syncing", "in_progress"]))
        .scalar()
        or 0
    )

    depreciation = float(purchase_value) - float(current_value)

    depreciation_percent = 0
    if float(purchase_value) > 0:
        depreciation_percent = (
            depreciation / float(purchase_value)
        ) * 100

    sync_success_rate = 0
    if sync_total > 0:
        sync_success_rate = (
            sync_success / sync_total
        ) * 100

    return {
        "generated_at": datetime.utcnow().isoformat(),

        "assets": {
            "total": total_assets,
            "active": active_assets,
            "maintenance": maintenance_assets,
            "inactive": inactive_assets,
            "locations": locations,
            "owners": owners,
            "types": types,
        },

        "financial": {
            "purchase_value": float(purchase_value),
            "current_value": float(current_value),
            "depreciation": depreciation,
            "depreciation_percent": round(depreciation_percent, 2),
        },

        "synchronization": {
            "total": sync_total,
            "successful": sync_success,
            "failed": sync_failed,
            "running": sync_running,
            "success_rate": round(sync_success_rate, 2),
        },

        "audit": {
            "total": audit_total,
        },

        "system": {
            "database": "healthy",
            "asset_store": "healthy",
            "audit_store": "healthy",
            "sync_store": "healthy",
            "status": "operational",
        },
    }


def build_health(db):
    asset_count = db.query(func.count(Asset.id)).scalar() or 0
    audit_count = db.query(func.count(AuditLog.id)).scalar() or 0
    sync_count = db.query(func.count(SyncRecord.id)).scalar() or 0

    return {
        "status": "healthy",
        "database": "healthy",
        "assets": asset_count,
        "audit_records": audit_count,
        "sync_records": sync_count,
        "timestamp": datetime.utcnow().isoformat(),
    }


def build_metrics(db):
    assets = db.query(Asset).all()

    total_purchase = sum(
        float(a.purchase_value or 0)
        for a in assets
    )

    total_current = sum(
        float(a.current_value or 0)
        for a in assets
    )

    missing_location = sum(
        1 for a in assets if not a.location
    )

    missing_owner = sum(
        1 for a in assets if not a.owner
    )

    missing_serial = sum(
        1 for a in assets if not a.serial_number
    )

    stale_threshold = datetime.utcnow() - timedelta(days=30)

    stale_assets = sum(
        1
        for a in assets
        if a.updated_at and a.updated_at < stale_threshold
    )

    return {
        "asset_count": len(assets),
        "total_purchase_value": total_purchase,
        "total_current_value": total_current,
        "value_change": total_current - total_purchase,
        "missing_location": missing_location,
        "missing_owner": missing_owner,
        "missing_serial_number": missing_serial,
        "stale_assets": stale_assets,
        "data_quality_score": calculate_quality_score(
            len(assets),
            missing_location,
            missing_owner,
            missing_serial,
        ),
    }


def calculate_quality_score(
    total,
    missing_location,
    missing_owner,
    missing_serial,
):
    if total == 0:
        return 100

    missing = (
        missing_location
        + missing_owner
        + missing_serial
    )

    score = 100 - ((missing / (total * 3)) * 100)

    return round(max(0, score), 2)
