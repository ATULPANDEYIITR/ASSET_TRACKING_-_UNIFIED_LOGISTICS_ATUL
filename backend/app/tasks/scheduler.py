from apscheduler.schedulers.background import (
    BackgroundScheduler,
)

from backend.app.tasks.automation_runner import (
    run_all_sources,
)

scheduler = BackgroundScheduler(
    timezone="UTC"
)


def start_scheduler():
    if scheduler.running:
        return

    scheduler.add_job(
        run_all_sources,
        "interval",
        minutes=5,
        id="atul_global_sync",
        replace_existing=True,
        max_instances=1,
        coalesce=True,
    )

    scheduler.start()


def stop_scheduler():
    if scheduler.running:
        scheduler.shutdown(
            wait=False
        )


def scheduler_status():
    return {
        "running": scheduler.running,
        "jobs": [
            {
                "id": job.id,
                "next_run_time": (
                    job.next_run_time.isoformat()
                    if job.next_run_time
                    else None
                ),
            }
            for job in scheduler.get_jobs()
        ],
    }
