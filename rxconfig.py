import reflex as rx
import os
from dotenv import load_dotenv

load_dotenv()

# Use the Render backend URL if we are in production, otherwise localhost
api_url = os.getenv("API_URL", "http://localhost:8000")

config = rx.Config(
    app_name="TurkeyApp",
    api_url=api_url,
    cors_allowed_origins=[
        "http://localhost:3000",
        "https://turkey-app-frontend.onrender.com",
    ],
    google_client_id=os.getenv("GOOGLE_CLIENT_ID"),
    show_built_with_reflex=False,  # Hide the Reflex "R" badge
    admin_dash=False,
)
