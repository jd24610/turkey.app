import reflex as rx
from .state import State
from .models import Image

def login_form() -> rx.Component:
    return rx.vstack(
        rx.heading("Login", size="7"),
        rx.text(State.auth_error, color="red"),
        rx.form(
            rx.vstack(
                rx.input(placeholder="Email", name="email"),
                rx.input(placeholder="Password", name="password", type="password"),
                rx.button("Login", type="submit"),
            ),
            on_submit=State.login,
        ),
        rx.text("Or"),
        rx.form( # Signup form for simplicity next to it
             rx.vstack(
                rx.input(placeholder="New Email", name="email"),
                rx.input(placeholder="New Password", name="password", type="password"),
                rx.button("Register", type="submit"),
            ),
            on_submit=State.signup,
        ),
        rx.button("Login with Google", on_click=State.start_google_auth),
        spacing="4",
        align="center",
        justify="center",
        height="100vh",
    )

def image_card(img: Image) -> rx.Component:
    return rx.card(
        rx.vstack(
            rx.image(src="/placeholder.png", height="100px"), # In real app, serve the image
            rx.text(img.filename, size="2"),
            rx.text(f"{img.file_size / 1024:.1f} KB", size="1"),
        )
    )

def dashboard() -> rx.Component:
    return rx.vstack(
        rx.hstack(
            rx.heading("My Images"),
            rx.spacer(),
            rx.text(State.storage_limit_display),
            rx.button("Logout", on_click=State.logout),
            width="100%",
            padding="4",
            border_bottom="1px solid #ccc"
        ),
        rx.vstack(
            rx.hstack(
                rx.text("Upload Images:"),
                rx.upload(
                    rx.button("Select Images"),
                    id="upload_images",
                    multiple=True,
                    accept={"image/*": [".png", ".jpg", ".jpeg"]},
                    max_files=10,
                ),
                rx.button(
                    "Upload",
                    on_click=State.handle_upload(rx.upload_files(upload_id="upload_images")),
                ),
            ),
            rx.hstack(
                rx.text("Import Folder (Zip):"),
                rx.upload(
                    rx.button("Select Zip"),
                    id="upload_zip",
                    multiple=False,
                    accept={".zip": [".zip"]},
                ),
                rx.button(
                    "Import",
                    on_click=State.handle_import_folder(rx.upload_files(upload_id="upload_zip")),
                ),
                 rx.button("Export All", on_click=State.export_folder),
            ),
            spacing="4",
            padding="4",
            align="start",
            width="100%"
        ),
        rx.grid(
            rx.foreach(State.images, image_card),
            columns="4",
            spacing="4",
            padding="4",
            width="100%"
        ),
        width="100%",
    )

def index() -> rx.Component:
    return rx.cond(
        State.is_logged_in,
        dashboard(),
        login_form(),
    )

app = rx.App()
app.add_page(index, on_load=[State.refresh_data, State.check_google_callback])
