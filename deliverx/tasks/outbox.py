import asyncio

from deliverx.configuration.celery_app import celery_app
from deliverx.service.outbox import publish_retryable_outbox_events
from loguru import logger


@celery_app.task(name="deliverx.tasks.outbox.requeue_outbox_events")
def requeue_outbox_events() -> int:
    published_count = asyncio.run(publish_retryable_outbox_events())
    logger.info(f"Requeued {published_count} outbox events")
    return published_count
