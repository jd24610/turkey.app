from pydantic import BaseModel, EmailStr
from fastapi import UploadFile, File
from datetime import datetime
from core.config import settings
from core.database import get_db
from core.models import User, Image
from core.schemas import UserBase, UserCreate, UserLogin, User, Token, TokenData, ImageBase, Image, ImageUpload
from jose import JWTError, jwt

from typing import Optional

class UserBase(BaseModel):
    email: EmailStr

class UserCreate(UserBase):
    password: str

class UserLogin(UserBase):
    password: str
    email: EmailStr
    
class User(UserBase):
    id: int
    is_active: bool
    storage_limit: int
    used_storage: int

    class Config:
        orm_mode = True

class Token(BaseModel):
    access_token: str
    token_type: str

class TokenData(BaseModel):
    email: Optional[str] = None

class ImageBase(BaseModel):
    filename: str

class Image(ImageBase):
    id: int
    file_path: str
    file_size: int
    upload_date: datetime
    owner_id: int

    class Config:
        orm_mode = True
        from_attributes = True 

    class Config:
        orm_mode = True 
    

    class Config:
        orm_mode = True 
        from_attributes = True 
        class from_attributes = True 
        class from_attributes = True  



class ImageUpload(BaseModel):
    file: UploadFile = File(...)
    upload_date: datetime
    owner_id: int   

    class Config:
        orm_mode = True 
        from_attributes = True 
        class from_attributes = True 
        class from_attributes = True  

        class       image_upload(BaseModel):
            file: UploadFile = File(...)
            upload_date: datetime
            owner_id: int   

            class Config:
                orm_mode = True 
                from_attributes = True 
                class from_attributes = True 
                class from_attributes = True  
    class image_upload(BaseModel):
        file: UploadFile = File(...)
        upload_date: datetime
        owner_id: int   

        class Config:
            orm_mode = True 
            from_attributes = True 
            class from_attributes = True 
            class from_attributes = True  