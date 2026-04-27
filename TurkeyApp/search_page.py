import reflex as rx
from TurkeyApp.profile_state import ProfileState
from TurkeyApp.upload_state import UploadState
from TurkeyApp.navbar import navbar




def _avatar_circle() -> rx.Component:
    """Generic initials fallback avatar."""
    return rx.box(
        rx.icon("user", size=22, color=UploadState.text_color),
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
                    src=result.full_avatar_url,
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
                    rx.text(result.display_name, size="3", weight="bold", color=UploadState.text_color),
                    rx.text("@", result.username, size="2", color=UploadState.sub_text_color),
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
                            rx.icon("map-pin", size=13, color=UploadState.sub_text_color),
                            rx.text(result.location, size="1", color=UploadState.sub_text_color),
                            spacing="1", align="center",
                        ),
                        rx.box(),
                    ),
                    rx.hstack(
                        rx.icon("images", size=13, color=UploadState.sub_text_color),
                        rx.text(result.image_count_str, " photos", size="1", color=UploadState.sub_text_color),
                        spacing="1", align="center",
                    ),
                    rx.hstack(
                        rx.icon("users", size=13, color=UploadState.sub_text_color),
                        rx.text(result.follower_count.to_string(), " followers", size="1", color=UploadState.sub_text_color),
                        spacing="1", align="center",
                    ),
                    rx.hstack(
                        rx.icon("calendar", size=13, color=UploadState.sub_text_color),
                        rx.text("Joined ", result.member_since, size="1", color=UploadState.sub_text_color),
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
       
            rx.button(
                "View Profile",
                rx.icon("arrow-right", size=14),
                on_click=ProfileState.goto_profile(result.username),
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
        background="#f9fafb",
        border="1px solid " + UploadState.border_color,
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
        on_click=ProfileState.goto_profile(result.username),
    )


def semantic_image_card(result: rx.Base) -> rx.Component:
    """Card for displaying an AI search result."""
    return rx.box(
        rx.vstack(
            rx.image(
                src=result.full_url,
                width="100%",
                height="180px",
                object_fit="cover",
                border_radius="12px",
            ),
            rx.vstack(
                rx.text(
                    rx.cond(result.caption != "", result.caption, "Untitled"),
                    size="2", weight="bold", color=UploadState.text_color, 
                    white_space="nowrap", overflow="hidden", text_overflow="ellipsis", width="100%"
                ),
                rx.hstack(
                    rx.icon("user", size=11, color=UploadState.sub_text_color),
                    rx.text("@" + result.owner_username, size="1", color=UploadState.sub_text_color),
                    spacing="1", align="center",
                ),
                spacing="1", align="start", width="100%",
            ),
            spacing="2",
        ),
        padding="12px",
        background=UploadState.bg_card,
        border="1px solid " + UploadState.border_color,
        border_radius="18px",
        transition="all 0.2s ease",
        _hover={"transform": "scale(1.02)", "border_color": "#7c3aed", "cursor": "pointer"},
    )


# ── Empty / loading states ─────────────────────────────────────────────────────

def _empty_state() -> rx.Component:
    return rx.vstack(
        rx.icon("users", size=52, color="#374151"),
        rx.text("No profiles found", size="4", color=UploadState.sub_text_color, weight="medium"),
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




# ── Full page ──────────────────────────────────────────────────────────────────

def search_page() -> rx.Component:
    return rx.box(
        navbar(active_page="search"),
        rx.box(
            rx.vstack(
                # Header
                rx.vstack(
                    rx.heading(
                        "Discover People",
                        size="8",
                        color=UploadState.text_color,
                        weight="bold",
                        letter_spacing="-1px",
                        text_align="center",
                    ),
                    rx.text(
                        "Find photographers and creators on turkey.app",
                        size="3",
                        color=UploadState.sub_text_color,
                        text_align="center",
                    ),
                    spacing="2",
                    align="center",
                ),

                # Mode Switcher
                rx.segmented_control.root(
                    rx.segmented_control.item("People", value="profiles"),
                    rx.segmented_control.item("Images (AI)", value="images"),
                    value=ProfileState.search_mode,
                    on_change=ProfileState.set_search_mode,
                    variant="surface",
                    radius="full",
                    size="2",
                ),
                rx.box(
                    rx.hstack(
                        rx.icon("search", size=20, color=UploadState.sub_text_color, flex_shrink="0"),
                        rx.input(
                            value=ProfileState.search_query,
                            on_change=ProfileState.set_search_query,
                            on_key_up=lambda key: rx.cond(
                                key == "Enter",
                                ProfileState.run_search,
                                rx.noop(),
                            ),
                            placeholder=rx.cond(
                                ProfileState.search_mode == "images",
                                "Describe what you're looking for (e.g. 'purple sunset')...",
                                "Search by username or name...",
                            ),
                            size="3",
                            flex="1",
                            background="transparent",
                            border="none",
                            color=UploadState.text_color,
                            _placeholder={"color": UploadState.sub_text_color},
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
                    background=UploadState.input_bg,
                    border=f"1px solid {UploadState.border_color}",
                    border_radius="99px",
                    width="100%",
                    max_width="620px",
                    _focus_within={
                        "background": rx.cond(UploadState.is_dark_mode, "black", "white"),
                        "border_color": "#7c3aed",
                        "box_shadow": "0 0 0 3px rgba(124, 58, 237, 0.1)",
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
                            rx.box(
                                rx.cond(
                                    ProfileState.search_mode == "images",
                                    # ─── AI Image Grid ───
                                    rx.cond(
                                        ProfileState.image_search_results.length() > 0,
                                        rx.grid(
                                            rx.foreach(ProfileState.image_search_results, semantic_image_card),
                                            columns=rx.breakpoints(initial="2", sm="3", md="4"),
                                            spacing="4",
                                            width="100%",
                                        ),
                                        rx.center(
                                            rx.vstack(
                                                rx.icon("search-slash", size=48, opacity="0.3"),
                                                rx.text("No matching images found.", color=UploadState.sub_text_color),
                                                spacing="2",
                                            ),
                                            padding_y="60px",
                                        ),
                                    ),
                                    # ─── Profile List ───
                                    rx.cond(
                                        ProfileState.search_results.length() > 0,
                                        rx.vstack(
                                            rx.foreach(ProfileState.search_results, search_result_card),
                                            spacing="4",
                                            width="100%",
                                        ),
                                        rx.center(
                                            rx.vstack(
                                                rx.icon("user-x", size=48, opacity="0.3"),
                                                rx.text("No profiles found matching '", ProfileState.search_query, "'", color=UploadState.sub_text_color),
                                                spacing="2",
                                            ),
                                            padding_y="60px",
                                        ),
                                    ),
                                ),
                                width="100%",
                            ),
                            # ─── Suggestions (initial state) ───
                            rx.vstack(
                                rx.hstack(
                                    rx.icon("sparkles", size=18, color="#a855f7"),
                                    rx.text("Suggested for you", size="3", weight="bold", color=UploadState.text_color),
                                    spacing="2", align="center",
                                    width="100%",
                                    margin_top="20px",
                                ),
                                rx.cond(
                                    ProfileState.suggested_loading,
                                    rx.center(rx.spinner(size="2", color="#a855f7"), padding_y="30px"),
                                    rx.cond(
                                        ProfileState.suggested_creators.length() > 0,
                                        rx.vstack(
                                            rx.foreach(ProfileState.suggested_creators, search_result_card),
                                            spacing="3",
                                            width="100%",
                                        ),
                                        _initial_state(),
                                    ),
                                ),
                                spacing="4", width="100%",
                            ),
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
        background=UploadState.bg_theme,
        width="100%",
    )
