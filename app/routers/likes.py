from fastapi import APIRouter, Depends, HTTPException, status
from bson import ObjectId
from app.depends import get_current_user
from app.db.database import db
from app.schemas import likes
from app.utils.onesignal import send_onesignal_notification
from app.schemas.likes import LikeResponse
from app.utils.onesignal import send_onesignal_notification

router = APIRouter(prefix="/posts", tags=["Likes"])

@router.post("/{post_id}/", response_model=LikeResponse)
async def like_post(post_id: str, current_user: dict = Depends(get_current_user)):
    user_id = str(current_user["_id"])

    post = await db["posts"].find_one({"_id": ObjectId(post_id)})
    if not post:
        raise HTTPException(status_code=404, detail="Post not found.")

    existing_like = await db["likes"].find_one({
        "post_id": ObjectId(post_id),
        "user_id": ObjectId(user_id)
    })
    if existing_like:
        raise HTTPException(status_code=400, detail="You already liked this post.")

    await db["likes"].insert_one({
        "post_id": ObjectId(post_id),
        "user_id": ObjectId(user_id)
    })

    # Send OneSignal notification to the post author (if not liking their own post)
    if str(post["user_id"]) != user_id:
        await send_onesignal_notification(
            user_id=str(post["author_id"]),
            heading="New Like",
            message=f"{current_user['username']} liked your post!"
        )

    return {"message": "Post liked successfully.", "post_id": post_id}

@router.delete("/{post_id}/", response_model=LikeResponse)
async def unlike_post(post_id: str, current_user: dict = Depends(get_current_user)):
    user_id = str(current_user["_id"])

    # Delete like if exists
    result = await db["likes"].delete_one({
        "post_id": ObjectId(post_id),
        "user_id": ObjectId(user_id)
    })

    if result.deleted_count == 0:
        raise HTTPException(status_code=404, detail="Like not found.")

    return {"message": "Post unliked successfully.", "post_id": post_id}
