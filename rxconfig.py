import reflex as rx
import os
from dotenv import load_dotenv

load_dotenv()

config = rx.Config(
    app_name="TurkeyApp",
    cors_allowed_origins=[
        "http://localhost:3000",
        "https://turkey-app-frontend.onrender.com",
    ],
    google_client_id=os.getenv("GOOGLE_CLIENT_ID"),
)
