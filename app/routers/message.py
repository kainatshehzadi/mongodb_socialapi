from fastapi import APIRouter, Depends
from app.db.database import db
from app.schemas.message import MessageCreate, MessageResponse
from app.depends import get_current_user
from app.utils.pusher import pusher_client
from bson import ObjectId
from datetime import datetime, timezone

router = APIRouter(prefix="/messages", tags=["Messages"])

@router.post("/", response_model=MessageResponse)
async def send_message(payload: MessageCreate, current_user: dict = Depends(get_current_user)):
    message_data = {
        "sender_id": current_user["_id"],
        "receiver_id": ObjectId(payload.receiver_id),
        "text": payload.text,
        "timestamp": datetime.now(timezone.utc)
    }

    result = await db["messages"].insert_one(message_data)
    message_data["_id"] = result.inserted_id

    # Notify the receiver via Pusher
    pusher_client.trigger(
        f"user_{payload.receiver_id}",  
        "new_message",                  
        {
            "sender_id": str(current_user["_id"]),
            "text": payload.text,
            "timestamp": str(message_data["timestamp"])
        }
    )

    return {
        "id": str(result.inserted_id),
        "sender_id": str(current_user["_id"]),
        "receiver_id": payload.receiver_id,
        "text": payload.text,
        "timestamp": message_data["timestamp"]
    }

# Optional: Get chat history between two users
@router.get("/{user_id}", response_model=list[MessageResponse])
async def get_conversation(user_id: str, current_user: dict = Depends(get_current_user)):
    messages = db["messages"].find({
        "$or": [
            {"sender_id": current_user["_id"], "receiver_id": ObjectId(user_id)},
            {"sender_id": ObjectId(user_id), "receiver_id": current_user["_id"]}
        ]
    }).sort("timestamp", 1)

    return [{
        "id": str(msg["_id"]),
        "sender_id": str(msg["sender_id"]),
        "receiver_id": str(msg["receiver_id"]),
        "text": msg["text"],
        "timestamp": msg["timestamp"]
    } async for msg in messages]
