from bson import ObjectId
from pydantic import BaseModel, HttpUrl, Field
from typing import List, Optional
from datetime import datetime
from app.enum import PostVisibilityEnum

class PostCreate(BaseModel):
    content: str = Field(..., max_length=1000)
    image_url: Optional[HttpUrl] = None
    visibility: PostVisibilityEnum = PostVisibilityEnum.public

class PostResponse(BaseModel):
    id: str 
    user_id: str 
    content: str
    image_url: Optional[str] = None
    hashtags: List[str] = []
    visibility: PostVisibilityEnum
    created_at: datetime

    class Config:
        json_encoders = {ObjectId: str}

class PostUpdate(BaseModel):
    content: Optional[str]
    media_url: Optional[str]