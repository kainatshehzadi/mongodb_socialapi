from pydantic import BaseModel, Field
from typing import List
from datetime import datetime


class CommentCreate(BaseModel):
    post_id: str
    text: str

class CommentResponse(BaseModel):
    id: str
    post_id: str
    user_id: str
    username: str
    text: str
    created_at: datetime
    
class CommentUpdate(BaseModel):
    content: str = Field(..., min_length=1, max_length=300)