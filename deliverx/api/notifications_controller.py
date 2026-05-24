from deliverx.constant.api_payloads import SUCCESS
from deliverx.configuration.database import get_db_session
from fastapi import Depends
from typing import Dict
from deliverx.service.idempotency import Idempotency
from deliverx.service.notification import NotificationService
from fastapi import Header
from deliverx.model.messages import MessageRequest
from fastapi import APIRouter

router = APIRouter(prefix="/notifications")


@router.post("")
async def notification_dispatch(
    content: MessageRequest,
    user_id: str = Header(alias="x-user-id"),
    session=Depends(get_db_session),
) -> Dict:
    is_served = await Idempotency.is_already_served(session, content.request_id)
    if is_served:
        return SUCCESS

    result = await NotificationService.handle_notification_creation(session, content, user_id)

    
    return SUCCESS
