from deliverx.constant.subscription import NotificationDeliveryMedium
from deliverx.constant.notification import NotificationChannelStatus
from deliverx.configuration.database import Base
from sqlalchemy.orm import mapped_column, Mapped
from sqlalchemy.types import Integer, String, DateTime
from sqlalchemy import Enum as SqlEnum, ForeignKey
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
        "channel",
        SqlEnum(
            NotificationDeliveryMedium,
            name="notification_delivery_medium_enum",
            create_type=False,
        ),
        nullable=False,
    )
    status: Mapped[NotificationChannelStatus] = mapped_column(
        "status",
        SqlEnum(
            NotificationChannelStatus,
            name="notification_channel_status_enum",
            values_callable=lambda enum_cls: [item.value for item in enum_cls],
            create_type=True,
        ),
        nullable=False,
        default=NotificationChannelStatus.PENDING,
    )
    attempt_count: Mapped[int] = mapped_column("attempt_count", Integer, default=0)
    last_error: Mapped[str | None] = mapped_column("last_error", String, nullable=True)
    sent_at: Mapped[DateTime | None] = mapped_column("sent_at", DateTime, nullable=True)
    created_at: Mapped[DateTime] = mapped_column("created_at", DateTime, default=datetime.now)
    updated_at: Mapped[DateTime] = mapped_column("updated_at", DateTime, default=datetime.now)