"""Public Feed page — /feed  Shows the most-recent public images from all users."""

import reflex as rx
import sqlmodel
from datetime import datetime
from pydantic import BaseModel
from TurkeyApp.models import ImageRecord, UserProfile, Follow, Like
from TurkeyApp.profile_state import ProfileState
from TurkeyApp.navbar import navbar


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
    owner_avatar_url: str = ""   # full upload path
    image_url: str = ""
    like_count: int = 0
    viewer_has_liked: bool = False
    tags: list[dict] = []   # list of {"name": str, "color": str}


class FeedState(rx.State):
    """State for the public feed page."""
    posts: list[FeedPost] = []
    loading: bool = False
    loaded: bool = False
    active_tab: str = "all"   # "all" | "following"
    tag_filter: str = ""     # tag name to filter by
    trending_tags: list[dict] = []

    # ── helpers ───────────────────────────────────────────────────────────────

    async def _viewer_email(self) -> str:
        """Returns the logged-in user's email from ProfileState cookie."""
        prof_state = await self.get_state(ProfileState)
        return prof_state.own_email  # type: ignore[attr-defined]

    def _build_posts(self, images, profile_map, viewer_email: str, session) -> list[FeedPost]:
        """Convert image rows + profile map into FeedPost objects with like data."""
        image_ids = [img.id for img in images if img.id is not None]

        # Bulk fetch like counts
        like_rows = session.exec(
            sqlmodel.select(Like.image_id, sqlmodel.func.count(Like.id).label("cnt"))
            .where(Like.image_id.in_(image_ids))
            .group_by(Like.image_id)
        ).all()
        like_counts = {row[0]: row[1] for row in like_rows}

        # Fetch which images the viewer already liked
        viewer_liked: set[int] = set()
        if viewer_email:
            liked_rows = session.exec(
                sqlmodel.select(Like.image_id)
                .where(Like.liker_email == viewer_email, Like.image_id.in_(image_ids))
            ).all()
            viewer_liked = set(liked_rows)

        posts = []
        for img in images:
            p = profile_map.get(img.owner_email)
            if not p:
                continue
            posts.append(FeedPost(
                image_id=img.id or 0,
                filename=img.filename,
                caption=img.caption or "",
                created_at=(img.created_at[:10] if img.created_at else ""),
                owner_email=img.owner_email,
                owner_username=p.username,
                owner_display_name=p.display_name or p.username,
                owner_avatar_url=("/uploaded_files/avatars/" + p.avatar_filename) if p.avatar_filename else "",
                image_url="/uploaded_files/" + img.filename,
                like_count=like_counts.get(img.id or 0, 0),
                viewer_has_liked=(img.id in viewer_liked),
                tags=[] # will be populated in bulk if possible, or later
            ))
        
        # Load tags for all posts in bulk
        from TurkeyApp.models import Tag, ImageTag
        all_tags = session.exec(
            sqlmodel.select(Tag, ImageTag.image_id)
            .join(ImageTag, ImageTag.tag_id == Tag.id)
            .where(ImageTag.image_id.in_(image_ids))
        ).all()
        
        tag_map = {}
        for tag, img_id in all_tags:
            if img_id not in tag_map:
                tag_map[img_id] = []
            tag_map[img_id].append({"name": tag.name, "color": tag.color})
            
        for post in posts:
            post.tags = tag_map.get(post.image_id, [])

        return posts

    # ── loaders ───────────────────────────────────────────────────────────────

    async def load_feed(self):
        """Fetch the most recent public images (respects active tab)."""
        self.loading = True
        try:
            viewer = await self._viewer_email()
            with rx.session() as session:
                if self.active_tab == "following" and viewer:
                    # Only images from users the viewer follows
                    following_emails = [
                        row for row in session.exec(
                            sqlmodel.select(Follow.following_email)
                            .where(
                                Follow.follower_email == viewer,
                                Follow.status == "accepted"
                            )
                        ).all()
                    ]
                    images = session.exec(
                        sqlmodel.select(ImageRecord)
                        .where(
                            ImageRecord.is_public == True,
                            ImageRecord.owner_email.in_(following_emails),
                        )
                        .order_by(ImageRecord.created_at.desc())
                        .limit(FEED_LIMIT)
                    ).all()
                else:
                    images = session.exec(
                        sqlmodel.select(ImageRecord)
                        .where(ImageRecord.is_public == True)
                        .order_by(ImageRecord.created_at.desc())
                        .limit(FEED_LIMIT)
                    ).all()

                owner_emails = list({img.owner_email for img in images})
                profiles = session.exec(
                    sqlmodel.select(UserProfile).where(
                        UserProfile.email.in_(owner_emails),
                        UserProfile.is_public == True,
                        UserProfile.onboarding_complete == True,
                    )
                ).all()
                profile_map = {p.email: p for p in profiles}
                self.posts = self._build_posts(images, profile_map, viewer, session)
                
                # Filter by tag if requested
                if self.tag_filter:
                    self.posts = [p for p in self.posts if any(t["name"].lower() == self.tag_filter.lower() for t in p.tags)]
                
                # Load trending
                self.load_trending_tags()
            self.loaded = True
        except Exception:
            self.posts = []
            self.loaded = True
        finally:
            self.loading = False

    def switch_tab(self, tab: str):
        self.active_tab = tab
        self.tag_filter = ""
        self.loaded = False
        self.posts = []
        return FeedState.load_feed

    def set_tag_filter(self, tag_name: str):
        self.tag_filter = tag_name
        self.loaded = False
        self.posts = []
        return FeedState.load_feed

    def clear_tag_filter(self):
        self.tag_filter = ""
        self.loaded = False
        self.posts = []
        return FeedState.load_feed

    def load_trending_tags(self):
        """Fetch top 8 most used tags for sidebar."""
        from TurkeyApp.models import Tag, ImageTag, ImageRecord
        with rx.session() as session:
            # Count tags associated with PUBLIC images
            rows = session.exec(
                sqlmodel.select(Tag, sqlmodel.func.count(ImageTag.id).label("cnt"))
                .join(ImageTag, ImageTag.tag_id == Tag.id)
                .join(ImageRecord, ImageRecord.id == ImageTag.image_id)
                .where(ImageRecord.is_public == True)
                .group_by(Tag.id)
                .order_by(sqlmodel.desc("cnt"))
                .limit(8)
            ).all()
            self.trending_tags = [{"name": r[0].name, "color": r[0].color, "count": r[1]} for r in rows]

    # ── like / unlike ─────────────────────────────────────────────────────────

    async def toggle_like(self, image_id: int):
        viewer = await self._viewer_email()
        if not viewer or image_id == 0:
            return
        with rx.session() as session:
            existing = session.exec(
                sqlmodel.select(Like).where(
                    Like.liker_email == viewer,
                    Like.image_id == image_id,
                )
            ).first()
            if existing:
                session.delete(existing)
                session.commit()
                delta = -1
                now_liked = False
            else:
                session.add(Like(
                    liker_email=viewer,
                    image_id=image_id,
                    created_at=datetime.utcnow().strftime("%Y-%m-%d"),
                ))
                # Get owner email for notification
                img_owner_email = session.exec(
                    sqlmodel.select(ImageRecord.owner_email).where(ImageRecord.id == image_id)
                ).first()
                session.commit()
                delta = 1
                now_liked = True
                
                # Notify owner of the like
                if img_owner_email and img_owner_email != viewer:
                    prof_state = await self.get_state(ProfileState)
                    session.add(Notification(
                        to_email=img_owner_email,
                        from_email=viewer,
                        from_username=prof_state.own_username,
                        type="like",
                        message=f"@{prof_state.own_username} liked your photo",
                        created_at=datetime.utcnow().strftime("%Y-%m-%d %H:%M:%S"),
                    ))
                    session.commit()

        # Update in-place without reloading the whole feed
        self.posts = [
            FeedPost(
                **{
                    **post.dict(),
                    "like_count": max(0, post.like_count + delta),
                    "viewer_has_liked": now_liked,
                }
            ) if post.image_id == image_id else post
            for post in self.posts
        ]


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
                rx.link(
                    _feed_avatar(post),
                    href="/u/" + post.owner_username,
                ),
                rx.vstack(
                    rx.link(
                        rx.text(post.owner_display_name, size="2", weight="bold", color="#111827"),
                        href="/u/" + post.owner_username,
                        text_decoration="none",
                        _hover={"text_decoration": "underline"},
                    ),
                    rx.text("@" + post.owner_username, size="1", color="#6b7280"),
                    spacing="0", align="start",
                ),
                rx.spacer(),
                rx.text(post.created_at, size="1", color="#9ca3af"),
                spacing="3", align="center", width="100%",
                cursor="pointer",
                on_click=rx.redirect("/u/" + post.owner_username),
            ),

            # ── Image ──
            rx.box(
                rx.image(
                    src=post.image_url,
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

            rx.cond(
                post.caption != "",
                rx.text(
                    post.caption,
                    size="2", color="#374151",
                    line_height="1.6",
                ),
                rx.box(),
            ),

            # ── Tags ──
            rx.cond(
                post.tags.length() > 0,
                rx.hstack(
                    rx.foreach(
                        post.tags,
                        lambda t: rx.box(
                            rx.hstack(
                                rx.box(width="6px", height="6px", border_radius="50%", background=t["color"]),
                                rx.text("#", t["name"], size="1", weight="bold"),
                                spacing="1", align="center",
                            ),
                            padding="3px 8px",
                            background="#f3f4f6",
                            color="#4b5563",
                            border_radius="12px",
                            cursor="pointer",
                            on_click=lambda: FeedState.set_tag_filter(t["name"]),
                            _hover={"background": "#e5e7eb", "color": "#111827"},
                            transition="all 0.2s ease",
                        )
                    ),
                    spacing="2", flex_wrap="wrap", width="100%",
                ),
                rx.box(),
            ),

            # ── Like bar ──
            rx.hstack(
                rx.cond(
                    ProfileState.is_guest,
                    # Guest: greyed heart redirects to sign-in
                    rx.button(
                        rx.icon("heart", size=18, color="#4b5563"),
                        rx.text(post.like_count.to_string(), size="2", color="#4b5563"),
                        on_click=rx.redirect("/"),
                        variant="ghost",
                        size="2",
                        cursor="pointer",
                        border_radius="10px",
                        padding_x="10px",
                        title="Sign in to like",
                        _hover={"background": "rgba(255,255,255,0.05)"},
                    ),
                    # Authenticated: full like toggle
                    rx.button(
                        rx.cond(
                            post.viewer_has_liked,
                            rx.icon("heart", size=18, color="#f43f5e"),
                            rx.icon("heart", size=18, color="#6b7280"),
                        ),
                        rx.text(
                            post.like_count.to_string(),
                            size="2",
                            color=rx.cond(post.viewer_has_liked, "#f43f5e", "#6b7280"),
                            weight=rx.cond(post.viewer_has_liked, "bold", "regular"),
                        ),
                        on_click=FeedState.toggle_like(post.image_id),
                        variant="ghost",
                        size="2",
                        cursor="pointer",
                        border_radius="10px",
                        padding_x="10px",
                        _hover={"background": "rgba(244,63,94,0.1)"},
                        transition="all 0.15s ease",
                    ),
                ),
                rx.spacer(),
                rx.button(
                    rx.icon("arrow-up-right", size=15, color="#6b7280"),
                    "View profile",
                    on_click=ProfileState.goto_profile(post.owner_username),
                    variant="ghost",
                    size="1",
                    color="#6b7280",
                    cursor="pointer",
                    _hover={"color": "#7c3aed"},
                ),
                rx.button(
                    rx.icon("download", size=15, color="#6b7280"),
                    "Save",
                    on_click=rx.download(post.image_url),
                    variant="ghost",
                    size="1",
                    color="#6b7280",
                    cursor="pointer",
                    _hover={"color": "#10b981", "background": "rgba(16,185,129,0.08)"},
                ),
                width="100%",
                align="center",
                padding_top="2px",
            ),

            spacing="3", align="start", width="100%",
        ),
        padding="20px",
        background="#ffffff",
        border="1px solid #f1f1f1",
        border_radius="20px",
        _hover={
            "border_color": "rgba(168,85,247,0.35)",
            "box_shadow": "0 8px 32px rgba(0,0,0,0.3)",
        },
        transition="all 0.2s ease",
        width="100%",
    )


