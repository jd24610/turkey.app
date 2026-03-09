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
    created_at: str = ""


class ImageRecord(rx.Model, table=True):
    """A stored image record."""
    filename: str
    original_filename: str
    folder_name: str = ""
    owner_email: str
    mime_type: str = "image/jpeg"
    size_bytes: int = 0
    was_compressed: bool = False
    created_at: str = ""


class Tag(rx.Model, table=True):
    """A user-defined tag for organizing images."""
    name: str
    color: str = "#7c3aed"
    owner_email: str
    created_at: str = ""


class ImageTag(rx.Model, table=True):
    """Many-to-many association between images and tags."""
    image_id: int = Field(foreign_key="imagerecord.id")
    tag_id: int = Field(foreign_key="tag.id")
