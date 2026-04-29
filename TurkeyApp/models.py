import reflex as rx
from sqlmodel import Field, Relationship
from typing import List, Optional
from datetime import datetime


class User(rx.Model, table=True):
    email: str = Field(unique=True, index=True)
    password_hash: str
    storage_limit: int = Field(default=1073741824)  # 1GB default
    used_storage: int = Field(default=0)

    images: List["Image"] = Relationship(back_populates="user")


class Image(rx.Model, table=True):
    filename: str
    file_path: str
    file_size: int
    upload_date: datetime = Field(default_factory=datetime.utcnow)
    user_id: int = Field(foreign_key="user.id")

    user: Optional[User] = Relationship(back_populates="images")


class Folder(rx.Model, table=True):
    """A folder that groups images."""
    name: str
    owner_email: str
    description: Optional[str] = Field(default=None)
    is_public: bool = False
    created_at: Optional[str] = Field(default=None)


class ImageRecord(rx.Model, table=True):
    """A stored image record."""
    filename: str
    original_filename: str
    folder_name: str = ""
    owner_email: str
    mime_type: str = "image/jpeg"
    size_bytes: int = 0
    was_compressed: bool = False
    created_at: Optional[str] = Field(default=None)
    is_public: bool = Field(default=False)
    caption: Optional[str] = Field(default=None)
    exif_info: Optional[str] = Field(default=None) # JSON-stringified metadata
    cdn_url: Optional[str] = Field(default=None)   # Permanent Cloudinary/CDN URL


class Tag(rx.Model, table=True):
    """A user-defined tag for organizing images."""
    name: str
    color: str = "#7c3aed"
    owner_email: str
    created_at: Optional[str] = Field(default=None)


class ImageTag(rx.Model, table=True):
    """Many-to-many association between images and tags."""
    image_id: int = Field(foreign_key="imagerecord.id")
    tag_id: int = Field(foreign_key="tag.id")


class UserProfile(rx.Model, table=True):
    """Extended user profile collected during onboarding."""
    email: str = Field(unique=True, index=True)    # FK to Google OAuth email
    username: str = Field(unique=True, index=True) # @handle, URL-safe
    display_name: str = ""
    bio: str = ""
    date_of_birth: str = ""     # YYYY-MM-DD string
    avatar_filename: str = ""   # uploaded avatar via storage system
    banner_filename: str = ""   # custom profile banner
    location: str = ""
    website: str = ""
    is_public: bool = True
    created_at: Optional[str] = Field(default=None)
    onboarding_complete: bool = False


class Follow(rx.Model, table=True):
    """Follower -> Following relationship."""
    follower_email: str = Field(index=True)   # the person who clicked Follow
    following_email: str = Field(index=True)  # the person being followed
    status: str = "accepted"                  # "pending" | "accepted"
    created_at: Optional[str] = Field(default=None)


class Notification(rx.Model, table=True):
    """General notification system."""
    to_email: str = Field(index=True)
    from_email: str = ""
    from_username: str = ""
    type: str = "follow_request"              # "follow_request" | "alert" | "comment" | "like"
    status: str = "unread"                    # "unread" | "read" | "accepted" | "declined"
    message: str = ""
    created_at: Optional[str] = Field(default=None)


class Like(rx.Model, table=True):
    """A heart/like on a public image."""
    liker_email: str = Field(index=True)
    image_id: int = Field(index=True)
    created_at: Optional[str] = Field(default=None)


class Comment(rx.Model, table=True):
    """A text comment on a public image."""
    image_id: int = Field(index=True)
    author_email: str = Field(index=True)
    author_username: str = ""
    text: str
    created_at: Optional[str] = Field(default=None)
