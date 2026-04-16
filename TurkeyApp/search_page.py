"""Search & Discovery page — /search"""

import reflex as rx
from TurkeyApp.profile_state import ProfileState


# ── User result card ───────────────────────────────────────────────────────────

def _avatar_circle() -> rx.Component:
    """Generic initials fallback avatar."""
    return rx.box(
        rx.icon("user", size=22, color="white"),
        width="52px",
        height="52px",
        border_radius="50%",
        background="linear-gradient(135deg, #6d28d9, #a855f7)",
        display="flex",
        align_items="center",
        justify_content="center",
        box_shadow="0 4px 16px rgba(124,58,237,0.4)",
        flex_shrink="0",
    )


def search_result_card(result: rx.Base) -> rx.Component:
    return rx.box(
        rx.hstack(
            # Avatar
            rx.cond(
                result.avatar_url != "",
                rx.image(
                    src=rx.get_upload_url(result.avatar_url),
                    width="52px",
                    height="52px",
                    object_fit="cover",
                    border_radius="50%",
                    border="2px solid rgba(168,85,247,0.4)",
                    flex_shrink="0",
                ),
                _avatar_circle(),
            ),
            # Info
            rx.vstack(
                rx.hstack(
                    rx.text(result.display_name, size="3", weight="bold", color="white"),
                    rx.text("@" + result.username, size="2", color="#a78bfa"),
                    spacing="2",
                    align="baseline",
                    flex_wrap="wrap",
                ),
                rx.cond(
                    result.bio != "",
                    rx.text(
                        result.bio,
                        size="2",
                        color="#9ca3af",
                        overflow="hidden",
                        text_overflow="ellipsis",
                        white_space="nowrap",
                        max_width="360px",
                    ),
                    rx.box(),
                ),
                rx.hstack(
                    rx.cond(
                        result.location != "",
                        rx.hstack(
                            rx.icon("map-pin", size=13, color="#6b7280"),
                            rx.text(result.location, size="1", color="#6b7280"),
                            spacing="1", align="center",
                        ),
                        rx.box(),
                    ),
                    rx.hstack(
                        rx.icon("images", size=13, color="#6b7280"),
                        rx.text(result.image_count_str, " photos", size="1", color="#6b7280"),
                        spacing="1", align="center",
                    ),
                    rx.hstack(
                        rx.icon("calendar", size=13, color="#6b7280"),
                        rx.text("Joined " + result.member_since, size="1", color="#6b7280"),
                        spacing="1", align="center",
                    ),
                    spacing="4",
                    flex_wrap="wrap",
                ),
                spacing="1",
                align="start",
                flex="1",
                min_width="0",
            ),
            # CTA
            rx.button(
                "View Profile",
                rx.icon("arrow-right", size=14),
                on_click=rx.redirect("/u/" + result.username),
                size="2",
                background="linear-gradient(135deg, #7c3aed, #a855f7)",
                color="white",
                border_radius="10px",
                cursor="pointer",
                flex_shrink="0",
                _hover={"opacity": "0.9"},
            ),
            spacing="4",
            align="center",
            width="100%",
        ),
        padding="20px 24px",
        background="rgba(255,255,255,0.04)",
        border="1px solid rgba(124,58,237,0.18)",
        border_radius="16px",
        _hover={
            "border_color": "rgba(168,85,247,0.45)",
            "background": "rgba(124,58,237,0.07)",
            "transform": "translateY(-2px)",
            "box_shadow": "0 8px 28px rgba(0,0,0,0.3)",
        },
        transition="all 0.2s ease",
        width="100%",
        cursor="pointer",
        on_click=rx.redirect("/u/" + result.username),
    )


# ── Empty / loading states ─────────────────────────────────────────────────────

def _empty_state() -> rx.Component:
    return rx.vstack(
        rx.icon("users", size=52, color="#374151"),
        rx.text("No profiles found", size="4", color="#6b7280", weight="medium"),
        rx.text("Try a different name or username", size="2", color="#4b5563"),
        spacing="3",
        align="center",
        padding_y="60px",
    )


