from datetime import datetime, timedelta
from fastapi import APIRouter, Depends
from sqlalchemy import func, select
from sqlalchemy.orm import Session

from backend.app.db.database import get_db
from backend.app.models.asset import Asset
from backend.app.models.audit_log import AuditLog
from backend.app.models.sync_record import SyncRecord

router = APIRouter(
    prefix="/api/v1/intelligence",
    tags=["Intelligence"]
)


def asset_summary(db: Session):
    total = db.scalar(select(func.count()).select_from(Asset)) or 0

    active = db.scalar(
        select(func.count()).select_from(Asset).where(
            func.lower(Asset.status) == "active"
        )
    ) or 0

    maintenance = db.scalar(
        select(func.count()).select_from(Asset).where(
            func.lower(Asset.status) == "maintenance"
        )
    ) or 0

    retired = db.scalar(
        select(func.count()).select_from(Asset).where(
            func.lower(Asset.status) == "retired"
        )
    ) or 0

    locations = db.scalar(
        select(func.count(func.distinct(Asset.location)))
    ) or 0

    types = db.scalar(
        select(func.count(func.distinct(Asset.asset_type)))
    ) or 0

    owners = db.scalar(
        select(func.count(func.distinct(Asset.owner)))
    ) or 0

    return {
        "total_assets": total,
        "active_assets": active,
        "maintenance_assets": maintenance,
        "retired_assets": retired,
        "locations": locations,
        "asset_types": types,
        "owners": owners
    }


def financial_summary(db: Session):
    rows = db.execute(
        select(Asset.purchase_value, Asset.current_value)
    ).all()

    purchase_total = 0.0
    current_total = 0.0

    for purchase_value, current_value in rows:
        if purchase_value is not None:
            purchase_total += float(purchase_value)
        if current_value is not None:
            current_total += float(current_value)

    value_change = current_total - purchase_total

    depreciation = max(purchase_total - current_total, 0.0)

    depreciation_percent = 0.0
    if purchase_total > 0:
        depreciation_percent = (depreciation / purchase_total) * 100

    return {
        "purchase_value_total": round(purchase_total, 2),
        "current_value_total": round(current_total, 2),
        "value_change": round(value_change, 2),
        "depreciation": round(depreciation, 2),
        "depreciation_percent": round(depreciation_percent, 2)
    }


def data_quality_summary(db: Session):
    assets = db.execute(select(Asset)).scalars().all()

    total = len(assets)

    required_fields = [
        "asset_code",
        "name",
        "asset_type",
        "status",
        "location",
        "owner"
    ]

    possible = total * len(required_fields)
    populated = 0

    for asset in assets:
        for field in required_fields:
            value = getattr(asset, field, None)
            if value is not None and str(value).strip() != "":
                populated += 1

    score = 100.0
    if possible > 0:
        score = (populated / possible) * 100

    missing_records = []

    for asset in assets:
        missing = []
        for field in required_fields:
            value = getattr(asset, field, None)
            if value is None or str(value).strip() == "":
                missing.append(field)

        if missing:
            missing_records.append({
                "asset_id": asset.id,
                "asset_code": asset.asset_code,
                "missing_fields": missing
            })

    return {
        "quality_score": round(score, 2),
        "total_assets_checked": total,
        "required_fields_checked": required_fields,
        "populated_fields": populated,
        "possible_fields": possible,
        "records_with_missing_data": len(missing_records),
        "missing_data": missing_records
    }


def synchronization_summary(db: Session):
    records = db.execute(
        select(SyncRecord).order_by(SyncRecord.id.desc())
    ).scalars().all()

    total = len(records)
    completed = 0
    failed = 0
    running = 0
    records_found = 0
    records_created = 0
    records_updated = 0
    records_failed = 0

    for record in records:
        status = (record.status or "").lower()

        if status in ("completed", "success", "successful"):
            completed += 1

        if status in ("failed", "error"):
            failed += 1

        if status in ("running", "started", "in_progress"):
            running += 1

        records_found += record.records_found or 0
        records_created += record.records_created or 0
        records_updated += record.records_updated or 0
        records_failed += record.records_failed or 0

    return {
        "total_sync_records": total,
        "completed": completed,
        "failed": failed,
        "running": running,
        "records_found": records_found,
        "records_created": records_created,
        "records_updated": records_updated,
        "records_failed": records_failed,
        "last_sync": (
            records[0].completed_at.isoformat()
            if records and records[0].completed_at
            else None
        )
    }


@router.get("/dashboard")
def intelligence_dashboard(db: Session = Depends(get_db)):
    assets = asset_summary(db)
    financial = financial_summary(db)
    quality = data_quality_summary(db)
    synchronization = synchronization_summary(db)

    audit_total = db.scalar(
        select(func.count()).select_from(AuditLog)
    ) or 0

    return {
        "application": "ATUL",
        "module": "Intelligence Command Center",
        "status": "online",
        "generated_at": datetime.utcnow().isoformat(),
        "assets": assets,
        "financial": financial,
        "data_quality": quality,
        "synchronization": synchronization,
        "audit_records": audit_total
    }


@router.get("/health")
def intelligence_health(db: Session = Depends(get_db)):
    asset_count = db.scalar(
        select(func.count()).select_from(Asset)
    ) or 0

    audit_count = db.scalar(
        select(func.count()).select_from(AuditLog)
    ) or 0

    sync_count = db.scalar(
        select(func.count()).select_from(SyncRecord)
    ) or 0

    return {
        "status": "healthy",
        "database": "healthy",
        "assets": asset_count,
        "audit_records": audit_count,
        "sync_records": sync_count,
        "checked_at": datetime.utcnow().isoformat()
    }


@router.get("/metrics")
def intelligence_metrics(db: Session = Depends(get_db)):
    assets = asset_summary(db)
    financial = financial_summary(db)
    quality = data_quality_summary(db)

    return {
        "status": "online",
        "asset_metrics": assets,
        "financial_metrics": financial,
        "quality_metrics": quality,
        "generated_at": datetime.utcnow().isoformat()
    }


@router.get("/data-quality")
def intelligence_data_quality(db: Session = Depends(get_db)):
    return {
        "status": "online",
        **data_quality_summary(db),
        "generated_at": datetime.utcnow().isoformat()
    }


@router.get("/financial")
def intelligence_financial(db: Session = Depends(get_db)):
    return {
        "status": "online",
        **financial_summary(db),
        "generated_at": datetime.utcnow().isoformat()
    }


@router.get("/synchronization")
def intelligence_synchronization(db: Session = Depends(get_db)):
    return {
        "status": "online",
        **synchronization_summary(db),
        "generated_at": datetime.utcnow().isoformat()
    }


@router.get("/assets")
def intelligence_assets(db: Session = Depends(get_db)):
    assets = db.execute(
        select(Asset).order_by(Asset.id.asc())
    ).scalars().all()

    items = []

    for asset in assets:
        items.append({
            "id": asset.id,
            "asset_code": asset.asset_code,
            "name": asset.name,
            "asset_type": asset.asset_type,
            "status": asset.status,
            "location": asset.location,
            "owner": asset.owner,
            "purchase_value": (
                float(asset.purchase_value)
                if asset.purchase_value is not None
                else None
            ),
            "current_value": (
                float(asset.current_value)
                if asset.current_value is not None
                else None
            ),
            "updated_at": (
                asset.updated_at.isoformat()
                if asset.updated_at
                else None
            )
        })

    return {
        "status": "online",
        "total": len(items),
        "assets": items,
        "generated_at": datetime.utcnow().isoformat()
    }
