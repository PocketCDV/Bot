from celery import Celery
from celery.schedules import crontab

from config import Config

config = Config(_env_file=".env")


def create_worker() -> Celery:
    """
    Create a Celery worker for task management.

    :return: Celery worker instance.
    """

    celery = Celery(
        "worker",
        broker=config.rabbitmq_dsn.get_secret_value(),
        backend=config.result_backend_dsn,
        include=["app.celery.tasks", "app.celery.crons"],
    )

    celery.conf.update(
        task_time_limit=30,
        worker_max_tasks_per_child=None,
    )

    celery.conf.beat_schedule = {
        "cron_refresh_session": {
            "task": "refresh_session",
            "schedule": crontab(minute="5,15,25,35,45,55"),
        },
        "cron_refresh_home_page": {
            "task": "refresh_home_page",
            "schedule": crontab(minute="0,10,20,30,40,50"),
        },
        "cron_plan_notifications": {
            "task": "plan_notifications",
            "schedule": crontab(hour=2, minute=0),
        },
        "cron_dispatch_notifications": {
            "task": "dispatch_notifications",
            "schedule": crontab(minute="*/5"),
        },
    }

    return celery


# Main Celery worker
worker: Celery = create_worker()
