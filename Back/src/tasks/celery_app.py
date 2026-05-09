from celery import Celery

from src.core.config import get_settings

settings = get_settings()

celery_app = Celery(
    "ant_stock",
    broker=settings.celery_broker,
    backend=settings.celery_backend,
    include=["src.tasks.health"],
)
celery_app.conf.update(
    task_serializer="json",
    result_serializer="json",
    accept_content=["json"],
    timezone="America/Sao_Paulo",
    enable_utc=True,
)
