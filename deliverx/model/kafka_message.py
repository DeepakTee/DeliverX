from typing import Optional
from pydantic import BaseModel

class KafkaMessage(BaseModel):
    id_: Optional[int] = -1
    priority: int
    content: dict
    type_: str