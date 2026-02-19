import reflex as rx

config = rx.Config(
    app_name="capstone_p",
    db_url="sqlite:///reflex.db",
    env=rx.Env.DEV,
)
