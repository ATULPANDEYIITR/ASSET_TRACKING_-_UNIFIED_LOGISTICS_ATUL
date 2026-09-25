from datetime import datetime

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from backend.app.db.database import get_db
from backend.app.models.sync_record import SyncRecord

router = APIRouter()


@router.get("")
def list_sync_records(
    limit: int = 100,
    db: Session = Depends(get_db),
):

    records = (
        db.query(SyncRecord)
        .order_by(SyncRecord.id.desc())
        .limit(min(limit, 1000))
        .all()
    )


    return {
        "records": [
            {
                "id": item.id,
                "source_name": item.source_name,
                "source_type": item.source_type,
                "status": item.status,
                "records_found": item.records_found,
                "records_created": item.records_created,
                "records_updated": item.records_updated,
                "records_failed": item.records_failed,
                "message": item.message,
                "started_at": item.started_at,
                "completed_at": item.completed_at,
            }
            for item in records
        ],
        "total": len(records),
    }


@router.post("")
def create_sync_record(
    source_name: str,
    source_type: str,
    db: Session = Depends(get_db),
):

    record = SyncRecord(
        source_name=source_name,
        source_type=source_type,
        status="running",
        started_at=datetime.utcnow(),
    )


    db.add(record)

    db.commit()

    db.refresh(record)


    return {
        "id": record.id,
        "status": record.status,
        "message": "Synchronization started."
    }


@router.put("/{sync_id}/complete")
def complete_sync(
    sync_id: int,
    status_value: str = "completed",
    records_found: int = 0,
    records_created: int = 0,
    records_updated: int = 0,
    records_failed: int = 0,
    message: str | None = None,
    db: Session = Depends(get_db),
):

    record = (
        db.query(SyncRecord)
        .filter(SyncRecord.id == sync_id)
        .first()
    )


    if not record:

        raise HTTPException(
            status_code=404,
            detail="Synchronization record not found."
        )


    record.status = status_value
    record.records_found = records_found
    record.records_created = records_created
    record.records_updated = records_updated
    record.records_failed = records_failed
    record.message = message
    record.completed_at = datetime.utcnow()


    db.commit()

    db.refresh(record)


    return {
        "id": record.id,
        "status": record.status,
        "completed_at": record.completed_at,
    }
