from datetime import datetime

from deliverx.configuration.database import Base
from deliverx.constant.outbox import OutboxEventStatus
from sqlalchemy import Enum as SqlEnum
from sqlalchemy.orm import mapped_column, Mapped
from sqlalchemy.types import Integer, String, DateTime
from sqlalchemy.types import JSON


class OutboxEvents(Base):
    __tablename__ = "outbox_events"

    id_: Mapped[int] = mapped_column("id_outbox_event", Integer, primary_key=True)
    aggregate_id: Mapped[int] = mapped_column("aggregate_id", Integer, nullable=False)
    event_type: Mapped[str] = mapped_column("event_type", String, nullable=False)
    payload: Mapped[dict] = mapped_column("payload", JSON, nullable=False)
    status: Mapped[OutboxEventStatus] = mapped_column(
        "status",
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
        "created_at", DateTime, nullable=False, default=datetime.now
    )
    published_at: Mapped[DateTime | None] = mapped_column(
        "published_at", DateTime, nullable=True
    )