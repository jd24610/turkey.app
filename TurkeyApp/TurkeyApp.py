import reflex as rx

from rxconfig import config
from TurkeyApp.react_oauth_google import google_oauth_provider, google_login
from TurkeyApp.upload_state import UploadState
from TurkeyApp.import_export_page import import_export_page
from TurkeyApp.profile_state import ProfileState
from TurkeyApp.onboarding_page import onboarding_modal
from TurkeyApp.profile_page import public_profile_page
from TurkeyApp.edit_profile_modal import edit_profile_modal
from TurkeyApp.navbar import navbar
from TurkeyApp.search_page import search_page
from TurkeyApp.notifications_page import notifications_page
from TurkeyApp.feed_page import feed_page, FeedState
from TurkeyApp.state import State


# State is now imported from TurkeyApp.state


# ─── Login page ──────────────────────────────────────────────────────────────

def login_page() -> rx.Component:
    return google_oauth_provider(
        rx.box(
            rx.vstack(
                # Logo / branding
                rx.vstack(
                    # Icon mark
                    rx.box(
                        rx.image(
                            src="/turkey_icon.png",
                            width="90px",
                            height="90px",
                            object_fit="cover",
                            border_radius="22px",
                        ),
                        box_shadow="0 8px 40px rgba(124,58,237,0.55)",
                        border_radius="22px",
                        border="1px solid rgba(168,85,247,0.3)",
                    ),
                    # Brand name
                    rx.hstack(
                        rx.text(
                            "turkey",
                            size="7",
                            weight="bold",
                            color=UploadState.text_color,
                            letter_spacing="-1px",
                        ),
                        rx.text(
                            ".app",
                            size="7",
                            weight="bold",
                            color="#a855f7",
                            letter_spacing="-1px",
                        ),
                        spacing="0",
                    ),
                    rx.text(
                        "Your intelligent media library",
                        size="2",
                        color=UploadState.sub_text_color,
                        letter_spacing="0.5px",
                    ),
                    spacing="4",
                    align="center",
                ),

                # Login card
                rx.box(
                    rx.vstack(
                        rx.text("Sign in to continue", size="3", color=UploadState.text_color, weight="medium"),
                        rx.divider(color=UploadState.border_color),
                        rx.cond(
                            State.is_authenticated,
                            rx.vstack(
                                rx.hstack(
                                    rx.icon("circle-check", size=20, color="#22c55e"),
                                    rx.text("You're signed in!", size="3", color="#16a34a"),
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
                                # ── Divider ──
                                rx.hstack(
                                    rx.divider(flex="1", color=UploadState.border_color),
                                    rx.text("or", size="1", color="#9ca3af", padding_x="10px"),
                                    rx.divider(flex="1", color=UploadState.border_color),
                                    width="100%",
                                    align="center",
                                ),
                                # ── Guest button ──
                                rx.button(
                                    rx.icon("user", size=15),
                                    "Continue as Guest",
                                    on_click=State.login_as_guest,
                                    size="3",
                                    width="100%",
                                    variant="outline",
                                    color_scheme="gray",
                                    border_radius="12px",
                                    cursor="pointer",
                                    border="1px solid " + UploadState.border_color,
                                    color=UploadState.sub_text_color,
                                    _hover={
                                        "background": "rgba(0,0,0,0.04)",
                                    },
                                    transition="all 0.2s ease",
                                ),
                                rx.text(
                                    "👁 Guests can browse the feed & profiles, but can't upload or like.",
                                    size="1",
                                    color="#9ca3af",
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
                    padding="40px",
                    background=UploadState.bg_theme,
                    border="1px solid " + UploadState.border_color,
                    border_radius="32px",
                    box_shadow="0 30px 60px rgba(0,0,0,0.12), 0 0 0 1px rgba(0,0,0,0.02)",
                    width="400px",
                ),

                spacing="8",
                align="center",
                justify="center",
                min_height="100vh",
            ),
            min_height="100vh",
            background=UploadState.bg_theme,
            display="flex",
            align_items="center",
            justify_content="center",
        ),
        client_id=config.google_client_id,
    )


# ─── Library page (protected) ─────────────────────────────────────────────────




def library_page() -> rx.Component:
    """Protected wrapper around the import/export page."""
    return rx.cond(
        State.is_authenticated,
        rx.box(
            # ── Onboarding wizard overlay ──
            onboarding_modal(),
            # ── Edit profile modal ──
            edit_profile_modal(),
            # Top nav bar
            navbar(active_page="library"),
            import_export_page(),
            width="100%",
            min_height="100vh",
            background=UploadState.bg_theme,
        ),
        # Not authenticated
        rx.box(
            rx.vstack(
                rx.icon("lock", size=48, color="#7c3aed"),
                rx.heading("Access Restricted", size="6", color=UploadState.text_color),
                rx.text("Please sign in to access the media library.", size="3", color=UploadState.sub_text_color),
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
            background=UploadState.bg_theme,
            display="flex",
            align_items="center",
            justify_content="center",
        ),
    )


# ─── App ─────────────────────────────────────────────────────────────────────

app = rx.App(
    theme=rx.theme(
        appearance="light",
        accent_color="violet",
        radius="medium",
    ),
)

# Serve uploaded files from the backend (only if fastapi is present)
try:
    from fastapi.staticfiles import StaticFiles
    import os
    # Force absolute path for Render
    base_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    upload_dir = os.path.join(base_dir, "assets", "uploaded_files")
    if not os.path.exists(upload_dir):
        os.makedirs(upload_dir, exist_ok=True)
    
    app.api.mount("/uploaded_files", StaticFiles(directory=upload_dir), name="uploaded_files")
    
    @app.api.get("/ping")
    def ping():
        return {"status": "ok", "upload_dir": upload_dir}
        
except Exception as e:
    print(f"[turkey] Static mount error: {e}")

app.add_page(login_page, route="/", on_load=State.on_app_load, title="turkey.app — Your Media Library")
app.add_page(library_page, route="/library", on_load=[State.on_app_load, UploadState.on_load], title="My Library • turkey.app")
app.add_page(public_profile_page, route="/u/[username]", on_load=ProfileState.load_public_profile, title="Profile • turkey.app")
app.add_page(search_page, route="/search", on_load=[State.on_app_load, ProfileState.run_search], title="Discover People • turkey.app")
app.add_page(feed_page, route="/feed", on_load=[State.on_app_load, FeedState.load_posts], title="Feed • turkey.app")
app.add_page(notifications_page, route="/notifications", on_load=[State.on_app_load, ProfileState.load_notifications], title="Notifications • turkey.app")


# ─── Database Initialization ──────────────────────────────────────────────────

def init_db():
    import sqlalchemy
    from TurkeyApp import models
    try:
        engine = sqlalchemy.create_engine(config.db_url)
        models.rx.Model.metadata.create_all(engine)
        print("[turkey] Database tables initialized successfully.")
    except Exception as e:
        print(f"[turkey] Database initialization failed: {e}")

# Run init on startup
init_db()
