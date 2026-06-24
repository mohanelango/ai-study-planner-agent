from celery import Celery
from kombu import Queue

from app.core.config.settings import settings

celery_app = Celery(
    "ai_study_planner_agent",
    broker=settings.CELERY_BROKER_URL,
    backend=settings.CELERY_RESULT_BACKEND,
)

celery_app.conf.task_queues = (
    Queue("default"),
    Queue("documents"),
    Queue("embeddings"),
    Queue("ai"),
    Queue("planning"),
    Queue("notifications"),
)
celery_app.conf.task_default_queue = "default"
celery_app.conf.timezone = "UTC"


@celery_app.task(name="health.ping")
def health_ping() -> dict[str, str]:
    return {"status": "ok"}


from app.modules.documents.tasks import process_document  # noqa: E402,F401
