from celery import Celery

from src.nucleo.configuracao import configuracao

config = configuracao()

celery_app = Celery(
    "ant",
    broker=config.broker_celery,
    backend=config.backend_celery,
    include=["src.tarefas.saude"],
)
celery_app.conf.update(
    task_serializer="json",
    result_serializer="json",
    accept_content=["json"],
    timezone="America/Sao_Paulo",
    enable_utc=True,
)
