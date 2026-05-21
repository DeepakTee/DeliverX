from sqlalchemy.sql import select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.types import ARRAY
from sqlalchemy.types import Text
from sqlalchemy.types import DateTime
from datetime import datetime
from deliverx.constant.notification import NotificationStatus
from deliverx.constant.subscription import NotificationDeliveryMedium
from sqlalchemy.orm import mapped_column, Mapped
from sqlalchemy.types import JSON
from deliverx.configuration.database import Base
from sqlalchemy import Integer, TIMESTAMP, Enum as SqlEnum


class Notifications(Base):
    __tablename__ = "notifications"

    id_: Mapped[int] = mapped_column("id_notification", Integer, primary_key=True)
    request_id: Mapped[str] = mapped_column("id_api_request", Text, unique=True)
    content: Mapped[dict] = mapped_column("js_content", JSON)
    type_: Mapped[list[NotificationDeliveryMedium]] = mapped_column(
        "arr_types",
        ARRAY(
            SqlEnum(
                NotificationDeliveryMedium,
                name="notification_delivery_medium_enum",
                create_type=True,
            )
        ),
        nullable=False,
        default=list,
    )
    trigger_event: Mapped[str] = mapped_column("tx_trigger_event", Text, nullable=True)
    status: Mapped[NotificationStatus] = mapped_column(
        "status",
        SqlEnum(
            NotificationStatus,
            name="notification_status_enum",
            values_callable=lambda enum_cls: [item.value for item in enum_cls],
            create_type=True,
        ),
        nullable=False,
        default=NotificationStatus.QUEUED,
    )
    created_on: Mapped[DateTime] = mapped_column(
        "ts_created_on", TIMESTAMP, default=datetime.now
    )
    user_id: Mapped[str] = mapped_column("id_user", Text, nullable=False)

    @classmethod
    async def create(
        cls,
        session: AsyncSession,
        request_id: str,
        content: dict,
        subscriptions: list[NotificationDeliveryMedium],
        trigger_event: str,
        user_id: int,
    ) -> "Notifications":
        notification = cls(
            request_id=request_id,
            content=content,
            type_=subscriptions,
            trigger_event=trigger_event,
            user_id=user_id,
            status=NotificationStatus.QUEUED,
        )
        session.add(notification)
        await session.flush()

        return notification

    @classmethod
    async def get_by_request_id(
        cls, session: AsyncSession, request_id: int
    ) -> "Notifications":
        stmt = select(cls).where(cls.request_id == request_id)
        exec_result = await session.execute(stmt)
        result = exec_result.scalars().all()

        return result
