from pydantic import field_validator
from deliverx.constant.subscription import NotificationDeliveryMedium
from typing import List
from pydantic import BaseModel


class MessageRequest(BaseModel):
    request_id: str

    content: dict

    subscriptions: List[NotificationDeliveryMedium]
    trigger_event: str


    @field_validator("subscriptions", mode="before")
    @classmethod
    def validate_enum_name(cls, value):
        conv = []
        if isinstance(value, list):
            for v in value:
                try:
                    conv.append(NotificationDeliveryMedium[v])
                except KeyError:
                    raise ValueError(
                        f"Invalid enum name '{value}'. "
                        f"Allowed: {list(NotificationDeliveryMedium.__members__.keys())}"
                    )
        return conv
