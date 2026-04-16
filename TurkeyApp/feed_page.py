"""Public Feed page — /feed  Shows the most-recent public images from all users."""

import reflex as rx
import sqlmodel
from pydantic import BaseModel
from TurkeyApp.models import ImageRecord, UserProfile
from TurkeyApp.profile_state import ProfileState


FEED_LIMIT = 60   # max posts per load


class FeedPost(BaseModel):
    """A single public post in the feed."""
    image_id: int = 0
    filename: str = ""
    caption: str = ""
    created_at: str = ""
    owner_email: str = ""
    owner_username: str = ""
    owner_display_name: str = ""
    owner_avatar_url: str = ""   # full upload path e.g. "avatars/abc.jpg"


class FeedState(rx.State):
    """State for the public feed page."""
    posts: list[FeedPost] = []
    loading: bool = False
    loaded: bool = False

    def load_feed(self):
        """Fetch the most recent public images from all public profiles."""
        self.loading = True
        try:
            with rx.session() as session:
                # All public images, newest first
                images = session.exec(
                    sqlmodel.select(ImageRecord)
                    .where(ImageRecord.is_public == True)
                    .order_by(ImageRecord.created_at.desc())
                    .limit(FEED_LIMIT)
                ).all()

                # Fetch profile map (email -> UserProfile) for all owners
                owner_emails = list({img.owner_email for img in images})
                profiles = session.exec(
                    sqlmodel.select(UserProfile).where(
                        UserProfile.email.in_(owner_emails),
                        UserProfile.is_public == True,
                        UserProfile.onboarding_complete == True,
                    )
                ).all()
                profile_map = {p.email: p for p in profiles}

            posts = []
            for img in images:
                p = profile_map.get(img.owner_email)
                if not p:
                    continue   # skip images from private/incomplete profiles
                posts.append(FeedPost(
                    image_id=img.id or 0,
                    filename=img.filename,
                    caption=img.caption or "",
                    created_at=(img.created_at[:10] if img.created_at else ""),
                    owner_email=img.owner_email,
                    owner_username=p.username,
                    owner_display_name=p.display_name or p.username,
                    owner_avatar_url=("avatars/" + p.avatar_filename) if p.avatar_filename else "",
                ))
            self.posts = posts
            self.loaded = True
        except Exception:
            self.posts = []
            self.loaded = True
        finally:
            self.loading = False


# ── Feed post card ─────────────────────────────────────────────────────────────

def _feed_avatar(post: rx.Base) -> rx.Component:
    return rx.cond(
        post.owner_avatar_url != "",
        rx.image(
            src=rx.get_upload_url(post.owner_avatar_url),
            width="34px", height="34px",
            border_radius="50%", object_fit="cover",
            border="2px solid rgba(168,85,247,0.4)",
            flex_shrink="0",
        ),
        rx.box(
            rx.icon("user", size=16, color="white"),
            width="34px", height="34px",
            border_radius="50%",
            background="linear-gradient(135deg, #6d28d9, #a855f7)",
            display="flex", align_items="center", justify_content="center",
            flex_shrink="0",
        ),
    )


def feed_post_card(post: rx.Base) -> rx.Component:
    return rx.box(
        rx.vstack(
            # ── Author header ──
            rx.hstack(
                _feed_avatar(post),
                rx.vstack(
                    rx.text(post.owner_display_name, size="2", weight="bold", color="white"),
                    rx.text("@" + post.owner_username, size="1", color="#a78bfa"),
                    spacing="0", align="start",
                ),
                rx.spacer(),
                rx.text(post.created_at, size="1", color="#4b5563"),
                spacing="3", align="center", width="100%",
                cursor="pointer",
                on_click=rx.redirect("/u/" + post.owner_username),
            ),

            # ── Image ──
            rx.box(
                rx.image(
                    src=rx.get_upload_url(post.filename),
                    width="100%",
                    max_height="480px",
                    object_fit="cover",
                    border_radius="12px",
                    display="block",
                ),
                width="100%",
                border_radius="12px",
                overflow="hidden",
                cursor="pointer",
                on_click=rx.redirect("/u/" + post.owner_username),
                _hover={"opacity": "0.93"},
                transition="opacity 0.15s ease",
            ),

            # ── Caption ──
            rx.cond(
                post.caption != "",
                rx.text(
                    post.caption,
                    size="2", color="#d1d5db",
                    line_height="1.6",
                ),
                rx.box(),
            ),

            spacing="3", align="start", width="100%",
        ),
        padding="20px",
        background="rgba(255,255,255,0.04)",
        border="1px solid rgba(124,58,237,0.15)",
        border_radius="20px",
        _hover={
            "border_color": "rgba(168,85,247,0.35)",
            "box_shadow": "0 8px 32px rgba(0,0,0,0.3)",
        },
        transition="all 0.2s ease",
        width="100%",
    )


