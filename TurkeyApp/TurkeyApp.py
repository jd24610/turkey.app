"""Welcome to Reflex! This file outlines the steps to create a basic app."""

import reflex as rx

from rxconfig import config
from TurkeyApp.react_oauth_google import google_oauth_provider, google_login
from TurkeyApp.upload_state import UploadState
from TurkeyApp.import_export_page import import_export_page


class State(rx.State):
    """The app state."""
    id_token_json: str = ""
    user_email: str = ""
    user_name: str = ""

    @rx.var
    def is_authenticated(self) -> bool:
        return bool(self.id_token_json)

    def on_success(self, id_token: dict):
        self.id_token_json = str(id_token)
        # Extract email / name from the credential response if present
        cred = id_token.get("credential", "")
        # Decode JWT payload (middle segment) without verification for display
        try:
            import base64, json as _json
            payload_b64 = cred.split(".")[1]
            # Pad base64
            payload_b64 += "=" * (-len(payload_b64) % 4)
            payload = _json.loads(base64.urlsafe_b64decode(payload_b64))
            self.user_email = payload.get("email", "")
            self.user_name = payload.get("name", "")
        except Exception:
            self.user_email = ""
            self.user_name = ""
        return rx.redirect("/library")

    def logout(self):
        self.id_token_json = ""
        self.user_email = ""
        self.user_name = ""
        return rx.redirect("/")


def login_page() -> rx.Component:
    return google_oauth_provider(
        rx.box(
            rx.vstack(
                # Logo / branding
                rx.vstack(
                    rx.box(
                        rx.icon("layers", size=44, color="white"),
                        padding="18px",
                        background="linear-gradient(135deg, #7c3aed, #a855f7)",
                        border_radius="20px",
                        box_shadow="0 8px 32px rgba(124,58,237,0.5)",
                    ),
                    rx.heading("Turkey.app", size="8", color="white",
                               style={"letterSpacing": "-0.03em"}),
                    rx.text(
                        "Your intelligent media library",
                        size="4",
                        color="#a78bfa",
                    ),
                    spacing="4",
                    align="center",
                ),

                # Login card
                rx.box(
                    rx.vstack(
                        rx.text("Sign in to continue", size="3", color="#c4b5fd", weight="medium"),
                        rx.divider(color="rgba(124,58,237,0.2)"),
                        rx.cond(
                            State.is_authenticated,
                            rx.vstack(
                                rx.hstack(
                                    rx.icon("circle-check", size=20, color="#22c55e"),
                                    rx.text("You're signed in!", size="3", color="#86efac"),
                                    spacing="2",
                                    align="center",
                                ),
                                rx.button(
                                    rx.icon("library-big", size=16),
                                    "Open Media Library",
                                    on_click=rx.redirect("/library"),
                                    size="3",
                                    background="linear-gradient(135deg, #7c3aed, #a855f7)",
                                    color="white",
                                    border_radius="12px",
                                    cursor="pointer",
                                    width="100%",
                                ),
                                rx.button(
                                    rx.icon("log-out", size=16),
                                    "Sign out",
                                    on_click=State.logout,
                                    size="2",
                                    variant="ghost",
                                    color_scheme="gray",
                                    width="100%",
                                    cursor="pointer",
                                ),
                                spacing="3",
                                width="100%",
                            ),
                            rx.vstack(
                                google_login(on_success=State.on_success),
                                rx.text(
                                    "JPG & PNG · Up to 1GB storage · Folder export",
                                    size="1",
                                    color="#6b7280",
                                    text_align="center",
                                ),
                                spacing="4",
                                align="center",
                                width="100%",
                            ),
                        ),
                        spacing="5",
                        align="center",
                        width="100%",
                    ),
                    padding="36px",
                    background="rgba(255,255,255,0.05)",
                    border="1px solid rgba(124,58,237,0.3)",
                    border_radius="24px",
                    box_shadow="0 25px 50px rgba(0,0,0,0.5)",
                    backdrop_filter="blur(20px)",
                    width="380px",
                ),

                spacing="8",
                align="center",
                justify="center",
                min_height="100vh",
            ),
            min_height="100vh",
            background="radial-gradient(ellipse at top, #130a2e 0%, #0a0515 60%, #050208 100%)",
            display="flex",
            align_items="center",
            justify_content="center",
        ),
        client_id=config.google_client_id,
    )


def library_page() -> rx.Component:
    """Protected wrapper around the import/export page."""
    return rx.cond(
        State.is_authenticated,
        rx.box(
            # Top nav bar
            rx.hstack(
                rx.hstack(
                    rx.box(
                        rx.icon("layers", size=20, color="white"),
                        padding="8px",
                        background="linear-gradient(135deg, #7c3aed, #a855f7)",
                        border_radius="10px",
                    ),
                    rx.text("Turkey.app", size="4", weight="bold", color="white"),
                    spacing="3",
                    align="center",
                ),
                rx.hstack(
                    rx.cond(
                        State.user_name != "",
                        rx.hstack(
                            rx.icon("circle-user-round", size=18, color="#a78bfa"),
                            rx.text(State.user_name, size="2", color="#c4b5fd"),
                            spacing="2",
                            align="center",
                        ),
                        rx.box(),
                    ),
                    rx.button(
                        rx.icon("log-out", size=16),
                        "Sign out",
                        on_click=State.logout,
                        size="2",
                        variant="ghost",
                        color_scheme="purple",
                        cursor="pointer",
                    ),
                    spacing="4",
                    align="center",
                ),
                justify="between",
                align="center",
                padding="0 32px",
                height="60px",
                background="rgba(10,5,21,0.9)",
                border_bottom="1px solid rgba(124,58,237,0.2)",
                backdrop_filter="blur(12px)",
                position="sticky",
                top="0",
                z_index="100",
                width="100%",
            ),
            import_export_page(),
            width="100%",
        ),
        # Not authenticated → redirect to login
        rx.box(
            rx.vstack(
                rx.icon("lock", size=48, color="#7c3aed"),
                rx.heading("Access Restricted", size="6", color="white"),
                rx.text("Please sign in to access the media library.", size="3", color="#a78bfa"),
                rx.button(
                    "Go to Login",
                    on_click=rx.redirect("/"),
                    size="3",
                    background="linear-gradient(135deg, #7c3aed, #a855f7)",
                    color="white",
                    border_radius="12px",
                    cursor="pointer",
                ),
                spacing="5",
                align="center",
                justify="center",
                min_height="100vh",
            ),
            min_height="100vh",
            background="radial-gradient(ellipse at top, #130a2e 0%, #0a0515 60%, #050208 100%)",
            display="flex",
            align_items="center",
            justify_content="center",
        ),
    )


app = rx.App(
    theme=rx.theme(
        appearance="dark",
        accent_color="violet",
        radius="medium",
    ),
)
app.add_page(login_page, route="/")
app.add_page(library_page, route="/library")