def _initial_state() -> rx.Component:
    return rx.vstack(
        rx.box(
            rx.icon("search", size=52, color="#2d1a4a"),
        ),
        rx.text("Find people on turkey.app", size="4", color="#4b5563", weight="medium"),
        rx.text("Search by username or display name", size="2", color="#374151"),
        spacing="3",
        align="center",
        padding_y="60px",
    )


# ── Navbar (re-used style) ──────────────────────────────────────────────────────

def search_nav() -> rx.Component:
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
        rx.hstack(
            rx.button(
                rx.icon("library-big", size=15),
                "My Library",
                on_click=rx.redirect("/library"),
                size="2",
                background="linear-gradient(135deg, #7c3aed, #a855f7)",
                color="white",
                border_radius="10px",
                cursor="pointer",
            ),
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

def search_page() -> rx.Component:
    return rx.box(
        search_nav(),
        rx.box(
            rx.vstack(
                # Header
                rx.vstack(
                    rx.heading(
                        "Discover People",
                        size="8",
                        color="white",
                        weight="bold",
                        letter_spacing="-1px",
                        text_align="center",
                    ),
                    rx.text(
                        "Find photographers and creators on turkey.app",
                        size="3",
                        color="#6b7280",
                        text_align="center",
                    ),
                    spacing="2",
                    align="center",
                ),

                # Search bar
                rx.box(
                    rx.hstack(
                        rx.icon("search", size=20, color="#6b7280", flex_shrink="0"),
                        rx.input(
                            value=ProfileState.search_query,
                            on_change=ProfileState.set_search_query,
                        on_key_up=ProfileState.run_search,
                            placeholder="Search by username or name…",
                            size="3",
                            flex="1",
                            background="transparent",
                            border="none",
                            color="white",
                            _placeholder={"color": "#6b7280"},
                            _focus={"outline": "none", "border": "none", "box_shadow": "none"},
                        ),
                        rx.cond(
                            ProfileState.search_loading,
                            rx.spinner(size="2", color="#a855f7"),
                            rx.button(
                                "Search",
                                on_click=ProfileState.run_search,
                                size="2",
                                background="linear-gradient(135deg, #7c3aed, #a855f7)",
                                color="white",
                                border_radius="10px",
                                cursor="pointer",
                                flex_shrink="0",
                                _hover={"opacity": "0.9"},
                            ),
                        ),
                        spacing="3",
                        align="center",
                        width="100%",
                    ),
                    padding="14px 20px",
                    background="rgba(255,255,255,0.05)",
                    border="1px solid rgba(124,58,237,0.35)",
                    border_radius="16px",
                    width="100%",
                    max_width="620px",
                    backdrop_filter="blur(12px)",
                    _focus_within={
                        "border_color": "rgba(168,85,247,0.7)",
                        "box_shadow": "0 0 0 3px rgba(124,58,237,0.2)",
                    },
                    transition="all 0.2s ease",
                ),

                # Results
                rx.box(
                    rx.cond(
                        ProfileState.search_loading,
                        rx.center(rx.spinner(size="3", color="#a855f7"), padding_y="60px"),
                        rx.cond(
                            ProfileState.search_done,
                            rx.cond(
                                ProfileState.search_results.length() > 0,
                                rx.vstack(
                                    rx.text(
                                        ProfileState.search_results.length().to_string()
                                        + " profile(s) found",
                                        size="2",
                                        color="#6b7280",
                                        align_self="start",
                                    ),
                                    rx.foreach(ProfileState.search_results, search_result_card),
                                    spacing="3",
                                    width="100%",
                                ),
                                _empty_state(),
                            ),
                            _initial_state(),
                        ),
                    ),
                    width="100%",
                    max_width="720px",
                ),

                spacing="8",
                align="center",
                width="100%",
                max_width="760px",
                padding_y="60px",
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
