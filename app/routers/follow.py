from fastapi import APIRouter, Depends
from app.crud.follow import follow_user, get_user_follow_data, unfollow_user
from app.db.database import get_db
from app.routers.user import get_current_user
from app.schemas.user import FollowResponse, UserListResponse
from motor.motor_asyncio import AsyncIOMotorDatabase

router = APIRouter(prefix="/follow", tags=["Follow"])

@router.post("/{target_user_id}", response_model=FollowResponse)
async def follow_user_handler(
    target_user_id: str,
    db: AsyncIOMotorDatabase = Depends(get_db),
    current_user: dict = Depends(get_current_user)
):
    await follow_user(db, str(current_user["_id"]), target_user_id)
    return {"message": "Successfully followed the user."}

@router.delete("/{target_user_id}", response_model=FollowResponse)
async def unfollow_user_handler(
    target_user_id: str,
    db: AsyncIOMotorDatabase = Depends(get_db),
    current_user: dict = Depends(get_current_user)
):
    await unfollow_user(db, str(current_user["_id"]), target_user_id)
    return {"message": "Successfully unfollowed the user."}

@router.get("/followers-following/{user_id}", response_model=UserListResponse)
async def list_follow_data(
    user_id: str,
    db: AsyncIOMotorDatabase = Depends(get_db)
):
    data = await get_user_follow_data(db, user_id)
    return data