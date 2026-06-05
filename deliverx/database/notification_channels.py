from deliverx.constant.subscription import NotificationDeliveryMedium
from deliverx.constant.notification import NotificationChannelStatus
from deliverx.configuration.database import Base
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import mapped_column, Mapped
from sqlalchemy.types import Integer, String, DateTime
from sqlalchemy import Enum as SqlEnum, ForeignKey, select
from datetime import datetime


class NotificationChannels(Base):
    __tablename__ = "notification_channels"

    id_: Mapped[int] = mapped_column("id_notification_channel", Integer, primary_key=True)
    notification_id: Mapped[int] = mapped_column(
        "id_notification",
        ForeignKey("notifications.id_notification"),
        nullable=False,
    )
    channel: Mapped[NotificationDeliveryMedium] = mapped_column(
        "tx_channel",
        SqlEnum(
            NotificationDeliveryMedium,
            name="notification_delivery_medium_enum",
            create_type=False,
        ),
        nullable=False,
    )
    status: Mapped[NotificationChannelStatus] = mapped_column(
        "tx_status",
        SqlEnum(
            NotificationChannelStatus,
            name="notification_channel_status_enum",
            values_callable=lambda enum_cls: [item.value for item in enum_cls],
            create_type=True,
        ),
        nullable=False,
        default=NotificationChannelStatus.PENDING,
    )
    attempt_count: Mapped[int] = mapped_column("nu_attempt_count", Integer, default=0)
    last_error: Mapped[str | None] = mapped_column("tx_last_error", String, nullable=True)
    sent_at: Mapped[DateTime | None] = mapped_column("ts_sent_at", DateTime, nullable=True)
    created_at: Mapped[DateTime] = mapped_column("ts_created_at", DateTime, default=datetime.now)
    updated_at: Mapped[DateTime] = mapped_column("ts_updated_at", DateTime, default=datetime.now)

    @classmethod
    async def create_many(
        cls,
        session: AsyncSession,
        notification_id: int,
        channels: list[NotificationDeliveryMedium],
    ) -> list["NotificationChannels"]:
        notification_channels = [
            cls(
                notification_id=notification_id,
                channel=channel,
                status=NotificationChannelStatus.PENDING,
                attempt_count=0,
                last_error=None,
                sent_at=None,
            )
            for channel in channels
        ]

        session.add_all(notification_channels)
        await session.commit()

        return notification_channels

    @classmethod
    async def get_by_notification_ids(
        cls,
        session: AsyncSession,
        notification_ids: list[int],
    ) -> list["NotificationChannels"]:
        stmt = select(cls).where(cls.notification_id.in_(notification_ids))
        exec_result = await session.execute(stmt)
        result = exec_result.scalars().all()

        return result

    