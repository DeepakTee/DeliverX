from deliverx.constant.api_payloads import SUCCESS
from deliverx.configuration.database import get_db_session
from fastapi import Depends
from typing import Dict
from deliverx.service.idempotency import Idempotency
from fastapi import Header
from deliverx.model.messages import MessageRequest
from fastapi import APIRouter

router = APIRouter(prefix="/notifications")


@router.post("")
async def notification_dispatch(
    content: MessageRequest,
    user_id: int = Header(alias="x-user-id"),
    session=Depends(get_db_session),
) -> Dict:
    is_served = await Idempotency.is_already_served(session, content.request_id)
    if is_served:
        return SUCCESS
    # TODO: impl below one
    return {"message": "Waiting for logic..."}
