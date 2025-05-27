from pydantic import BaseModel, EmailStr,Field
from typing import List, Optional
from datetime import datetime
from pydantic import HttpUrl

#Take date for geister the user in DB
class UserRegister(BaseModel):
    username : str =Field(..., min_length=3, max_length=50)
    email : EmailStr
    password : str = Field(..., min_length=8)
    bio: Optional[str] = ""
    avatar_url: Optional[HttpUrl] = None


#For internal DB storage 
class UserInDB(BaseModel):
    username : str
    email : EmailStr
    hashed_password : str
    is_verified : bool = False
    bio: Optional[str] = ""
    avatar_url: Optional[HttpUrl] = None
    created_at: datetime

# For returning public profile data
class UserPublic(BaseModel):
    username: str
    email: EmailStr
    bio: Optional[str]
    avatar_url: Optional[HttpUrl]
    created_at: datetime

class OTPVerify(BaseModel):
    email: EmailStr
    otp: str

class UserLogin(BaseModel):
    email: EmailStr
    password: str

class UserUpdate(BaseModel):
    username: Optional[str]
    bio: Optional[str]
    avatar_url: Optional[HttpUrl]

class FollowResponse(BaseModel):
    message : str

class PublicUser(BaseModel):
    id: str = Field(..., alias="_id")
    username: str
    follower: List[str] = []
    following: List[str] = []

class UserListResponse(BaseModel):
    user_id :str
    follower : List[str]
    following : List[str]
    