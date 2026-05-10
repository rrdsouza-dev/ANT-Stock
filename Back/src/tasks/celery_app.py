from celery import Celery

from src.core.config import config

settings = config()

celery_app = Celery(
    "ant_stock",
    broker=settings.broker_celery,
    backend=settings.backend_celery,
    include=["src.tasks.health"],
)
celery_app.conf.update(
    task_serializer="json",
    result_serializer="json",
    accept_content=["json"],
    timezone="America/Sao_Paulo",
    enable_utc=True,
)
