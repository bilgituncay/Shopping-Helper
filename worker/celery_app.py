from celery import Celery
from celery.schedules import crontab

from shared.config import settings

celery_app = Celery(
    "shopper_helper",
    broker=settings.redis_url,
    backend=settings.redis_url,
    include=["worker.tasks"],
)

celery_app.conf.update(
    task_serializer="json",
    result_serializer="json",
    accept_content=["json"],
    timezone="UTC",
    enable_utc=True,
)

celery_app.conf.beat_schedule = {
    "refresh-all-prices-daily": {
        "task": "refresh_all_prices",
        "schedule": 60.0
    },
}