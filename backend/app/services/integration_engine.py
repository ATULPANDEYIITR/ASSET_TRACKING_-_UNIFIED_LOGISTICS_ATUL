from datetime import datetime

from backend.app.db.database import SessionLocal
from backend.app.models.sync_record import SyncRecord
from backend.app.services.http_connector import fetch_http
from backend.app.services.change_detection import (
    calculate_hash,
)
from backend.app.services.data_mapper import map_records
from backend.app.services.asset_sync_service import (
    synchronize_assets,
)

_last_hashes = {}


def _extract_records(data):
    if isinstance(data, list):
        return data

    if isinstance(data, dict):
        for key in [
            "assets",
            "records",
            "data",
            "items",
            "results",
        ]:
            value = data.get(key)

            if isinstance(value, list):
                return value

    return []


def run_source(source):
    db = SessionLocal()

    sync = SyncRecord(
        source_name=source.get(
            "name",
            source.get(
                "id",
                "Unknown",
            ),
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
        response = fetch_http(
            url=source["url"],
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
            retries=3,
        )

        data = response.get(
            "data"
        )

        if data is None:
            data = {
                "content": response.get(
                    "text",
                    "",
                )
            }

        current_hash = calculate_hash(
            data
        )

        previous_hash = _last_hashes.get(
            source["id"]
        )

        changed = (
            previous_hash != current_hash
        )

        _last_hashes[
            source["id"]
        ] = current_hash

        raw_records = _extract_records(
            data
        )

        records = map_records(
            raw_records,
            source.get(
                "asset_mapping",
                {},
            ),
        )

        result = {
            "records_found": len(records),
            "records_created": 0,
            "records_updated": 0,
            "records_failed": 0,
        }

        if changed and records:
            result = synchronize_assets(
                db=db,
                records=records,
                source=source.get(
                    "name",
                    "AUTOMATION",
                ),
            )

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
            f"CHANGED={changed} | "
            f"SHA256={current_hash}"
        )

        sync.completed_at = (
            datetime.utcnow()
        )

        db.commit()

        return {
            "success": True,
            "sync_id": sync.id,
            "source_id": source.get(
                "id"
            ),
            "source_name": source.get(
                "name"
            ),
            "status": sync.status,
            "changed": changed,
            "hash": current_hash,
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
            "source_id": source.get(
                "id"
            ),
            "source_name": source.get(
                "name"
            ),
            "status": "failed",
            "error": str(exc),
        }

    finally:
        db.close()


def clear_change_cache():
    _last_hashes.clear()


def get_change_cache():
    return dict(
        _last_hashes
    )
