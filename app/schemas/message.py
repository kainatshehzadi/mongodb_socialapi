from pydantic import BaseModel
from typing import Optional
from datetime import datetime

class MessageCreate(BaseModel):
    receiver_id: str
    text: str

class MessageResponse(BaseModel):
    id: str
    sender_id: str
    receiver_id: str
    text: str
    timestamp: datetime
