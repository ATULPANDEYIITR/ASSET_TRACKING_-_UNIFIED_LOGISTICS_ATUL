from sqlalchemy.orm import Session

from backend.app.models.audit_log import AuditLog


def serialize_asset(asset):

    if asset is None:
        return None

    return {
        "id": asset.id,
        "asset_code": asset.asset_code,
        "name": asset.name,
        "asset_type": asset.asset_type,
        "serial_number": asset.serial_number,
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
        "description": asset.description,
    }


def write_audit(
    db: Session,
    action: str,
    asset=None,
    old_data=None,
    new_data=None,
    description=None,
    source="ATUL API",
):

    record = AuditLog(
        action=action,
        entity_type="asset",
        entity_id=asset.id if asset else None,
        asset_code=asset.asset_code if asset else None,
        description=description,
        old_data=old_data,
        new_data=new_data,
        source=source,
    )

    db.add(record)

    return record
