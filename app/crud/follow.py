from motor.motor_asyncio import AsyncIOMotorDatabase
from fastapi import HTTPException
from bson import ObjectId
async def follow_user(db: AsyncIOMotorDatabase, current_user_id: str, target_user_id: str):
    if current_user_id == target_user_id:
        raise HTTPException(status_code=404, detail="You cannot follow yourself.")
    user_collection = db.get_collection("users")

    target_user = await user_collection.find_one({"_id": ObjectId(target_user_id)})

    if not target_user:
        raise HTTPException(status_code=400, detail="Target user not found.")

    current_user = await user_collection.find_one({"_id": ObjectId(current_user_id)})

    if target_user_id in current_user.get("following", []):
        raise HTTPException(status_code=400, detail="Already following this user.")

    # Add target_user_id to current_user's following list (no duplicates)
    await user_collection.update_one(
        {"_id": ObjectId(current_user_id)},
        {"$addToSet": {"following": target_user_id}}#$addToSet to add target to following list and self to followers list without duplicates
    )
    # Add current_user_id to target_user's followers list (no duplicates)
    await user_collection.update_one(
        {"_id": ObjectId(target_user_id)},
        {"$addToSet": {"followers": current_user_id}}
    )

async def unfollow_user(db: AsyncIOMotorDatabase, current_user_id: str, target_user_id: str):
    if current_user_id == target_user_id:
        raise HTTPException(status_code=400, detail="You cannot unfollow yourself.")

    user_collection = db.get_collection("users")

    await user_collection.update_one(
        {"_id": ObjectId(current_user_id)},
        {"$pull": {"following": target_user_id}}
    )
    await user_collection.update_one(
        {"_id": ObjectId(target_user_id)},
        {"$pull": {"followers": current_user_id}}#$pull user to remove elemeny from array
    )

async def get_user_follow_data(db: AsyncIOMotorDatabase, user_id: str):
    user = await db.get_collection("users").find_one({"_id": ObjectId(user_id)})
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    
    return {
        "user_id": str(user["_id"]),
        "follower": user.get("followers", []),
        "following": user.get("following", [])
    }