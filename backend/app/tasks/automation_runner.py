from backend.app.services.source_registry import (
    list_sources,
)
from backend.app.services.integration_engine import (
    run_source,
)


def run_all_sources():
    results = []

    for source in list_sources():
        if not source.get(
            "enabled",
            True,
        ):
            continue

        try:
            result = run_source(
                source
            )

            results.append(result)

        except Exception as exc:
            results.append({
                "success": False,
                "source_id": source.get(
                    "id"
                ),
                "source_name": source.get(
                    "name"
                ),
                "error": str(exc),
            })

    return results
