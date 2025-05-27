from fastapi import APIRouter, Depends,HTTPException,status
from pydantic import HttpUrl
from app.db.database import db
from app.depends import get_current_user
from app.schemas.user import UserUpdate

router = APIRouter(prefix="/users", tags=["Users"])
@router.put("/update")
async def update_my_profile(update_data: UserUpdate, current_user: dict = Depends(get_current_user)):
    current_user_email = current_user["email"]
    user = await db["users"].find_one({"email": current_user_email})
    if not user:
        raise HTTPException(status_code=404, detail="User not found.")

    update_dict = {
        k: (str(v) if isinstance(v, HttpUrl) else v)
        for k, v in update_data.dict().items()
        if v is not None and user.get(k) != v
    }

    if not update_dict:
        raise HTTPException(status_code=400, detail="No changes detected in update fields.")

    try:
        result = await db["users"].update_one(
            {"email": current_user_email},
            {"$set": update_dict}
        )

        if result.modified_count == 0:
            raise HTTPException(status_code=400, detail="Profile not updated.")

        updated_user = await db["users"].find_one({"email": current_user_email}, {"hashed_password": 0})
        updated_user["_id"] = str(updated_user["_id"])
        return updated_user

    except Exception as e:
        print("Update error:", e)
        raise HTTPException(status_code=500, detail="Failed to update profile.")

    
    
@router.get("/me")
async def get_current_user_endpoint(current_user: dict = Depends(get_current_user)):
    
    current_user.pop("hashed_password", None)
    current_user.pop("_id", None)  

    return {"user": current_user}
