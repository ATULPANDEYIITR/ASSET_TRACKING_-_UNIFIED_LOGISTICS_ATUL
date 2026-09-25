from datetime import datetime

from sqlalchemy.orm import Session

from backend.app.models.asset import Asset
from backend.app.services.audit_service import (
    serialize_asset,
    write_audit,
)

ASSET_FIELDS = [
    "asset_code",
    "name",
    "asset_type",
    "description",
    "serial_number",
    "status",
    "location",
    "owner",
    "purchase_value",
    "current_value",
]


def synchronize_assets(
    db: Session,
    records,
    source="AUTOMATION",
):
    created = 0
    updated = 0
    failed = 0

    for item in records:
        try:
            asset_code = item.get(
                "asset_code"
            )

            if not asset_code:
                failed += 1
                continue

            asset = (
                db.query(Asset)
                .filter(
                    Asset.asset_code
                    == str(asset_code)
                )
                .first()
            )

            if asset is None:
                values = {}

                for field in ASSET_FIELDS:
                    if field in item:
                        values[field] = item[field]

                values["asset_code"] = str(
                    asset_code
                )

                if "name" not in values:
                    values["name"] = str(
                        asset_code
                    )

                if "asset_type" not in values:
                    values["asset_type"] = "External"

                if "status" not in values:
                    values["status"] = "active"

                asset = Asset(
                    **values
                )

                db.add(asset)
                db.flush()

                write_audit(
                    db=db,
                    action="SYNC_CREATE",
                    asset=asset,
                    new_data=serialize_asset(
                        asset
                    ),
                    description=(
                        "Asset created by "
                        "external source synchronization."
                    ),
                    source=source,
                )

                created += 1
                continue

            old_data = serialize_asset(
                asset
            )

            changed = False

            for field in ASSET_FIELDS:
                if field not in item:
                    continue

                value = item[field]

                if field == "asset_code":
                    value = str(value)

                if getattr(
                    asset,
                    field,
                ) != value:
                    setattr(
                        asset,
                        field,
                        value,
                    )
                    changed = True

            if changed:
                asset.updated_at = (
                    datetime.utcnow()
                )

                db.flush()

                write_audit(
                    db=db,
                    action="SYNC_UPDATE",
                    asset=asset,
                    old_data=old_data,
                    new_data=serialize_asset(
                        asset
                    ),
                    description=(
                        "Asset updated by "
                        "external source synchronization."
                    ),
                    source=source,
                )

                updated += 1

        except Exception:
            failed += 1

    db.commit()

    return {
        "records_found": len(records),
        "records_created": created,
        "records_updated": updated,
        "records_failed": failed,
    }
