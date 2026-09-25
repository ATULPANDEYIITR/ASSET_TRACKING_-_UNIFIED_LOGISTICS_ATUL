from fastapi import APIRouter, HTTPException
from pydantic import BaseModel, Field

from backend.app.services.source_registry import (
    list_sources,
    get_source,
    add_source,
    update_source,
    delete_source,
)

from backend.app.services.integration_engine import (
    run_source,
    get_change_cache,
    clear_change_cache,
)

from backend.app.tasks.automation_runner import (
    run_all_sources,
)

router = APIRouter()


class SourceCreate(BaseModel):
    id: str = Field(
        min_length=1,
        max_length=100,
    )

    name: str = Field(
        min_length=1,
        max_length=255,
    )

    type: str = "http_json"
    url: str
    method: str = "GET"
    headers: dict = {}
    params: dict = {}
    timeout: int = 30
    enabled: bool = True
    schedule_minutes: int = 5
    asset_mapping: dict = {}


class SourceUpdate(BaseModel):
    name: str | None = None
    type: str | None = None
    url: str | None = None
    method: str | None = None
    headers: dict | None = None
    params: dict | None = None
    timeout: int | None = None
    enabled: bool | None = None
    schedule_minutes: int | None = None
    asset_mapping: dict | None = None


@router.get("/sources")
def get_sources():
    sources = list_sources()

    return {
        "sources": sources,
        "total": len(sources),
    }


@router.post("/sources")
def create_source(
    source: SourceCreate,
):
    try:
        result = add_source(
            source.model_dump()
        )

        return {
            "success": True,
            "source": result,
        }

    except ValueError as exc:
        raise HTTPException(
            status_code=409,
            detail=str(exc),
        )


@router.get("/sources/{source_id}")
def get_source_details(
    source_id: str,
):
    source = get_source(
        source_id
    )

    if source is None:
        raise HTTPException(
            status_code=404,
            detail="Source not found.",
        )

    return source


@router.put("/sources/{source_id}")
def modify_source(
    source_id: str,
    updates: SourceUpdate,
):
    result = update_source(
        source_id,
        updates.model_dump(
            exclude_unset=True
        ),
    )

    if result is None:
        raise HTTPException(
            status_code=404,
            detail="Source not found.",
        )

    return {
        "success": True,
        "source": result,
    }


@router.delete("/sources/{source_id}")
def remove_source(
    source_id: str,
):
    deleted = delete_source(
        source_id
    )

    if not deleted:
        raise HTTPException(
            status_code=404,
            detail="Source not found.",
        )

    return {
        "success": True,
        "message": "Source deleted.",
    }


@router.post("/run")
def run_automation():
    return {
        "success": True,
        "results": run_all_sources(),
    }


@router.post("/run/{source_id}")
def run_single_source(
    source_id: str,
):
    source = get_source(
        source_id
    )

    if source is None:
        raise HTTPException(
            status_code=404,
            detail="Source not found.",
        )

    return run_source(
        source
    )


@router.get("/changes")
def get_changes():
    return {
        "success": True,
        "cached_sources": get_change_cache(),
    }


@router.post("/changes/reset")
def reset_changes():
    clear_change_cache()

    return {
        "success": True,
        "message": "Change detection cache cleared.",
    }
