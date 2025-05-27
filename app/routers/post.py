from typing import List
from fastapi import APIRouter, Depends, HTTPException, Query, status
from httpx import post
from app.schemas.post import PostCreate, PostResponse, PostUpdate
from app.depends import get_current_user
from bson import ObjectId
from datetime import datetime, timedelta, timezone
from app.db.database import db
from app.utils.hashtag import extract_hashtags

router = APIRouter(prefix="/posts", tags=["Post"])

@router.post("/", response_model=PostResponse, status_code=status.HTTP_201_CREATED)
async def create_post(payload: PostCreate, current_user: dict = Depends(get_current_user)):
    hashtags = extract_hashtags(payload.content)
    post = {
        "content": payload.content,
        "image_url": str(payload.image_url) if payload.image_url else None,
        "hashtags": hashtags,
        "user_id": current_user["_id"],
        "created_at": datetime.now(timezone.utc),
        "visibility": payload.visibility
    }
    try:
        result = await db["posts"].insert_one(post)
        post["id"] = str(result.inserted_id)
        post["user_id"] = str(post["user_id"])  # convert ObjectId to str if needed
        return PostResponse(**post)
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Post creation failed: {e}")
    
@router.get("/", response_model=List[PostResponse])
async def get_posts():
    try:
        posts_cursor = db["posts"].find()
        posts = []
        async for post in posts_cursor:
            post["id"] = str(post["_id"])
            post["user_id"] = str(post["user_id"])  
            del post["_id"]  
            posts.append(PostResponse(**post))
        return posts
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to retrieve posts: {e}")

    

@router.put("/{post_id}")
async def update_post(post_id: str, update_data: PostUpdate, current_user: dict = Depends(get_current_user)):
    if not ObjectId.is_valid(post_id):
        raise HTTPException(status_code=400, detail="Invalid post ID.")

    post = await db["posts"].find_one({"_id": ObjectId(post_id)})

    if not post:
        raise HTTPException(status_code=404, detail="Post not found.")

    if str(post["user_id"]) != str(current_user["_id"]):
        raise HTTPException(status_code=403, detail="Not authorized to update this post.")

    update_dict = {k: v for k, v in update_data.dict().items() if v is not None}

    if not update_dict:
        raise HTTPException(status_code=400, detail="No valid fields provided to update.")

    try:
        await db["posts"].update_one({"_id": ObjectId(post_id)}, {"$set": update_dict})
        return {"msg": "Post updated successfully."}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error updating post: {str(e)}")


# Delete Post
@router.delete("/{post_id}")
async def delete_post(post_id: str, current_user: dict = Depends(get_current_user)):
    if not ObjectId.is_valid(post_id):
        raise HTTPException(status_code=400, detail="Invalid post ID.")

    post = await db["posts"].find_one({"_id": ObjectId(post_id)})

    if not post:
        raise HTTPException(status_code=404, detail="Post not found.")

    if str(post["user_id"]) != str(current_user["_id"]):
        raise HTTPException(status_code=403, detail="Not authorized to delete this post.")

    try:
        await db["posts"].delete_one({"_id": ObjectId(post_id)})
        return {"msg": "Post deleted successfully."}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error deleting post: {str(e)}")

@router.get("/hashtag/{tag}")
async def search_by_hashtag(tag: str):
    posts = db["posts"].find({"hashtags": tag})
    return [dict(p, id=str(p["_id"])) async for p in posts]

@router.get("/trending")
async def get_trending_posts(limit: int = 10, days: int = 7):
    try:
        cutoff_date = datetime.now(timezone.utc) - timedelta(days=days)
        posts_cursor = db["posts"].find(
            {"created_at": {"$gte": cutoff_date}}
        ).sort([("likes_count", -1), ("created_at", -1)]).limit(limit)

        posts = []
        async for post in posts_cursor:
            post["id"] = str(post["_id"])
            posts.append(post)
        return {"trending_posts": posts}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to fetch trending posts: {e}")

@router.get("/explore")
async def get_explore_posts(
    current_user: dict = Depends(get_current_user),
    limit: int = 10,
    days: int = Query(7, description="Number of days to look back for explore posts")
):
    try:
        cutoff_date = datetime.now(timezone.utc) - timedelta(days=days)
        posts_cursor = db["posts"].find(
            {
                "user_id": {"$ne": current_user["_id"]},
                "created_at": {"$gte": cutoff_date},
                "visibility": "public"
            }
        ).limit(limit)
        posts = []
        async for post in posts_cursor:
            post["id"] = str(post["_id"])
            posts.append(post)
        return {"explore_posts": posts}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to fetch explore posts: {e}")