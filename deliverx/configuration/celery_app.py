import os

from celery import Celery

celery_app = Celery(
    "deliverx",
    broker=os.getenv("CELERY_BROKER_URL", "redis://localhost:6379/0"),
    backend=os.getenv("CELERY_RESULT_BACKEND", "redis://localhost:6379/1"),
    include=["deliverx.tasks.outbox"],
)

celery_app.conf.beat_schedule = {
    "requeue-outbox-events-every-30-seconds": {
        "task": "deliverx.tasks.outbox.requeue_outbox_events",
        "schedule": 30.0,
    },
}
celery_app.conf.timezone = "UTC"
