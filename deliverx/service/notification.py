from sqlalchemy.ext.asyncio import AsyncSession

from deliverx.database.notification_channels import NotificationChannels
from deliverx.database.notifications import Notifications
from deliverx.database.outbox_events import OutboxEvents
from deliverx.model.messages import MessageRequest


class NotificationService:
    @staticmethod
    async def create_notification(
        session: AsyncSession, content: MessageRequest, user_id: int
    ) -> Notifications:
        notification = await Notifications.create(
            session=session,
            request_id=content.request_id,
            content=content.content,
            subscriptions=content.subscriptions,
            trigger_event=content.trigger_event,
            user_id=user_id,
        )

        await NotificationChannels.create_many(
            session=session,
            notification_id=notification.id_,
            channels=content.subscriptions,
        )
        await OutboxEvents.create_notification_created(
            session=session,
            notification_id=notification.id_,
            payload=content.content,
        )

        return notification