# ── Sidebar Components ─────────────────────────────────────────────────────────

def suggested_creators_sidebar() -> rx.Component:
    """Sidebar section showing recommended accounts."""
    return rx.vstack(
        rx.hstack(
            rx.icon("sparkles", size=18, color="#a855f7"),
            rx.text("Suggested Creators", size="3", weight="bold", color="#111827"),
            spacing="2", align="center",
        ),
        rx.cond(
            ProfileState.suggested_loading,
            rx.center(rx.spinner(size="2", color="#a855f7"), padding_y="20px"),
            rx.vstack(
                rx.foreach(
                    ProfileState.suggested_creators,
                    lambda p: rx.hstack(
                        rx.box(
                            rx.cond(
                                p.avatar_url != "",
                                rx.image(src=p.full_avatar_url, width="40px", height="40px", border_radius="50%", object_fit="cover"),
                                rx.center(rx.icon("user", size=16), width="40px", height="40px", border_radius="50%", background="#f3f4f6"),
                            ),
                            flex_shrink="0",
                        ),
                        rx.vstack(
                            rx.text(p.display_name, size="2", weight="bold", color="#111827", line_limit=1),
                            rx.text("@" + p.username, size="1", color="#6b7280"),
                            spacing="0", align="start",
                        ),
                        rx.spacer(),
                        rx.button(
                            rx.icon("arrow-right", size=12),
                            on_click=ProfileState.goto_profile(p.username),
                            size="1", variant="ghost", color_scheme="purple",
                        ),
                        spacing="3", align="center", width="100%", padding="8px",
                        border_radius="12px", _hover={"background": "#f9fafb"},
                        cursor="pointer",
                        on_click=ProfileState.goto_profile(p.username),
                    )
                ),
                spacing="1", width="100%",
            ),
        ),
        width="100%", padding="20px", background="#ffffff", border="1px solid #f1f1f1", border_radius="20px",
    )


