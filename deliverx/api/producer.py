from deliverx.constant.api_payloads import SUCCESS
from deliverx.configuration.database import get_db_session
from fastapi import Depends
from typing import Dict
from deliverx.service.idempotency import Idempotency
from fastapi import Header
from deliverx.model.messages import MessageRequest
from fastapi import APIRouter
from deliverx.database.notifications import Notifications
from deliverx.database.notification_channels import NotificationChannels
from deliverx.database.outbox_events import OutboxEvents
from deliverx.constant.outbox import OutboxEventStatus
from deliverx.constant.notification import NotificationChannelStatus, NotificationStatus
from datetime import datetime
from loguru import logger
router = APIRouter(prefix="/notifications")


@router.post("")
async def notification_dispatch(
    content: MessageRequest,
    user_id: int = Header(alias="x-user-id"),
    session=Depends(get_db_session),
) -> Dict:
    is_served = await Idempotency.is_already_served(session, content.request_id)
    if is_served:
        logger.info(
            "Skipping duplicate notification request: request_id={}",
            content.request_id,
        )
        return SUCCESS

    try:
        logger.info(
            "Creating notification: request_id={} user_id={} channels={}",
            content.request_id,
            user_id,
            content.subscriptions,
        )

        notification = Notifications(
            request_id=content.request_id,
            content=content.content,
            type_=content.subscriptions,
            trigger_event=content.trigger_event,
            user_id=user_id,
            status=NotificationStatus.QUEUED,
        )
        session.add(notification)
        await session.commit()

        logger.debug(
            "Notification persisted: request_id={} notification_id={}",
            content.request_id,
            notification.id_,
        )

        for subscription in content.subscriptions:
            logger.debug(
                "Creating notification channel: notification_id={} channel={}",
                notification.id_,
                subscription,
            )
            notification_channel = NotificationChannels(
                notification_id=notification.id_,
                channel=subscription,
                status=NotificationChannelStatus.PENDING,
                attempt_count=0,
                last_error=None,
                sent_at=None,
            )
            session.add(notification_channel)
            await session.commit()

        outbox_event = OutboxEvents(
            aggregate_id=notification.id_,
            event_type="notification_created",
            payload=content.content,
            status=OutboxEventStatus.PENDING,
            created_at=datetime.now(),
            published_at=None,
        )
        session.add(outbox_event)
        logger.info(
            "Queued notification outbox event: request_id={} notification_id={}",
            content.request_id,
            notification.id_,
        )
    except Exception:
        logger.exception(
            "Failed to dispatch notification: request_id={} user_id={}",
            content.request_id,
            user_id,
        )
        raise

    return SUCCESS

