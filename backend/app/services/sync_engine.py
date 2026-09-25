from datetime import datetime

from backend.app.db.database import SessionLocal
from backend.app.models.sync_record import SyncRecord
from backend.app.services.http_connector import fetch_url
from backend.app.services.change_detection import calculate_hash
from backend.app.services.asset_sync_service import (
    synchronize_assets,
)


def run_source(source):

    db = SessionLocal()

    sync = SyncRecord(
        source_name=source.get(
            "name",
            source.get("id", "Unknown"),
        ),
        source_type=source.get(
            "type",
            "http",
        ),
        status="running",
        started_at=datetime.utcnow(),
    )

    db.add(sync)
    db.commit()
    db.refresh(sync)

    try:

        response = fetch_url(
            source["url"],
            method=source.get(
                "method",
                "GET",
            ),
            headers=source.get(
                "headers",
                {},
            ),
            params=source.get(
                "params",
                {},
            ),
            timeout=source.get(
                "timeout",
                30,
            ),
        )

        data = response.get("data")

        if data is None:
            data = {
                "content": response.get(
                    "text",
                    "",
                )
            }

        sync_hash = calculate_hash(
            data
        )

        records = []

        if isinstance(data, list):
            records = data

        elif isinstance(data, dict):

            candidate_keys = [
                "assets",
                "records",
                "data",
                "items",
            ]

            for key in candidate_keys:

                value = data.get(key)

                if isinstance(value, list):
                    records = value
                    break

        if records:

            result = synchronize_assets(
                db=db,
                records=records,
                source=source.get(
                    "name",
                    "AUTOMATION",
                ),
            )

        else:

            result = {
                "records_found": 0,
                "records_created": 0,
                "records_updated": 0,
                "records_failed": 0,
            }

        sync.status = "completed"

        sync.records_found = result[
            "records_found"
        ]

        sync.records_created = result[
            "records_created"
        ]

        sync.records_updated = result[
            "records_updated"
        ]

        sync.records_failed = result[
            "records_failed"
        ]

        sync.message = (
            f"HTTP {response['status_code']} | "
            f"SHA256 {sync_hash}"
        )

        sync.completed_at = (
            datetime.utcnow()
        )

        db.commit()

        return {
            "success": True,
            "sync_id": sync.id,
            "status": sync.status,
            **result,
        }

    except Exception as exc:

        sync.status = "failed"

        sync.message = str(exc)

        sync.completed_at = (
            datetime.utcnow()
        )

        db.commit()

        return {
            "success": False,
            "sync_id": sync.id,
            "status": "failed",
            "error": str(exc),
        }

    finally:
        db.close()
