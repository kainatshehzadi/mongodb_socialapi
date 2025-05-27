from bson import ObjectId
from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from jose import JWTError
from app.db.database import db  
from app.utils.security import ALGORITHM, SECRET_KEY, decode_token 

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="auth/login")

async def get_current_user_email(token: str = Depends(oauth2_scheme)):
    try:
        payload = await decode_token(token) 
        return payload["sub"]
    except Exception:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid token.")

async def get_current_user(token: str = Depends(oauth2_scheme)):
    try:
        payload = await decode_token(token)   
        user_id = payload.get("user_id")
        if user_id is None:
            raise HTTPException(status_code=401, detail="Invalid token payload.")
    except JWTError:
        raise HTTPException(status_code=401, detail="Token is invalid or expired.")

    user = await db["users"].find_one({"_id": ObjectId(user_id)})
    if not user:
        raise HTTPException(status_code=404, detail="User not found.")
    return user
