"""Public profile page — /u/[username]"""

import reflex as rx
from TurkeyApp.profile_state import ProfileState


# ─── Avatar helpers ────────────────────────────────────────────────────────────

def initials_avatar(initials: rx.Var, size: str = "96px") -> rx.Component:
    """Purple gradient circle with user initials."""
    return rx.box(
        rx.text(initials, size="7", weight="bold", color="white"),
        width=size, height=size,
        border_radius="50%",
        background="linear-gradient(135deg, #6d28d9, #a855f7)",
        display="flex",
        align_items="center",
        justify_content="center",
        box_shadow="0 8px 32px rgba(124,58,237,0.5)",
        border="3px solid rgba(168,85,247,0.4)",
        flex_shrink="0",
    )


# ─── Profile image card ────────────────────────────────────────────────────────

def profile_gallery_card(img: dict) -> rx.Component:
    return rx.box(
        rx.image(
            src=rx.get_upload_url(img["filename"]),
            width="100%",
            height="180px",
            object_fit="cover",
            border_radius="12px",
            display="block",
            loading="lazy",
        ),
        rx.cond(
            img["caption"] != "",
            rx.box(
                rx.text(
                    img["caption"],
                    size="1",
                    color="#9ca3af",
                    overflow="hidden",
                    text_overflow="ellipsis",
                    white_space="nowrap",
                ),
                padding="6px 8px 8px",
            ),
            rx.box(
                rx.text(
                    img["original_filename"],
                    size="1",
                    color="#4b5563",
                    overflow="hidden",
                    text_overflow="ellipsis",
                    white_space="nowrap",
                ),
                padding="6px 8px 8px",
            ),
        ),
        background="rgba(255,255,255,0.03)",
        border="1px solid rgba(124,58,237,0.15)",
        border_radius="14px",
        overflow="hidden",
        _hover={
            "border_color": "rgba(168,85,247,0.4)",
            "transform": "translateY(-2px)",
            "box_shadow": "0 8px 24px rgba(0,0,0,0.3)",
        },
        transition="all 0.2s ease",
        cursor="pointer",
    )


# ─── Not found / private ───────────────────────────────────────────────────────

