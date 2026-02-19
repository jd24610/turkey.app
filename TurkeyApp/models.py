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
