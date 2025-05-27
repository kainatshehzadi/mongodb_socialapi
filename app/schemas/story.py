from pydantic import BaseModel
from typing import Optional
from datetime import datetime

class StoryCreate(BaseModel):
    media_url: str
    caption: Optional[str] = None