def profile_not_found() -> rx.Component:
    return rx.box(
        rx.vstack(
            rx.icon("user-x", size=56, color="#7c3aed"),
            rx.heading("Profile not found", size="6", color="white"),
            rx.text(
                "This profile is either private or doesn't exist.",
                size="3", color="#6b7280", text_align="center",
            ),
            rx.button(
                rx.icon("home", size=16),
                "Back to turkey.app",
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
            min_height="80vh",
        ),
        width="100%",
        display="flex",
        align_items="center",
        justify_content="center",
    )


# ─── Profile header ────────────────────────────────────────────────────────────

def profile_header() -> rx.Component:
    return rx.box(
        # Banner gradient
        rx.box(
            height="220px",
            background="radial-gradient(ellipse at 30% 50%, #3b0764 0%, #1e0a3c 40%, #080514 100%)",
            position="relative",
            overflow="hidden",
            _after={
                "content": "''",
                "position": "absolute",
                "bottom": "0",
                "left": "0",
                "right": "0",
                "height": "80px",
                "background": "linear-gradient(to bottom, transparent, #050210)",
            },
        ),
        # Avatar + info row
        rx.box(
            rx.hstack(
                rx.box(
                    rx.cond(
                        ProfileState.viewed_avatar_url != "",
                        rx.image(
                            src=ProfileState.viewed_avatar_url,
                            width="96px",
                            height="96px",
                            object_fit="cover",
                            border_radius="50%",
                            border="3px solid rgba(168,85,247,0.5)",
                        ),
                        initials_avatar(ProfileState.viewed_initials, size="96px"),
                    ),
                    margin_top="-52px",
                    position="relative",
                    z_index="1",
                ),
                rx.vstack(
                    rx.hstack(
                        rx.heading(
                            ProfileState.viewed_display_name,
                            size="7", color="white", weight="bold",
                        ),
                        rx.cond(
                            ProfileState.viewed_location != "",
                            rx.hstack(
                                rx.icon("map-pin", size=14, color="#6b7280"),
                                rx.text(ProfileState.viewed_location, size="2", color="#6b7280"),
                                spacing="1", align="center",
                                padding_top="6px",
                            ),
                            rx.box(),
                        ),
                        spacing="4",
                        align="end",
                        flex_wrap="wrap",
                    ),
                    rx.text(
                        "@" + ProfileState.viewed_username,
                        size="3", color="#a78bfa", weight="medium",
                    ),
                    rx.cond(
                        ProfileState.viewed_bio != "",
                        rx.text(
                            ProfileState.viewed_bio,
                            size="3", color="#d1d5db",
                            max_width="560px",
                        ),
                        rx.box(),
                    ),
                    # Follow / Unfollow button (only when not own profile)
                    rx.cond(
                        ~ProfileState.is_own_profile,
                        rx.cond(
                            ProfileState.viewer_is_following,
                            rx.button(
                                rx.icon("user-check", size=15),
                                "Following",
                                on_click=ProfileState.unfollow_user,
                                size="2",
                                variant="outline",
                                color_scheme="purple",
                                border_radius="20px",
                                cursor="pointer",
                                _hover={"background": "rgba(124,58,237,0.15)"},
                            ),
                            rx.button(
                                rx.icon("user-plus", size=15),
                                "Follow",
                                on_click=ProfileState.follow_user,
                                size="2",
                                background="linear-gradient(135deg, #7c3aed, #a855f7)",
                                color="white",
                                border_radius="20px",
                                cursor="pointer",
                                _hover={"opacity": "0.9"},
                            ),
                        ),
                        rx.box(),
                    ),
                    spacing="2", align="start",
                    padding_top="8px",
                ),
                spacing="5",
                align="start",
                padding_x="32px",
                padding_bottom="24px",
                flex_wrap="wrap",
                width="100%",
            ),
        ),
        position="relative",
        width="100%",
        overflow="visible",
    )


# ─── Stats bar ─────────────────────────────────────────────────────────────────

def profile_stats() -> rx.Component:
    def stat(icon: str, val: rx.Var, label: str) -> rx.Component:
        return rx.hstack(
            rx.icon(icon, size=16, color="#a78bfa"),
            rx.text(val, size="3", weight="bold", color="white"),
            rx.text(label, size="2", color="#6b7280"),
            spacing="2", align="center",
        )

    return rx.hstack(
        stat("images", ProfileState.viewed_image_count, "Photos"),
        rx.box(width="1px", height="20px", background="rgba(255,255,255,0.1)"),
        stat("users", ProfileState.viewed_follower_count, "Followers"),
        rx.box(width="1px", height="20px", background="rgba(255,255,255,0.1)"),
        stat("user-check", ProfileState.viewed_following_count, "Following"),
        rx.box(width="1px", height="20px", background="rgba(255,255,255,0.1)"),
        rx.hstack(
            rx.icon("calendar", size=16, color="#a78bfa"),
            rx.text("Joined " + ProfileState.viewed_member_since, size="2", color="#6b7280"),
            spacing="2", align="center",
        ),
        rx.cond(
            ProfileState.viewed_website != "",
            rx.fragment(
                rx.box(width="1px", height="20px", background="rgba(255,255,255,0.1)"),
                rx.hstack(
                    rx.icon("globe", size=16, color="#a78bfa"),
                    rx.link(
                        ProfileState.viewed_website,
                        href=ProfileState.viewed_website,
                        is_external=True,
                        size="2",
                        color="#a78bfa",
                        _hover={"color": "#c4b5fd"},
                    ),
                    spacing="2", align="center",
                ),
            ),
            rx.box(),
        ),
        # Share / copy link button
        rx.spacer(),
        rx.button(
            rx.icon("link", size=14),
            "Copy Link",
            on_click=rx.set_clipboard(
                "https://turkey.app/u/" + ProfileState.viewed_username
            ),
            size="1",
            variant="ghost",
            color_scheme="purple",
            cursor="pointer",
            _hover={"background": "rgba(124,58,237,0.15)"},
        ),
        spacing="5",
        align="center",
        padding="16px 32px",
        background="rgba(255,255,255,0.02)",
        border_top="1px solid rgba(124,58,237,0.12)",
        border_bottom="1px solid rgba(124,58,237,0.12)",
        width="100%",
        flex_wrap="wrap",
        gap="4",
    )


# ─── Gallery grid ──────────────────────────────────────────────────────────────

def profile_gallery() -> rx.Component:
    return rx.box(
        rx.cond(
            ProfileState.viewed_images.length() > 0,
            rx.box(
                rx.grid(
                    rx.foreach(
                        ProfileState.viewed_images,
                        profile_gallery_card,
                    ),
                    columns="4",
                    spacing="4",
                    width="100%",
                ),
                width="100%",
            ),
            rx.vstack(
                rx.icon("image-off", size=48, color="#374151"),
                rx.text("No public images yet.", size="3", color="#4b5563"),
                spacing="3",
                align="center",
                padding_y="60px",
                width="100%",
            ),
        ),
        padding="32px",
        width="100%",
        max_width="1200px",
        margin="0 auto",
    )


# ─── Loading state ─────────────────────────────────────────────────────────────

def profile_loading() -> rx.Component:
    return rx.box(
        rx.vstack(
            rx.spinner(size="3", color="#a855f7"),
            rx.text("Loading profile…", size="2", color="#6b7280"),
            spacing="3", align="center", justify="center",
            min_height="60vh",
        ),
        width="100%",
        display="flex",
        align_items="center",
        justify_content="center",
    )


# ─── Mini top navbar ──────────────────────────────────────────────────────────

def profile_nav() -> rx.Component:
    return rx.hstack(
        rx.hstack(
            rx.image(src="/turkey_icon.png", width="30px", height="30px", border_radius="8px"),
            rx.hstack(
                rx.text("turkey", size="3", weight="bold", color="white"),
                rx.text(".app", size="3", weight="bold", color="#a855f7"),
                spacing="0",
            ),
            spacing="2",
            align="center",
            cursor="pointer",
            on_click=rx.redirect("/"),
        ),
        rx.button(
            rx.icon("log-in", size=15),
            "Open My Library",
            on_click=rx.redirect("/library"),
            size="2",
            background="linear-gradient(135deg, #7c3aed, #a855f7)",
            color="white",
            border_radius="10px",
            cursor="pointer",
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


# ─── Full page ────────────────────────────────────────────────────────────────

def public_profile_page() -> rx.Component:
    return rx.box(
        profile_nav(),
        rx.cond(
            ProfileState.viewed_is_loading,
            profile_loading(),
            rx.cond(
                ProfileState.viewed_not_found,
                profile_not_found(),
                rx.box(
                    profile_header(),
                    profile_stats(),
                    profile_gallery(),
                    width="100%",
                ),
            ),
        ),
        min_height="100vh",
        background="radial-gradient(ellipse at top, #130a2e 0%, #050210 50%, #020108 100%)",
        width="100%",
    )