# ── Feed navbar ────────────────────────────────────────────────────────────────

def feed_nav() -> rx.Component:
    return rx.hstack(
        rx.hstack(
            rx.image(src="/turkey_icon.png", width="30px", height="30px", border_radius="8px"),
            rx.hstack(
                rx.text("turkey", size="3", weight="bold", color="white"),
                rx.text(".app", size="3", weight="bold", color="#a855f7"),
                spacing="0",
            ),
            spacing="2", align="center", cursor="pointer",
            on_click=rx.redirect("/"),
        ),
        rx.hstack(
            rx.button(
                rx.icon("search", size=15),
                "Discover",
                on_click=rx.redirect("/search"),
                size="2", variant="ghost", color_scheme="purple", cursor="pointer",
            ),
            rx.button(
                rx.icon("library-big", size=15),
                "My Library",
                on_click=rx.redirect("/library"),
                size="2",
                background="linear-gradient(135deg, #7c3aed, #a855f7)",
                color="white", border_radius="10px", cursor="pointer",
            ),
            spacing="2", align="center",
        ),
        justify="between",
        align="center",
        padding="0 24px",
        height="56px",
        background="rgba(5,2,16,0.9)",
        border_bottom="1px solid rgba(124,58,237,0.15)",
        backdrop_filter="blur(12px)",
        position="sticky",
        top="0",
        z_index="100",
        width="100%",
    )


# ── Full page ──────────────────────────────────────────────────────────────────

def feed_page() -> rx.Component:
    return rx.box(
        feed_nav(),
        rx.box(
            rx.vstack(
                # Header
                rx.vstack(
                    rx.hstack(
                        rx.icon("rss", size=28, color="#a855f7"),
                        rx.heading(
                            "Public Feed",
                            size="7", color="white", weight="bold", letter_spacing="-0.5px",
                        ),
                        spacing="3", align="center",
                    ),
                    rx.text(
                        "Recent public photos from the community",
                        size="3", color="#6b7280",
                    ),
                    spacing="2", align="center",
                ),

                # Content
                rx.cond(
                    FeedState.loading,
                    rx.center(
                        rx.vstack(
                            rx.spinner(size="3", color="#a855f7"),
                            rx.text("Loading feed…", size="2", color="#6b7280"),
                            spacing="3", align="center",
                        ),
                        padding_y="80px",
                    ),
                    rx.cond(
                        FeedState.loaded,
                        rx.cond(
                            FeedState.posts.length() > 0,
                            rx.vstack(
                                rx.foreach(FeedState.posts, feed_post_card),
                                spacing="5",
                                width="100%",
                            ),
                            # Empty state
                            rx.vstack(
                                rx.icon("image-off", size=52, color="#2d1a4a"),
                                rx.text("No public posts yet", size="4", color="#4b5563", weight="medium"),
                                rx.text(
                                    "Upload photos and make them public to appear here",
                                    size="2", color="#374151",
                                ),
                                rx.button(
                                    rx.icon("library-big", size=15),
                                    "Go to My Library",
                                    on_click=rx.redirect("/library"),
                                    size="3",
                                    background="linear-gradient(135deg, #7c3aed, #a855f7)",
                                    color="white", border_radius="12px", cursor="pointer",
                                    margin_top="4",
                                ),
                                spacing="3", align="center", padding_y="60px",
                            ),
                        ),
                        # Not loaded yet — trigger load
                        rx.box(),
                    ),
                ),

                spacing="8",
                align="center",
                width="100%",
                max_width="640px",
                padding_y="48px",
                padding_x="24px",
            ),
            width="100%",
            display="flex",
            justify_content="center",
        ),
        min_height="100vh",
        background="radial-gradient(ellipse at top, #130a2e 0%, #050210 50%, #020108 100%)",
        width="100%",
    )
