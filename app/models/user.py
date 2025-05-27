from datetime import datetime 

def user_helper(user) -> dict:
    return {
        "id": str(user["_id"]),
        "username": user["username"],
        "email": user["email"],
        "bio": user.get("bio", ""),
        "avatar_url": user.get("avatar_url"),
        "is_verified": user["is_verified"],
        "created_at": user["created_at"]
    }