import reflex as rx

config = rx.Config(
    app_name="turkeyapp",
    db_url="sqlite:///reflex.db",
    env=rx.Env.DEV,
)
