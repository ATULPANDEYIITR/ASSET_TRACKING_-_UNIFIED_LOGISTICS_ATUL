from datetime import datetime

from fastapi import APIRouter, Depends
from sqlalchemy import text
from sqlalchemy.orm import Session

from backend.app.db.database import get_db
from backend.app.models.asset import Asset
from backend.app.models.audit_log import AuditLog
from backend.app.models.sync_record import SyncRecord

router = APIRouter()


@router.get("/overview")
def system_overview(
    db: Session = Depends(get_db),
):

    database = "healthy"

    try:

        db.execute(text("SELECT 1"))

    except Exception:

        database = "unhealthy"


    return {

        "application":
            "ATUL",

        "full_name":
            "Asset Tracking & Unified Logistics",

        "timestamp":
            datetime.utcnow(),

        "database":
            database,

        "asset_records":
            db.query(Asset).count(),

        "audit_records":
            db.query(AuditLog).count(),

        "sync_records":
            db.query(SyncRecord).count(),

        "backend":
            "FastAPI",

        "database_engine":
            "PostgreSQL",

        "automation":
            "Ready",

        "scraping":
            "Scrapy + Playwright",

        "status":
            "operational",

    }


@router.get("/metrics")
def system_metrics(
    db: Session = Depends(get_db),
):

    return {

        "assets":
            db.query(Asset).count(),

        "audit_logs":
            db.query(AuditLog).count(),

        "synchronizations":
            db.query(SyncRecord).count(),

        "completed_syncs":
            db.query(SyncRecord)
            .filter(
                SyncRecord.status == "completed"
            )
            .count(),

        "failed_syncs":
            db.query(SyncRecord)
            .filter(
                SyncRecord.status == "failed"
            )
            .count(),

        "running_syncs":
            db.query(SyncRecord)
            .filter(
                SyncRecord.status == "running"
            )
            .count(),

    }
