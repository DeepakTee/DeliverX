from sqlalchemy.ext.asyncio import AsyncSession
from deliverx.database.notifications import Notifications
class Idempotency:

    @staticmethod
    async def is_already_served(session: AsyncSession, request_id: str) -> bool:
        notif = await Notifications.get_by_request_id(session, request_id=request_id)
        return bool(notif)