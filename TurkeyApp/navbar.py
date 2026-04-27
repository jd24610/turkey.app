"""Unified Navbar component — Pinterest style."""

import reflex as rx
# We import from TurkeyApp.TurkeyApp import State to get the main state if needed
from TurkeyApp.profile_state import ProfileState
from TurkeyApp.upload_state import UploadState
from TurkeyApp.state import State

def _nav_link(label: str, icon: str, route: str, is_active: bool = False) -> rx.Component:
    """A pill-shaped navigation link."""
    return rx.link(
        rx.hstack(
            rx.icon(icon, size=16),
            rx.text(label, size="2", weight="bold"),
            spacing="2",
            align="center",
            padding="10px 18px",
            border_radius="99px",
            background=rx.cond(is_active, UploadState.text_color, "transparent"),
            color=rx.cond(is_active, UploadState.nav_bg, UploadState.text_color),
            _hover={"opacity": "0.75"},
            transition="all 0.2s ease",
        ),
        href=route,
        text_decoration="none",
    )

def _profile_avatar_btn() -> rx.Component:
    """Compact avatar+name chip in the navbar."""
    from TurkeyApp.TurkeyApp import State # Circular import protection if needed
    
    return rx.cond(
        ProfileState.onboarding_complete,
        rx.link(
            rx.hstack(
                # Avatar or initials
                rx.cond(
                    ProfileState.own_avatar_url != "",
                    rx.image(
                        src=ProfileState.own_avatar_url,
                        width="28px", height="28px",
                        object_fit="cover",
                        border_radius="50%",
                        border="1.5px solid rgba(168,85,247,0.5)",
                        flex_shrink="0",
                    ),
                    rx.box(
                        rx.text(ProfileState.own_initials, size="1", weight="bold", color=UploadState.nav_bg),
                        width="28px", height="28px",
                        border_radius="50%",
                        background="linear-gradient(135deg, #7c3aed, #a855f7)",
                        display="flex", align_items="center", justify_content="center",
                        box_shadow="0 4px 12px rgba(124,58,237,0.2)",
                        flex_shrink="0",
                    ),
                ),
                rx.text(ProfileState.own_display_name, size="2", weight="bold", color=UploadState.text_color),
                spacing="2", align="center",
                padding="6px 14px 6px 6px",
                border_radius="99px",
                background="rgba(0,0,0,0.04)",
                _hover={"background": "rgba(0,0,0,0.08)"},
                transition="all 0.15s ease",
            ),
            href="/u/" + ProfileState.own_username,
            text_decoration="none",
        ),
        # Fallback
        rx.cond(
            State.user_name != "",
            rx.hstack(
                rx.icon("circle-user-round", size=18, color="#7c3aed"),
                rx.text(State.user_name, size="2", color=UploadState.text_color),
                spacing="2", align="center",
                padding="8px 16px",
                border_radius="99px",
                background="rgba(0,0,0,0.04)",
            ),
            rx.box(),
        ),
    )

