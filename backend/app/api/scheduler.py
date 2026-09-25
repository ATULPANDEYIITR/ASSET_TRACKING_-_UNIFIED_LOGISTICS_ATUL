from fastapi import APIRouter

from backend.app.tasks.scheduler import (
    scheduler_status,
)

router = APIRouter()


@router.get("/scheduler")
def get_scheduler_status():
    return scheduler_status()
