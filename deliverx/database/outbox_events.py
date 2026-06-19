from datetime import datetime

from deliverx.configuration.database import Base
from deliverx.constant.outbox import OutboxEventStatus
from sqlalchemy import Enum as SqlEnum
from sqlalchemy import update
from sqlalchemy import select
from sqlalchemy import or_
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
    attempt_count: Mapped[int] = mapped_column("nu_attempt_count", Integer, default=0)
    last_error: Mapped[str | None] = mapped_column("tx_last_error", String, nullable=True)
    next_retry_at: Mapped[DateTime | None] = mapped_column(
        "ts_next_retry_at", DateTime, nullable=True
    )

    @classmethod
    async def create_outbox_event(
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
            attempt_count=0,
            last_error=None,
            next_retry_at=None,
        )
        session.add(outbox_event)
        await session.flush()

        return outbox_event

    @classmethod
    async def get_by_id(cls, session: AsyncSession, outbox_event_id: int) -> "OutboxEvents | None":
        stmt = select(cls).where(cls.id_ == outbox_event_id)
        exec_result = await session.execute(stmt)
        return exec_result.scalar_one_or_none()

    @classmethod
    async def claim_for_publish(cls, session: AsyncSession, outbox_event_id: int) -> bool:
        stmt = (
            update(cls)
            .where(
                cls.id_ == outbox_event_id,
                cls.status.in_(
                    [
                        OutboxEventStatus.PENDING,
                        OutboxEventStatus.FAILED,
                        OutboxEventStatus.RETRYING,
                    ]
                ),
            )
            .values(status=OutboxEventStatus.PROCESSING)
        )
        result = await session.execute(stmt)
        return result.rowcount == 1

    @classmethod
    async def mark_sent(cls, session: AsyncSession, outbox_event_id: int) -> None:
        stmt = (
            update(cls)
            .where(cls.id_ == outbox_event_id)
            .values(
                status=OutboxEventStatus.SENT,
                published_at=datetime.now(),
                last_error=None,
                next_retry_at=None,
            )
        )
        await session.execute(stmt)

    @classmethod
    async def mark_failed(
        cls,
        session: AsyncSession,
        outbox_event_id: int,
        error: str,
        next_retry_at: datetime | None = None,
    ) -> None:
        outbox_event = await cls.get_by_id(session, outbox_event_id)
        if outbox_event is None:
            return

        outbox_event.status = OutboxEventStatus.FAILED
        outbox_event.attempt_count += 1
        outbox_event.last_error = error
        outbox_event.next_retry_at = next_retry_at

    @classmethod
    async def get_retryable_events(
        cls,
        session: AsyncSession,
        limit: int = 100,
    ) -> list["OutboxEvents"]:
        now = datetime.now()
        stmt = (
            select(cls)
            .where(
                cls.status.in_([OutboxEventStatus.PENDING, OutboxEventStatus.FAILED]),
                or_(cls.next_retry_at.is_(None), cls.next_retry_at <= now),
            )
            .order_by(cls.created_at)
            .limit(limit)
        )
        exec_result = await session.execute(stmt)
        return list(exec_result.scalars().all())
