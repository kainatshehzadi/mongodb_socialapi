from datetime import datetime, timezone
from typing import List
from fastapi import APIRouter, Body, HTTPException, Depends
from bson import ObjectId
from app.db.database import db
from app.depends import get_current_user
from app.schemas.comments import CommentCreate, CommentResponse, CommentUpdate
from app.utils.onesignal import send_onesignal_notification


router = APIRouter(prefix="/comments", tags=["Comments"])



@router.post("/", response_model=CommentResponse)
async def add_comment(payload: CommentCreate, current_user: dict = Depends(get_current_user)):
    post = await db["posts"].find_one({"_id": ObjectId(payload.post_id)})
    if not post:
        raise HTTPException(status_code=404, detail="Post not found.")

    comment = {
        "post_id": ObjectId(payload.post_id),
        "user_id": current_user["_id"],
        "username": current_user["username"],
        "text": payload.text,
        "created_at": datetime.now(timezone.utc)
    }

    result = await db["comments"].insert_one(comment)
    comment["id"] = str(result.inserted_id)

    # OneSignal Notification to post author
    if str(post["user_id"]) != str(current_user["_id"]):
        await send_onesignal_notification(
            user_id=str(post["author_id"]),
            heading="New Comment",
            message=f"{current_user['username']} commented on your post."
        )

    # Convert ObjectIds to string before returning
    comment["post_id"] = str(comment["post_id"])
    comment["user_id"] = str(comment["user_id"])

    return comment

@router.get("/{post_id}", response_model=List[CommentResponse])
async def get_comments(post_id: str):
    comments_cursor = db["comments"].find({"post_id": ObjectId(post_id)}).sort("created_at", -1)
    comments = []
    async for c in comments_cursor:
        comments.append({
            "id": str(c["_id"]),
            "post_id": str(c["post_id"]),
            "user_id": str(c["user_id"]),
            "username": c["username"],
            "text": c["text"],
            "created_at": c["created_at"]
        })
    return comments



@router.delete("/{comment_id}")
async def delete_comment(comment_id: str, current_user: dict = Depends(get_current_user)):
    comment = await db["comments"].find_one({"_id": ObjectId(comment_id)})
    if not comment:
        raise HTTPException(status_code=404, detail="Comment not found.")

    if str(comment["user_id"]) != str(current_user["_id"]):
        raise HTTPException(status_code=403, detail="You can delete only your comment.")

    await db["comments"].delete_one({"_id": ObjectId(comment_id)})
    return {"msg": "Comment deleted successfully."}

@router.put("/{comment_id}", response_model=CommentResponse)
async def update_comment(
    comment_id: str,
    payload: CommentUpdate,
    current_user: dict = Depends(get_current_user)
):
    comment = await db["comments"].find_one({"_id": ObjectId(comment_id)})
    if not comment:
        raise HTTPException(status_code=404, detail="Comment not found.")

    if str(comment["user_id"]) != str(current_user["_id"]):
        raise HTTPException(status_code=403, detail="You can update only your own comment.")

    updated_data = {
        "text": payload.content,
        "created_at": datetime.now(timezone.utc)
    }

    await db["comments"].update_one({"_id": ObjectId(comment_id)}, {"$set": updated_data})

    updated_comment = await db["comments"].find_one({"_id": ObjectId(comment_id)})
    return {
        "id": str(updated_comment["_id"]),
        "post_id": str(updated_comment["post_id"]),
        "user_id": str(updated_comment["user_id"]),
        "username": updated_comment["username"],
        "text": updated_comment["text"],
        "created_at": updated_comment["created_at"]
    }
