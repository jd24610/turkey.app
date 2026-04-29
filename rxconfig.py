import reflex as rx

config = rx.Config(
    app_name="TurkeyApp",
    cors_allowed_origins=[
        "http://localhost:3000",
        "https://turkey-app-frontend.onrender.com",
    ],
)
