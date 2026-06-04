from celery import Celery

from app.core.config import get_settings


settings = get_settings()
broker = settings.celery_broker_url or settings.redis_url
backend = settings.celery_result_backend or settings.redis_url

celery_app = Celery("heydoc", broker=broker, backend=backend)
celery_app.conf.update(
    task_serializer="json",
    result_serializer="json",
    accept_content=["json"],
    task_track_started=True,
    result_expires=3600,
    timezone="UTC",
    enable_utc=True,
)
