from src.tasks.celery import celery_app


@celery_app.task(name="health.ping")  # type: ignore[untyped-decorator]
def testar() -> str:
    return "pong"