def trending_tags_sidebar() -> rx.Component:
    """Sidebar section for popular topics."""
    return rx.vstack(
        rx.hstack(
            rx.icon("trending-up", size=18, color="#7c3aed"),
            rx.text("Popular Topics", size="3", weight="bold", color="#111827"),
            spacing="2", align="center",
        ),
        rx.cond(
            FeedState.trending_tags.length() > 0,
            rx.flex(
                rx.foreach(
                    FeedState.trending_tags,
                    lambda t: rx.box(
                        rx.hstack(
                            rx.box(width="4px", height="4px", border_radius="100%", background=t["color"]),
                            rx.text(t["name"], size="2", weight="medium"),
                            spacing="2", align="center"
                        ),
                        padding="6px 12px", background="#f9fafb", border_radius="12px",
                        cursor="pointer", on_click=lambda: FeedState.set_tag_filter(t["name"]),
                        _hover={"background": "rgba(124,58,237,0.08)", "color": "#7c3aed"},
                        transition="all 0.2s ease",
                        margin="4px",
                    )
                ),
                flex_wrap="wrap", width="100%", margin="-4px",
            ),
            rx.text("No trends yet", size="2", color="#9ca3af", padding_y="10px"),
        ),
        width="100%", padding="20px", background="#ffffff", border="1px solid #f1f1f1", border_radius="20px",
    )


