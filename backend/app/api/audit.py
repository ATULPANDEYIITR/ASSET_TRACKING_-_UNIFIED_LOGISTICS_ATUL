from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session

from backend.app.db.database import get_db
from backend.app.models.audit_log import AuditLog

router = APIRouter()


@router.get("")
def list_audit_logs(
    action: str | None = Query(None),
    asset_code: str | None = Query(None),
    limit: int = Query(100, ge=1, le=1000),
    db: Session = Depends(get_db),
):

    query = db.query(AuditLog)


    if action:

        query = query.filter(
            AuditLog.action == action.upper()
        )


    if asset_code:

        query = query.filter(
            AuditLog.asset_code == asset_code
        )


    records = (
        query
        .order_by(AuditLog.id.desc())
        .limit(limit)
        .all()
    )


    return {
        "records": [
            {
                "id": item.id,
                "action": item.action,
                "entity_type": item.entity_type,
                "entity_id": item.entity_id,
                "asset_code": item.asset_code,
                "description": item.description,
                "old_data": item.old_data,
                "new_data": item.new_data,
                "source": item.source,
                "created_at": item.created_at,
            }
            for item in records
        ],
        "total": len(records),
    }
