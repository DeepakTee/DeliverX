from datetime import datetime
from datetime import timedelta

from deliverx.configuration.database import AsyncPostgresSession
from deliverx.constant.outbox import OutboxEventStatus
from deliverx.constant.subscription import NotificationDeliveryMedium
from deliverx.database.outbox_events import OutboxEvents
from deliverx.model.kafka_message import KafkaMessage
from deliverx.producer.outbox_event import OutboxEvent
from loguru import logger

KAFKA_PRODUCER: OutboxEvent | None = None


def get_kafka_producer() -> OutboxEvent:
    global KAFKA_PRODUCER
    if KAFKA_PRODUCER is None:
        KAFKA_PRODUCER = OutboxEvent()
    return KAFKA_PRODUCER


async def publish_outbox_event(outbox_event_id: int) -> None:
    async with AsyncPostgresSession() as session:
        try:
            outbox_event = await OutboxEvents.get_by_id(session, outbox_event_id)
            if outbox_event is None or outbox_event.status == OutboxEventStatus.SENT:
                return

            claimed = await OutboxEvents.claim_for_publish(session, outbox_event_id)
            if not claimed:
                await session.rollback()
                return
            await session.commit()

            payload = outbox_event.payload
            priority = payload["priority"]
            kafka_message = KafkaMessage(**payload)

            get_kafka_producer().send_message(kafka_message, priority)

            await OutboxEvents.mark_sent(session, outbox_event_id)
            await session.commit()
        except Exception as exc:
            await session.rollback()
            logger.exception(f"Failed to publish outbox event {outbox_event_id}")
            async with AsyncPostgresSession() as failure_session:
                await OutboxEvents.mark_failed(
                    failure_session,
                    outbox_event_id,
                    str(exc),
                    datetime.now() + timedelta(seconds=30),
                )
                await failure_session.commit()


async def publish_retryable_outbox_events(limit: int = 100) -> int:
    async with AsyncPostgresSession() as session:
        events = await OutboxEvents.get_retryable_events(session, limit=limit)

    for event in events:
        await publish_outbox_event(event.id_)

    return len(events)
