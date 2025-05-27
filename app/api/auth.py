from fastapi import APIRouter, HTTPException, status
from app.schemas.user import OTPVerify, UserLogin, UserRegister
from app.db.database import db
from app.utils.security import hash_password, create_access_token, verify_password
from app.utils.email import generate_otp, send_otp_email
from datetime import datetime, timedelta, timezone
from pydantic import HttpUrl, ValidationError

router = APIRouter(prefix="/auth", tags=["Auth"])

otp_store = {}

@router.post("/register")
async def register(user: UserRegister):
    try:
        existing = await db["user"].find_one({"email": user.email})
        if existing:
            raise HTTPException(status_code=400, detail="Email is already registered.")

        otp = generate_otp()
        send_otp_email(user.email, otp)

        otp_store[user.email] = {
            "otp": otp,
            "data": user.dict(),
            "created_at":datetime.now(timezone.utc),
            "password":"password"
        }

        return {"msg": "OTP sent to your email. Please verify to complete registration."}

    except ValidationError as ve:
        raise HTTPException(status_code=422, detail=str(ve))

    except Exception as e:
        raise HTTPException(status_code=500, detail="Error occurred during registration.")
    
@router.post("/verify-otp")
async def verify_otp(payload: OTPVerify):
    entry = otp_store.get(payload.email)
    if not entry:
        raise HTTPException(status_code=400, detail="OTP not found or expired.")

    if entry["otp"] != payload.otp:
        raise HTTPException(status_code=400, detail="Invalid OTP provided.")

    user_data = entry["data"]

    # Convert HttpUrl to string if needed
    if "avatar_url" in user_data and isinstance(user_data["avatar_url"], HttpUrl):
        user_data["avatar_url"] = str(user_data["avatar_url"])

    # Pop password from user_data
    password = user_data.pop("password", None)
    if not password:
        raise HTTPException(status_code=400, detail="Password missing in OTP data.")

    user_data["hashed_password"] = await hash_password(password)
    user_data["is_verified"] = True

    try:
        result = await db["users"].insert_one(user_data)
        del otp_store[payload.email]
        return {
            "msg": "User registered successfully.",
            "user_id": str(result.inserted_id)
        }
    except Exception as e:
        print("MongoDB Insert Error:", e)
        raise HTTPException(status_code=500, detail="Failed to save user to database.")

@router.post("/login")
async def login(user: UserLogin):
    if not user.email or not user.password:
        raise HTTPException(status_code=400, detail="Email and password are required.")

    user_in_db = await db["users"].find_one({"email": user.email})
    if not user_in_db:
        raise HTTPException(status_code=404, detail="Invalid email address.")

    if not user_in_db.get("is_verified"):
        raise HTTPException(status_code=403, detail="Account not verified. Please verify via OTP.")

    if not await verify_password(user.password, user_in_db["hashed_password"]):
        raise HTTPException(status_code=401, detail="Incorrect password.")

    token = await create_access_token({"user_id": str(user_in_db["_id"])}, timedelta(hours=2))

    return {
        "access_token": token,
        "token_type": "bearer",
    }
