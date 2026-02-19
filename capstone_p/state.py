import reflex as rx
import os
import shutil
import zipfile
import io
from datetime import datetime
from typing import List, Optional
from .models import User, Image
from sqlmodel import select

UPLOAD_DIR = "uploaded_images"
if not os.path.exists(UPLOAD_DIR):
    os.makedirs(UPLOAD_DIR)

class State(rx.State):
    """The app state."""
    
    # Auth State
    user: Optional[User] = None
    is_logged_in: bool = False
    auth_error: str = ""
    
    # Image State
    images: List[Image] = []
    current_storage_usage: int = 0
    storage_limit_display: str = "0 GB / 1 GB"
    
    def check_login(self):
        """Check if a user is logged in (simulated session)."""
        # In a real app, check local storage/cookies
        pass

    def login(self, form_data: dict):
        email = form_data.get("email")
        password = form_data.get("password")
        
        with rx.session() as session:
            user = session.exec(select(User).where(User.email == email)).first()
            if user and user.password_hash == password: # In real app, verify hash
                self.user = user
                self.is_logged_in = True
                self.auth_error = ""
                self.refresh_data()
                return rx.redirect("/")
            else:
                self.auth_error = "Invalid credentials"

    def signup(self, form_data: dict):
        email = form_data.get("email")
        password = form_data.get("password")
        
        with rx.session() as session:
            if session.exec(select(User).where(User.email == email)).first():
                self.auth_error = "Email already exists"
                return

            new_user = User(
                email=email, 
                password_hash=password, # In real app, hash this!
                storage_limit=1024*1024*1024 # 1GB
            )
            session.add(new_user)
            session.commit()
            session.refresh(new_user)
            
            self.user = new_user
            self.is_logged_in = True
            self.refresh_data()
            return rx.redirect("/")

    def logout(self):
        self.user = None
        self.is_logged_in = False
        return rx.redirect("/")

    # Google Auth
    def start_google_auth(self):
        """Redirect to Google's OAuth consent screen."""
        client_id = os.getenv("GOOGLE_CLIENT_ID", "")
        if not client_id:
            return rx.window_alert("GOOGLE_CLIENT_ID not set in environment.")
            
        redirect_uri = os.getenv("GOOGLE_REDIRECT_URL", "http://localhost:3000/")
        scope = "openid email profile"
        
        # Manual construction of Google Auth URL (Server-side flow)
        response_type = "code"
        auth_url = f"https://accounts.google.com/o/oauth2/v2/auth?client_id={client_id}&redirect_uri={redirect_uri}&scope={scope}&response_type={response_type}"
        return rx.redirect(auth_url)

    async def check_google_callback(self):
        """Check if we just returned from Google with a code."""
        args = self.router.page.params
        code = args.get("code")
        
        if code and not self.is_logged_in:
            await self.finish_google_auth(code)

    async def finish_google_auth(self, code: str):
        """Exchange code for token and log in user."""
        client_id = os.getenv("GOOGLE_CLIENT_ID", "")
        client_secret = os.getenv("GOOGLE_CLIENT_SECRET", "")
        redirect_uri = os.getenv("GOOGLE_REDIRECT_URL", "http://localhost:3000/")
        
        if not client_id or not client_secret:
            self.auth_error = "Missing Google Credentials"
            return

        import httpx
        token_url = "https://oauth2.googleapis.com/token"
        data = {
            "code": code,
            "client_id": client_id,
            "client_secret": client_secret,
            "redirect_uri": redirect_uri,
            "grant_type": "authorization_code"
        }
        
        async with httpx.AsyncClient() as client:
            resp = await client.post(token_url, data=data)
            if resp.status_code != 200:
                self.auth_error = "Failed to verify Google Token"
                return
            
            token_data = resp.json()
            id_token = token_data.get("id_token")
            access_token = token_data.get("access_token")
            
            # Get User Info
            user_info_resp = await client.get(
                "https://www.googleapis.com/oauth2/v1/userinfo", 
                headers={"Authorization": f"Bearer {access_token}"}
            )
            if user_info_resp.status_code != 200:
                self.auth_error = "Failed to fetch user info"
                return
                
            user_info = user_info_resp.json()
            email = user_info.get("email")
            
            # Login or Create User
            with rx.session() as session:
                user = session.exec(select(User).where(User.email == email)).first()
                if not user:
                    # Auto-register
                    user = User(
                        email=email,
                        password_hash="google-oauth-user", 
                        storage_limit=1024*1024*1024 # 1GB
                    )
                    session.add(user)
                    session.commit()
                    session.refresh(user)
                
                self.user = user
                self.is_logged_in = True
                self.auth_error = ""
                
        # Clear params from URL
        return rx.redirect("/")
        
    def refresh_data(self):
        if not self.user:
            return
            
        with rx.session() as session:
            # Refresh user from DB to get latest storage usage
            self.user = session.exec(select(User).where(User.id == self.user.id)).first()
            self.images = self.user.images
            
            self.current_storage_usage = self.user.used_storage
            limit_gb = self.user.storage_limit / (1024**3)
            used_mb = self.user.used_storage / (1024**2)
            self.storage_limit_display = f"{used_mb:.2f} MB / {limit_gb:.2f} GB"

    async def handle_upload(self, files: List[rx.UploadFile]):
        if not self.user:
            return

        with rx.session() as session:
            # re-fetch user to be thread-safe with session
            current_user = session.exec(select(User).where(User.id == self.user.id)).first()
            
            for file in files:
                upload_data = await file.read()
                file_size = len(upload_data)
                
                # Check storage limit
                if current_user.used_storage + file_size > current_user.storage_limit:
                    return rx.window_alert("Storage limit exceeded!")
                
                filename = file.filename
                # Simple save to disk
                save_path = os.path.join(UPLOAD_DIR, f"{datetime.now().timestamp()}_{filename}")
                with open(save_path, "wb") as f:
                    f.write(upload_data)
                    
                # DB Entry
                img = Image(
                    filename=filename,
                    file_path=save_path,
                    file_size=file_size,
                    user_id=current_user.id
                )
                session.add(img)
                current_user.used_storage += file_size
                
            session.add(current_user)
            session.commit()
            
        self.refresh_data()

    async def handle_import_folder(self, files: List[rx.UploadFile]):
        if not self.user:
            return
            
        with rx.session() as session:
             current_user = session.exec(select(User).where(User.id == self.user.id)).first()
             
             for file in files:
                 if not file.filename.endswith(".zip"):
                     return rx.window_alert("Please upload a .zip file")
                     
                 content = await file.read()
                 try:
                     with zipfile.ZipFile(io.BytesIO(content)) as z:
                         for file_info in z.infolist():
                             if file_info.is_dir() or not file_info.filename.lower().endswith(('.png','.jpg','.jpeg')):
                                 continue
                                 
                             file_size = file_info.file_size
                             if current_user.used_storage + file_size > current_user.storage_limit:
                                 return rx.window_alert("Storage limit exceeded during import!")
                                 
                             filename = os.path.basename(file_info.filename)
                             save_path = os.path.join(UPLOAD_DIR, f"{datetime.now().timestamp()}_{filename}")
                             
                             with open(save_path, "wb") as f:
                                 f.write(z.read(file_info.filename))
                                 
                             img = Image(
                                 filename=filename,
                                 file_path=save_path,
                                 file_size=file_size,
                                 user_id=current_user.id
                             )
                             session.add(img)
                             current_user.used_storage += file_size
                             
                 except zipfile.BadZipFile:
                     return rx.window_alert("Invalid zip file")
            
             session.add(current_user)
             session.commit()
             
        self.refresh_data()
        return rx.window_alert("Import successful")

    def export_folder(self):
        """Export all images as a zip file."""
        if not self.user or not self.images:
            return rx.window_alert("No images to export")
            
        
        
        zip_filename = f"export_{self.user.id}_{int(datetime.now().timestamp())}.zip"
        zip_path = os.path.join("assets", zip_filename)
        
        with zipfile.ZipFile(zip_path, "w") as z:
            for img in self.images:
                if os.path.exists(img.file_path):
                    z.write(img.file_path, arcname=img.filename)
                    
        return rx.download(f"/{zip_filename}")
        




