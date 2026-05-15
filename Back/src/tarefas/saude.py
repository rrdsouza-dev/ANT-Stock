from src.tarefas.celery import celery_app


@celery_app.task(name="saude")  # type: ignore[untyped-decorator]
def saude() -> str:
    return "ok"
