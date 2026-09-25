import json
from pathlib import Path
from threading import Lock


PROJECT_ROOT = Path(__file__).resolve().parents[3]
CONFIG_DIR = PROJECT_ROOT / "config"
CONFIG_FILE = CONFIG_DIR / "sources.json"

_lock = Lock()


def _ensure_config():
    CONFIG_DIR.mkdir(
        parents=True,
        exist_ok=True,
    )

    if not CONFIG_FILE.exists():
        CONFIG_FILE.write_text(
            json.dumps(
                {"sources": []},
                indent=2,
            ),
            encoding="utf-8",
        )


def _load():
    _ensure_config()

    try:
        content = CONFIG_FILE.read_text(
            encoding="utf-8"
        )

        data = json.loads(content)

        if not isinstance(data, dict):
            return {"sources": []}

        if not isinstance(
            data.get("sources"),
            list,
        ):
            data["sources"] = []

        return data

    except Exception:
        return {"sources": []}


def _save(data):
    _ensure_config()

    CONFIG_FILE.write_text(
        json.dumps(
            data,
            indent=2,
            ensure_ascii=False,
        ),
        encoding="utf-8",
    )


def list_sources():
    with _lock:
        return _load().get(
            "sources",
            [],
        )


def get_source(source_id):
    for source in list_sources():
        if source.get("id") == source_id:
            return source

    return None


def add_source(source):
    with _lock:
        data = _load()

        sources = data.setdefault(
            "sources",
            [],
        )

        for existing in sources:
            if existing.get("id") == source.get("id"):
                raise ValueError(
                    "Source ID already exists."
                )

        sources.append(source)

        _save(data)

        return source


def update_source(
    source_id,
    updates,
):
    with _lock:
        data = _load()

        sources = data.setdefault(
            "sources",
            [],
        )

        for source in sources:
            if source.get("id") == source_id:
                source.update(updates)

                _save(data)

                return source

    return None


def delete_source(source_id):
    with _lock:
        data = _load()

        original = data.get(
            "sources",
            [],
        )

        filtered = [
            source
            for source in original
            if source.get("id") != source_id
        ]

        if len(filtered) == len(original):
            return False

        data["sources"] = filtered

        _save(data)

        return True


def source_count():
    return len(list_sources())
