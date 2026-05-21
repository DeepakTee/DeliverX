from datetime import datetime

from deliverx.configuration.database import Base
from deliverx.constant.outbox import OutboxEventStatus
from sqlalchemy import Enum as SqlEnum
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import mapped_column, Mapped
from sqlalchemy.types import Integer, String, DateTime
from sqlalchemy.types import JSON


class OutboxEvents(Base):
    __tablename__ = "outbox_events"

    id_: Mapped[int] = mapped_column("id_outbox_event", Integer, primary_key=True)
    aggregate_id: Mapped[int] = mapped_column("id_aggregate", Integer, nullable=False)
    event_type: Mapped[str] = mapped_column("tx_event_type", String, nullable=False)
    payload: Mapped[dict] = mapped_column("js_payload", JSON, nullable=False)
    status: Mapped[OutboxEventStatus] = mapped_column(
        "tx_status",
        SqlEnum(
            OutboxEventStatus,
            name="outbox_event_status_enum",
            values_callable=lambda enum_cls: [item.value for item in enum_cls],
            create_type=True,
        ),
        nullable=False,
        default=OutboxEventStatus.PENDING,
    )
    created_at: Mapped[DateTime] = mapped_column(
        "ts_created_at", DateTime, nullable=False, default=datetime.now
    )
    published_at: Mapped[DateTime | None] = mapped_column(
        "ts_published_at", DateTime, nullable=True
    )

    @classmethod
    async def create_notification_created(
        cls,
        session: AsyncSession,
        notification_id: int,
        payload: dict,
    ) -> "OutboxEvents":
        outbox_event = cls(
            aggregate_id=notification_id,
            event_type="notification_created",
            payload=payload,
            status=OutboxEventStatus.PENDING,
            created_at=datetime.now(),
            published_at=None,
        )
        session.add(outbox_event)

        return outbox_event