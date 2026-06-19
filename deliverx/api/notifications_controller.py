from deliverx.constant.api_payloads import SUCCESS
from deliverx.configuration.database import get_db_session
from deliverx.service.outbox import publish_outbox_event
from fastapi import Depends
from typing import Dict
from deliverx.service.idempotency import Idempotency
from deliverx.service.notification import NotificationService
from fastapi import Header
from fastapi import BackgroundTasks
from deliverx.model.messages import MessageRequest
from fastapi import APIRouter

router = APIRouter(prefix="/notifications")


@router.post("")
async def notification_dispatch(
    content: MessageRequest,
    background_tasks: BackgroundTasks,
    user_id: str = Header(alias="x-user-id"),
    session=Depends(get_db_session),
) -> Dict:
    is_served = await Idempotency.is_already_served(session, content.request_id)
    if is_served:
        return SUCCESS

    _, outbox_event_ids = await NotificationService.handle_notification_creation(session, content, user_id)

    await session.commit()
    for outbox_event_id in outbox_event_ids:
        background_tasks.add_task(publish_outbox_event, outbox_event_id)

    return SUCCESS