# ── Tab bar ────────────────────────────────────────────────────────────────────

def feed_tabs() -> rx.Component:
    active_style = {
        "background": "linear-gradient(135deg,#7c3aed,#a855f7)",
        "color": "white",
        "border_radius": "10px",
    }
    ghost_style = {
        "background": "transparent",
        "color": "#6b7280",
        "border_radius": "10px",
    }
    return rx.hstack(
        rx.button(
            rx.icon("rss", size=15),
            "All",
            on_click=FeedState.switch_tab("all"),
            size="2",
            cursor="pointer",
            style=rx.cond(FeedState.active_tab == "all", active_style, ghost_style),
            _hover={"opacity": "0.85"},
        ),
        rx.button(
            rx.icon("users", size=15),
            "Following",
            on_click=FeedState.switch_tab("following"),
            size="2",
            cursor="pointer",
            style=rx.cond(FeedState.active_tab == "following", active_style, ghost_style),
            _hover={"opacity": "0.85"},
        ),
        spacing="1",
        padding="4px",
        background="#f1f1f1",
        border="1px solid #e2e2e2",
        border_radius="13px",
    )





# ── Full page ──────────────────────────────────────────────────────────────────

def feed_page() -> rx.Component:
    return rx.box(
        navbar(active_page="feed"),
        rx.box(
            rx.hstack(
                # Main Feed
                rx.vstack(
                    # Header
                    rx.vstack(
                        rx.hstack(
                            rx.icon("rss", size=28, color="#a855f7"),
                            rx.heading(
                                "Feed",
                                size="7", color="#111827", weight="bold", letter_spacing="-0.5px",
                            ),
                            spacing="3", align="center",
                        ),
                        rx.text(
                            "Recent public photos from the community",
                            size="3", color="#6b7280",
                        ),
                        spacing="2", align="center",
                    ),

                    # Active Tag Indicator
                    rx.cond(
                        FeedState.tag_filter != "",
                        rx.hstack(
                            rx.text("Filtering by topic:", size="2", color="#6b7280"),
                            rx.box(
                                rx.hstack(
                                    rx.icon("tag", size=14),
                                    rx.text("#", FeedState.tag_filter, size="2", weight="bold"),
                                    rx.icon("x", size=14, cursor="pointer", on_click=FeedState.clear_tag_filter),
                                    spacing="2", align="center",
                                ),
                                padding="4px 12px",
                                background="rgba(124,58,237,0.1)",
                                color="#7c3aed",
                                border_radius="20px",
                            ),
                            rx.box(),
                        ),
                        rx.box(),
                    ),

                    # Tab switcher
                    feed_tabs(),

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
                                    rx.cond(
                                        FeedState.active_tab == "following",
                                        rx.vstack(
                                            rx.icon("users", size=52, color="#2d1a4a"),
                                            rx.text("No posts from people you follow", size="4", color="#4b5563", weight="medium"),
                                            rx.text("Follow some creators to see their photos here", size="2", color="#374151"),
                                            rx.button(
                                                rx.icon("search", size=15),
                                                "Discover People",
                                                on_click=rx.redirect("/search"),
                                                size="3",
                                                background="linear-gradient(135deg, #7c3aed, #a855f7)",
                                                color="white", border_radius="12px", cursor="pointer",
                                                margin_top="4",
                                            ),
                                            spacing="3", align="center", padding_y="60px",
                                        ),
                                        rx.vstack(
                                            rx.icon("image-off", size=52, color="#2d1a4a"),
                                            rx.text("No public posts yet", size="4", color="#4b5563", weight="medium"),
                                            rx.text("Upload photos and make them public to appear here", size="2", color="#374151"),
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
                                    width="100%",
                                ),
                            ),
                            rx.box(),
                        ),
                    ),

                    spacing="6",
                    align="center",
                    width="100%",
                    max_width="640px",
                    padding_y="48px",
                    padding_x="24px",
                ),
                
                # Sidebar
                rx.vstack(
                    suggested_creators_sidebar(),
                    trending_tags_sidebar(),
                    rx.vstack(
                        rx.text("About turkey.app", size="1", color="#9ca3af", weight="bold", letter_spacing="1px"),
                        rx.text("A premium social media experience for photographers and collectors.", size="1", color="#6b7280"),
                        spacing="2", align="start",
                        padding="20px", background="#f9fafb", border_radius="20px", width="100%",
                    ),
                    spacing="6",
                    width="320px",
                    padding_y="48px",
                    display=rx.breakpoints(initial="none", lg="flex"),
                ),
                
                spacing="8",
                align="start",
                justify="center",
                width="100%",
                max_width="1100px",
            ),
            width="100%",
            display="flex",
            justify_content="center",
        ),
        min_height="100vh",
        background="#ffffff",
        width="100%",
    )
