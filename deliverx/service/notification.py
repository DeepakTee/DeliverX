from sqlalchemy.ext.asyncio import AsyncSession

from deliverx.database.outbox_events import OutboxEvents
from deliverx.database.notification_channels import NotificationChannels
from deliverx.database.notifications import Notifications
from deliverx.model.messages import MessageRequest


class NotificationService:

    @staticmethod
    async def handle_notification_creation(
        session: AsyncSession, content: MessageRequest, user_id: str
    ) -> tuple[Notifications, list[int]]:
        notification = await Notifications.create(
            session=session,
            request_id=content.request_id,
            content=content.content,
            subscriptions=content.subscriptions,
            trigger_event=content.trigger_event,
            user_id=user_id,
        )

        channels: list[NotificationChannels] = await NotificationChannels.create_many(
            session=session,
            notification_id=notification.id_,
            channels=content.subscriptions,
        )
        mapped_channel_ids = {channel.channel: channel.id_ for channel in channels}
        outbox_event_ids: list[int] = []

        for channel in content.subscriptions:
            channel_id = mapped_channel_ids.get(channel)
            outbox_event = await OutboxEvents.create_outbox_event(
                session=session,
                notification_id=notification.id_,
                payload={
                    "id_": channel_id,
                    "priority": content.priority,
                    "content": content.content,
                    "type_": channel.value,
                },
            )
            outbox_event_ids.append(outbox_event.id_)

        return notification, outbox_event_ids
