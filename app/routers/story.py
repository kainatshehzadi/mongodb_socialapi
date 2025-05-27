from fastapi import APIRouter, Depends, HTTPException
from app.schemas.story import StoryCreate
from app.depends import get_current_user
from datetime import datetime, timedelta, timezone
from bson import ObjectId
from app.db.database import db
router = APIRouter(prefix="/stories", tags=["Stories"])

@router.post("/")
async def create_story(payload: StoryCreate, current_user: dict = Depends(get_current_user)):
    story = {
        "user_id": current_user["_id"],
        "media_url": payload.media_url,
        "caption": payload.caption,
        "created_at": datetime.utcnow(),
        "expires_at": datetime.utcnow() + timedelta(hours=24)
    }

    await db["stories"].insert_one(story)
    return {"msg": "Story uploaded."}

@router.get("/feed")
async def get_active_stories():
    now = datetime.now(timezone.utc)
    cursor = db["stories"].find({"expires_at": {"$gt": now}})
    stories = [dict(s, id=str(s["_id"]), user_id=str(s["user_id"])) async for s in cursor]
    return stories