def navbar(active_page: str = "") -> rx.Component:
    """The unified navbar component."""
    from TurkeyApp.TurkeyApp import State # Local import

    return rx.hstack(
        # ── Left: Logo ──────────────────────────────────────────────────
        rx.link(
            rx.hstack(
                rx.image(
                    src="/turkey_icon.png",
                    width="32px", height="32px",
                    object_fit="cover",
                    border_radius="9px",
                    box_shadow="0 4px 12px rgba(124,58,237,0.2)",
                ),
                rx.hstack(
                    rx.text("turkey", size="4", weight="bold", color=UploadState.text_color, letter_spacing="-0.5px"),
                    rx.text(".app", size="4", weight="bold", color="#7c3aed", letter_spacing="-0.5px"),
                    spacing="0",
                ),
                spacing="3", align="center",
            ),
            href="/",
            text_decoration="none",
            _hover={"opacity": "0.8"},
        ),

        # ── Center-Left: Navigation Links ───────────────────────────────
        rx.hstack(
            _nav_link("Library", "library-big", "/library", active_page == "library"),
            _nav_link("Feed", "rss", "/feed", active_page == "feed"),
            _nav_link("Discover", "search", "/search", active_page == "search"),
            spacing="1",
            margin_left="20px",
        ),

        # ── Center: Search Bar (Pinterest style) ─────────────────────────
        rx.hstack(
            rx.icon("search", size=16, color=UploadState.sub_text_color),
            rx.input(
                placeholder="Search...",
                value=ProfileState.search_query,
                on_change=ProfileState.set_search_query,
                on_key_down=lambda key: rx.cond(
                    key == "Enter",
                    ProfileState.global_search_submit(),
                    rx.noop(),
                ),
                size="2",
                variant="soft",
                background="transparent",
                border="none",
                color=UploadState.text_color,
                _placeholder={"color": UploadState.sub_text_color},
                _focus={"outline": "none", "border": "none", "box_shadow": "none"},
                flex="1",
                padding="0",
            ),
            background="#f1f1f1",
            padding="0 18px",
            height="44px",
            border_radius="99px",
            display=["none", "none", "flex", "flex"], # Hide on small screens
            flex="1",
            margin="0 40px",
            align="center",
            spacing="2",
            border="1px solid transparent",
            _hover={"background": "#e2e2e2"},
            _focus_within={"background": UploadState.nav_bg, "border_color": UploadState.text_color, "box_shadow": "0 0 0 4px rgba(0,0,0,0.05)"},
            transition="all 0.2s ease",
            cursor="text",
        ),
        
        rx.spacer(display=["flex", "flex", "none", "none"]), # Spacer for mobile

        # ── Right: User Actions ─────────────────────────────────────────
        rx.hstack(
            # Guest view: Login button
            rx.cond(
                ProfileState.is_guest,
                rx.button(
                    "Sign In",
                    on_click=rx.redirect("/"),
                    size="2",
                    background=UploadState.text_color,
                    color=UploadState.nav_bg,
                    border_radius="99px",
                    padding="0 24px",
                    cursor="pointer",
                    _hover={"background": "#374151"},
                ),
                # Authenticated view: Avatar + Preferences
                rx.hstack(
                    # ── Notifications (Bell) ────────────────────────
                    rx.popover.root(
                        rx.popover.trigger(
                            rx.box(
                                rx.icon("bell", size=18, color=UploadState.text_color),
                                rx.cond(
                                    ProfileState.unread_notifications_count > 0,
                                    rx.box(
                                        rx.text(
                                            ProfileState.unread_notifications_count.to_string(),
                                            size="1", weight="bold", color=UploadState.nav_bg,
                                        ),
                                        position="absolute", top="-4px", right="-4px",
                                        background="#f43f5e",
                                        border_radius="50%",
                                        width="14px", height="14px",
                                        display="flex", align_items="center", justify_content="center",
                                    ),
                                    rx.box(),
                                ),
                                position="relative",
                                cursor="pointer",
                                padding="8px",
                                border_radius="50%",
                                _hover={"background": "rgba(0,0,0,0.05)"},
                                on_click=ProfileState.toggle_notifications,
                            )
                        ),
                        rx.popover.content(
                            rx.vstack(
                                rx.text("Notifications", size="3", weight="bold", color=UploadState.text_color),
                                rx.divider(),
                                rx.cond(
                                    ProfileState.notifications.length() > 0,
                                    rx.vstack(
                                        rx.foreach(
                                            ProfileState.notifications,
                                            lambda n: rx.hstack(
                                                rx.vstack(
                                                    rx.text(n.message, size="2", color=UploadState.text_color, width="100%"),
                                                    rx.text(n.created_at, size="1", color=UploadState.sub_text_color),
                                                    spacing="1", align="start",
                                                    width="160px",
                                                ),
                                                rx.spacer(),
                                                rx.cond(
                                                    n.status == "unread",
                                                    rx.hstack(
                                                        rx.button(
                                                            rx.icon("check", size=14),
                                                            on_click=ProfileState.accept_follow_request(n.id),
                                                            size="1", color_scheme="green", variant="soft",
                                                            cursor="pointer",
                                                        ),
                                                        rx.button(
                                                            rx.icon("x", size=14),
                                                            on_click=ProfileState.decline_follow_request(n.id),
                                                            size="1", color_scheme="red", variant="soft",
                                                            cursor="pointer",
                                                        ),
                                                        spacing="2",
                                                    ),
                                                    rx.text(n.status.capitalize(), size="1", color="#9ca3af", italic=True),
                                                ),
                                                spacing="3", align="center", width="100%", padding_y="8px",
                                            )
                                        ),
                                        spacing="0", width="100%",
                                    ),
                                    rx.center(
                                        rx.text("No notifications", size="2", color=UploadState.sub_text_color),
                                        padding_y="20px",
                                        width="100%",
                                    ),
                                ),
                                rx.divider(),
                                rx.link(
                                    rx.hstack(
                                        rx.text("View all notifications", size="2", weight="medium"),
                                        rx.icon("arrow-right", size=14),
                                        justify="between", width="100%", align="center",
                                        padding="8px 4px",
                                        color="#7c3aed",
                                    ),
                                    href="/notifications",
                                    text_decoration="none",
                                    width="100%",
                                ),
                                width="300px",
                                spacing="3",
                                align="start",
                            ),
                            side="bottom",
                            align="end",
                        )
                    ),
                    _profile_avatar_btn(),
                    rx.button(
                        rx.cond(
                            UploadState.is_dark_mode,
                            rx.icon("sun", size=18),
                            rx.icon("moon", size=18),
                        ),
                        on_click=UploadState.toggle_dark_mode,
                        size="2", variant="ghost", color=UploadState.text_color,
                        padding="8px", border_radius="50%",
                        _hover={"background": rx.cond(UploadState.is_dark_mode, "rgba(255,255,255,0.1)", "rgba(0,0,0,0.05)")},
                        cursor="pointer",
                        title="Toggle Theme",
                    ),
                    rx.button(
                        rx.icon("settings", size=18),
                        on_click=UploadState.toggle_settings,
                        size="2", variant="ghost", color=UploadState.text_color,
                        padding="8px", border_radius="50%",
                        _hover={"background": "rgba(0,0,0,0.05)"},
                        cursor="pointer",
                        title="Preferences",
                    ),
                    rx.button(
                        rx.icon("log-out", size=18),
                        on_click=State.logout,
                        size="2", variant="ghost", color=UploadState.sub_text_color,
                        padding="8px", border_radius="50%",
                        _hover={"background": "rgba(239,68,68,0.08)", "color": "#ef4444"},
                        cursor="pointer",
                        title="Sign out",
                    ),
                    spacing="3", align="center",
                ),
            ),
            spacing="4", align="center",
        ),

        justify="between",
        align="center",
        padding="0 24px",
        height="76px",
        background=UploadState.nav_bg,
        border_bottom="1px solid " + UploadState.border_color,
        position="sticky",
        top="0",
        z_index="1000",
        width="100%",
    )
