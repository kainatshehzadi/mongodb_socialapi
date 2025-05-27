from enum import Enum

class PostVisibilityEnum(str, Enum):
    public = "public"
    private = "private"
    friends_only = "friends_only"
