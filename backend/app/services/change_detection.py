import hashlib
import json


def calculate_hash(value):
    payload = json.dumps(
        value,
        sort_keys=True,
        ensure_ascii=False,
        default=str,
    )

    return hashlib.sha256(
        payload.encode("utf-8")
    ).hexdigest()


def has_changed(
    current_value,
    previous_hash,
):
    current_hash = calculate_hash(
        current_value
    )

    return (
        current_hash != previous_hash,
        current_hash,
    )
