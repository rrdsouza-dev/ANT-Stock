from src.tarefas.celery import celery_app


@celery_app.task(name="saude")
def saude() -> str:
    return "ok"
