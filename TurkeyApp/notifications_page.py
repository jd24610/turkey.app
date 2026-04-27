"""Notifications Management Page."""

import reflex as rx
from TurkeyApp.profile_state import ProfileState
from TurkeyApp.upload_state import UploadState
from TurkeyApp.navbar import navbar

def notification_row(notif: rx.Base) -> rx.Component:
    """A row representing a single notification."""
    return rx.box(
        rx.hstack(
            rx.vstack(
                rx.text(notif.message, size="3", color=UploadState.text_color, weight="medium"),
                rx.text(notif.created_at, size="1", color=UploadState.sub_text_color),
                spacing="1", align="start",
                flex="1",
            ),
            rx.spacer(),
            rx.cond(
                notif.status == "unread",
                rx.hstack(
                    rx.button(
                        rx.icon("check", size=14),
                        "Accept",
                        on_click=ProfileState.accept_follow_request(notif.id),
                        size="2", color_scheme="green", variant="soft",
                        cursor="pointer",
                    ),
                    rx.button(
                        rx.icon("x", size=14),
                        "Decline",
                        on_click=ProfileState.decline_follow_request(notif.id),
                        size="2", color_scheme="red", variant="soft",
                        cursor="pointer",
                    ),
                    spacing="2",
                ),
                rx.badge(
                    notif.status.capitalize(),
                    color_scheme=rx.cond(notif.status == "accepted", "green", "gray"),
                    variant="soft",
                    size="1",
                ),
            ),
            spacing="4", align="center", width="100%", padding="16px",
        ),
        background=UploadState.bg_card,
        border="1px solid " + UploadState.border_color,
        border_radius="12px",
        margin_bottom="12px",
        _hover={"border_color": "#7c3aed", "box_shadow": "0 4px 12px rgba(0,0,0,0.03)"},
        transition="all 0.2s ease",
        width="100%",
    )

def notifications_page() -> rx.Component:
    return rx.box(
        navbar(active_page="notifications"),
        rx.box(
            rx.vstack(
                # Header
                rx.vstack(
                    rx.hstack(
                        rx.icon("bell", size=28, color="#a855f7"),
                        rx.heading("Notifications", size="8", color=UploadState.text_color, weight="bold"),
                        spacing="3", align="center",
                    ),
                    rx.text("Keep track of likes, follows, and community updates.", size="3", color=UploadState.sub_text_color),
                    spacing="2", align="center",
                ),

                rx.divider(color="#f1f1f1", margin_y="24px"),

                # List
                rx.cond(
                    ProfileState.notifications.length() > 0,
                    rx.vstack(
                        rx.foreach(ProfileState.notifications, notification_row),
                        width="100%", spacing="0",
                    ),
                    # Empty state
                    rx.vstack(
                        rx.icon("bell-off", size=52, color="#d1d5db"),
                        rx.text("No notifications yet.", size="4", color="#9ca3af", weight="medium"),
                        spacing="4", align="center", padding_y="100px",
                    ),
                ),
                width="100%",
                max_width="700px",
                padding_x="24px",
                padding_y="48px",
                align="center",
            ),
            width="100%",
            display="flex",
            justify_content="center",
        ),
        min_height="100vh",
        background=UploadState.bg_theme,
    )
