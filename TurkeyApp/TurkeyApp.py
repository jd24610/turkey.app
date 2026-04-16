import reflex as rx

from rxconfig import config
from TurkeyApp.react_oauth_google import google_oauth_provider, google_login
from TurkeyApp.upload_state import UploadState
from TurkeyApp.import_export_page import import_export_page
from TurkeyApp.profile_state import ProfileState
from TurkeyApp.onboarding_page import onboarding_modal
from TurkeyApp.profile_page import public_profile_page
from TurkeyApp.edit_profile_modal import edit_profile_modal
from TurkeyApp.search_page import search_page
from TurkeyApp.feed_page import feed_page, FeedState


class State(rx.State):
    """The app state."""
    id_token_json: str = ""
    user_email: str = ""
    user_name: str = ""

    # ── Session persistence via cookie ────────
    session_email: str = rx.Cookie(name="turkey_email", max_age=604800)  # 7 days
    session_name: str = rx.Cookie(name="turkey_name", max_age=604800)

    @rx.var
    def is_authenticated(self) -> bool:
        return bool(self.id_token_json) or bool(self.session_email)

    def on_app_load(self):
        """Called on every page load — restores session from cookie if present."""
        if self.session_email and not self.id_token_json:
            self.user_email = self.session_email
            self.user_name = self.session_name
            yield UploadState.set_user_email(self.session_email)
            yield UploadState.set_user_name(self.session_name)
            yield ProfileState.init_profile(self.session_email, self.session_name)

    def on_success(self, id_token: dict):
        self.id_token_json = str(id_token)
        cred = id_token.get("credential", "")
        try:
            import base64, json as _json
            payload_b64 = cred.split(".")[1]
            payload_b64 += "=" * (-len(payload_b64) % 4)
            payload = _json.loads(base64.urlsafe_b64decode(payload_b64))
            self.user_email = payload.get("email", "")
            self.user_name = payload.get("name", "")
        except Exception:
            self.user_email = ""
            self.user_name = ""

        # Persist to cookie
        self.session_email = self.user_email
        self.session_name = self.user_name

        yield UploadState.set_user_email(self.user_email)
        yield UploadState.set_user_name(self.user_name)
        yield ProfileState.init_profile(self.user_email, self.user_name)
        yield rx.redirect("/library")

    def logout(self):
        self.id_token_json = ""
        self.user_email = ""
        self.user_name = ""
        # Clear cookies
        self.session_email = ""
        self.session_name = ""
        yield UploadState.set_user_email("")
        yield UploadState.set_user_name("")
        yield ProfileState.clear_profile()
        yield rx.redirect("/")


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
                            color="white",
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
                        color="#6b7280",
                        letter_spacing="0.5px",
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


# ─── Library page (protected) ─────────────────────────────────────────────────

def _profile_avatar_btn() -> rx.Component:
    """Compact avatar+name chip in the navbar that opens Edit Profile."""
    return rx.cond(
        ProfileState.onboarding_complete,
        rx.hstack(
            # Avatar or initials
            rx.cond(
                ProfileState.own_avatar_url != "",
                rx.image(
                    src=ProfileState.own_avatar_url,
                    width="30px", height="30px",
                    object_fit="cover",
                    border_radius="50%",
                    border="2px solid rgba(168,85,247,0.5)",
                    flex_shrink="0",
                ),
                rx.box(
                    rx.text(ProfileState.own_initials, size="1", weight="bold", color="white"),
                    width="30px", height="30px",
                    border_radius="50%",
                    background="linear-gradient(135deg, #7c3aed, #a855f7)",
                    display="flex", align_items="center", justify_content="center",
                    box_shadow="0 0 10px rgba(124,58,237,0.5)",
                    flex_shrink="0",
                ),
            ),
            rx.vstack(
                rx.text(ProfileState.own_display_name, size="1", weight="bold", color="white"),
                rx.text("@" + ProfileState.own_username, size="1", color="#a78bfa"),
                spacing="0", align="start",
            ),
            spacing="2", align="center",
            cursor="pointer",
            padding="6px 12px",
            border_radius="20px",
            background="rgba(124,58,237,0.12)",
            border="1px solid rgba(124,58,237,0.25)",
            _hover={"background": "rgba(124,58,237,0.22)", "border_color": "rgba(168,85,247,0.5)"},
            transition="all 0.15s ease",
            on_click=rx.redirect("/u/" + ProfileState.own_username),
        ),
        # Fallback: just show the Google name
        rx.cond(
            State.user_name != "",
            rx.hstack(
                rx.icon("circle-user-round", size=18, color="#a78bfa"),
                rx.text(State.user_name, size="2", color="#c4b5fd"),
                spacing="2", align="center",
            ),
            rx.box(),
        ),
    )


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
            rx.hstack(
                # Navbar logo mark
                rx.hstack(
                    rx.image(
                        src="/turkey_icon.png",
                        width="34px",
                        height="34px",
                        object_fit="cover",
                        border_radius="9px",
                        box_shadow="0 0 12px rgba(124,58,237,0.5)",
                    ),
                    rx.hstack(
                        rx.text("turkey", size="4", weight="bold", color="white", letter_spacing="-0.5px"),
                        rx.text(".app", size="4", weight="bold", color="#a855f7", letter_spacing="-0.5px"),
                        spacing="0",
                    ),
                    spacing="2", align="center",
                ),
                rx.hstack(
                    _profile_avatar_btn(),
                    # Edit profile
                    rx.cond(
                        ProfileState.onboarding_complete,
                        rx.button(
                            rx.icon("user-pen", size=15),
                            on_click=ProfileState.open_edit_profile,
                            size="2",
                            variant="ghost",
                            color_scheme="purple",
                            cursor="pointer",
                            title="Edit Profile",
                        ),
                        rx.box(),
                    ),
                    # Feed
                    rx.button(
                        rx.icon("rss", size=15),
                        on_click=rx.redirect("/feed"),
                        size="2",
                        variant="ghost",
                        color_scheme="purple",
                        cursor="pointer",
                        title="Public Feed",
                    ),
                    # Search
                    rx.button(
                        rx.icon("search", size=15),
                        on_click=rx.redirect("/search"),
                        size="2",
                        variant="ghost",
                        color_scheme="purple",
                        cursor="pointer",
                        title="Discover people",
                    ),
                    # Settings gear
                    rx.button(
                        rx.icon("settings", size=16),
                        on_click=UploadState.toggle_settings,
                        size="2",
                        variant="ghost",
                        color_scheme="purple",
                        cursor="pointer",
                        title="Preferences",
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
                    spacing="3",
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
            min_height="100vh",
            background=UploadState.bg_theme,
        ),
        # Not authenticated
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


# ─── App ─────────────────────────────────────────────────────────────────────

app = rx.App(
    theme=rx.theme(
        appearance="dark",
        accent_color="violet",
        radius="medium",
    ),
)
app.add_page(login_page, route="/", on_load=State.on_app_load)
app.add_page(library_page, route="/library", on_load=[State.on_app_load, UploadState.on_load])
app.add_page(public_profile_page, route="/u/[username]", on_load=ProfileState.load_public_profile)
app.add_page(search_page, route="/search", on_load=State.on_app_load)
app.add_page(feed_page, route="/feed", on_load=FeedState.load_feed)
