from fastapi import FastAPI, Request
from fastapi.exceptions import RequestValidationError
from fastapi.responses import JSONResponse
from fastapi.staticfiles import StaticFiles
from app.api import auth
from app.routers import comments, follow, likes, message, post, story, user  

app = FastAPI()
@app.get("/")
async def root():
    return {"message": "Welcome to the Social Media API deployed on Vercel!"}

@app.exception_handler(RequestValidationError)
async def validation_exception_handler(request: Request, exc: RequestValidationError):
    errors = exc.errors()

    for error in errors:
        loc = error.get("loc", [])
        msg = error.get("msg", "")

        if "email" in loc:
            return JSONResponse(status_code=400, content={"message": "Invalid email address"})
        if "password" in loc:
            return JSONResponse(status_code=400, content={"message": "Password must be at least 8 characters"})
        if "username" in loc:
            return JSONResponse(status_code=400, content={"message": "Username is required"})
        if loc and loc[-1] == "visibility":
            return JSONResponse(
                status_code=422,
                content={"detail": "Invalid visibility value! Allowed: public, private, friends_only."},
            )

    return JSONResponse(status_code=400, content={"message": "Invalid credentials"})

    # Default error response for other validation errors
    return JSONResponse(
        status_code=422,
        content={"detail": exc.errors()},
    )
app.include_router(auth.router)
app.include_router(user.router)
app.include_router(follow.router)
app.include_router(post.router)
app.include_router(likes.router)
app.include_router(comments.router)
app.include_router(message.router)
app.include_router(story.router)
app.mount("/uploads", StaticFiles(directory="uploads"), name="uploads")