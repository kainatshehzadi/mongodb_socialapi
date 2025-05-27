from pydantic import BaseModel
from bson import ObjectId

class LikeResponse(BaseModel):
    message: str
    post_id: str
