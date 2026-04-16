"""Edit Profile modal — accessible from the library navbar."""

import reflex as rx
from TurkeyApp.profile_state import ProfileState


_INPUT = {
    "background": "rgba(255,255,255,0.06)",
    "border": "1px solid rgba(124,58,237,0.4)",
    "border_radius": "12px",
    "color": "white",
    "_placeholder": {"color": "#4b5563"},
    "_focus": {"border_color": "#a855f7", "box_shadow": "0 0 0 3px rgba(168,85,247,0.2)"},
    "width": "100%",
}


def _label(text: str) -> rx.Component:
    return rx.text(text, size="1", color="#a78bfa", weight="medium", letter_spacing="0.8px")


# ── Avatar section ────────────────────────────────────────────────────────────

def _avatar_section() -> rx.Component:
    return rx.vstack(
        rx.center(
            # Avatar circle — shows real photo or initials
            rx.cond(
                ProfileState.own_avatar_url != "",
                rx.box(
                    rx.image(
                        src=ProfileState.own_avatar_url,
                        width="88px",
                        height="88px",
                        object_fit="cover",
                        border_radius="50%",
                        border="3px solid rgba(168,85,247,0.5)",
                    ),
                    position="relative",
                ),
                rx.box(
                    rx.text(ProfileState.own_initials, size="7", weight="bold", color="white"),
                    width="88px",
                    height="88px",
                    border_radius="50%",
                    background="linear-gradient(135deg, #6d28d9, #a855f7)",
                    display="flex",
                    align_items="center",
                    justify_content="center",
                    box_shadow="0 4px 20px rgba(124,58,237,0.5)",
                    border="3px solid rgba(168,85,247,0.3)",
                ),
            ),
        ),
        rx.upload(
            rx.button(
                rx.cond(
                    ProfileState.avatar_uploading,
                    rx.hstack(
                        rx.spinner(size="2"),
                        rx.text("Uploading…", size="2"),
                        spacing="2", align="center",
                    ),
                    rx.hstack(
                        rx.icon("camera", size=15),
                        rx.text("Change Photo", size="2"),
                        spacing="2", align="center",
                    ),
                ),
                size="2",
                variant="outline",
                color_scheme="purple",
                border_radius="10px",
                cursor="pointer",
                disabled=ProfileState.avatar_uploading,
            ),
            id="avatar_upload",
            accept={
                "image/jpeg": [".jpg", ".jpeg"],
                "image/png": [".png"],
                "image/gif": [".gif"],
                "image/webp": [".webp"],
            },
            max_files=1,
            on_drop=ProfileState.handle_avatar_upload(
                rx.upload_files(upload_id="avatar_upload")
            ),
        ),
        rx.cond(
            ProfileState.avatar_error != "",
            rx.hstack(
                rx.icon("circle-x", size=14, color="#ef4444"),
                rx.text(ProfileState.avatar_error, size="1", color="#ef4444"),
                spacing="1", align="center",
            ),
            rx.text("JPG, PNG, GIF or WEBP · max 5 MB", size="1", color="#6b7280"),
        ),
        spacing="3",
        align="center",
        width="100%",
    )


# ── Form fields ───────────────────────────────────────────────────────────────

def _form_fields() -> rx.Component:
    return rx.vstack(
        # Username
        rx.vstack(
            _label("USERNAME"),
            rx.hstack(
                rx.text("@", size="3", color="#7c3aed", weight="bold", padding_top="2px"),
                rx.input(
                    value=ProfileState.edit_username,
                    on_change=ProfileState.set_edit_username,
                    placeholder="your_handle",
                    size="3",
                    flex="1",
                    **_INPUT,
                ),
                spacing="2", width="100%", align="center",
            ),
            rx.cond(
                ProfileState.edit_username_error != "",
                rx.hstack(
                    rx.icon("circle-x", size=13, color="#ef4444"),
                    rx.text(ProfileState.edit_username_error, size="1", color="#ef4444"),
                    spacing="1", align="center",
                ),
                rx.text("3–20 chars · lowercase, numbers, underscores", size="1", color="#6b7280"),
            ),
            spacing="2", width="100%", align="start",
        ),

        # Display Name
        rx.vstack(
            _label("DISPLAY NAME"),
            rx.input(
                value=ProfileState.edit_display_name,
                on_change=ProfileState.set_edit_display_name,
                placeholder="Your name or nickname",
                size="3",
                **_INPUT,
            ),
            spacing="2", width="100%", align="start",
        ),

        # Bio
        rx.vstack(
            _label("BIO"),
            rx.text_area(
                value=ProfileState.edit_bio,
                on_change=ProfileState.set_edit_bio,
                placeholder="A short intro about yourself…",
                rows="3",
                resize="none",
                **_INPUT,
            ),
            spacing="2", width="100%", align="start",
        ),

        # Location + Website
        rx.hstack(
            rx.vstack(
                _label("LOCATION"),
                rx.input(
                    value=ProfileState.edit_location,
                    on_change=ProfileState.set_edit_location,
                    placeholder="City, Country",
                    size="3",
                    **_INPUT,
                ),
                spacing="2", width="100%", align="start",
            ),
            rx.vstack(
                _label("WEBSITE"),
                rx.input(
                    value=ProfileState.edit_website,
                    on_change=ProfileState.set_edit_website,
                    placeholder="https://…",
                    size="3",
                    **_INPUT,
                ),
                spacing="2", width="100%", align="start",
            ),
            spacing="4", width="100%",
        ),

        # Privacy
        rx.box(
            rx.hstack(
                rx.vstack(
                    rx.hstack(
                        rx.icon("globe", size=15, color="#a78bfa"),
                        rx.text("Public Profile", size="2", weight="medium", color="white"),
                        spacing="2", align="center",
                    ),
                    rx.text("Others can find & view your library", size="1", color="#6b7280"),
                    spacing="1", align="start",
                ),
                rx.switch(
                    checked=ProfileState.edit_is_public,
                    on_change=ProfileState.toggle_edit_is_public,
                    color_scheme="purple",
                ),
                justify="between", align="center", width="100%",
            ),
            padding="14px 18px",
            background="rgba(255,255,255,0.03)",
            border="1px solid rgba(124,58,237,0.2)",
            border_radius="12px",
            width="100%",
        ),

        spacing="4",
        width="100%",
    )


# ── Full modal ─────────────────────────────────────────────────────────────────

def edit_profile_modal() -> rx.Component:
    return rx.cond(
        ProfileState.show_edit_profile,
        rx.box(
            # Backdrop
            rx.box(
                position="fixed", top="0", left="0",
                width="100vw", height="100vh",
                background="rgba(0,0,0,0.65)",
                backdrop_filter="blur(8px)",
                z_index="4000",
                on_click=ProfileState.close_edit_profile,
            ),
            # Modal card
            rx.box(
                rx.vstack(
                    # ── Header ──
                    rx.hstack(
                        rx.hstack(
                            rx.box(
                                rx.icon("user-pen", size=18, color="white"),
                                padding="8px",
                                background="linear-gradient(135deg, #7c3aed, #a855f7)",
                                border_radius="10px",
                            ),
                            rx.heading("Edit Profile", size="5", color="white"),
                            spacing="3", align="center",
                        ),
                        rx.button(
                            rx.icon("x", size=18),
                            on_click=ProfileState.close_edit_profile,
                            variant="ghost",
                            color_scheme="gray",
                            size="2",
                            border_radius="50%",
                            cursor="pointer",
                        ),
                        justify="between",
                        align="center",
                        width="100%",
                    ),

                    rx.divider(color="rgba(124,58,237,0.2)"),

                    # Scrollable body
                    rx.box(
                        rx.vstack(
                            _avatar_section(),
                            rx.divider(color="rgba(124,58,237,0.1)"),
                            _form_fields(),
                            spacing="5",
                            width="100%",
                        ),
                        overflow_y="auto",
                        max_height="65vh",
                        padding_right="4px",
                        width="100%",
                    ),

                    rx.divider(color="rgba(124,58,237,0.15)"),

                    # ── Footer: error / success + buttons ──
                    rx.vstack(
                        rx.cond(
                            ProfileState.edit_save_success,
                            rx.hstack(
                                rx.icon("circle-check", size=16, color="#22c55e"),
                                rx.text("Profile saved!", size="2", color="#86efac", weight="medium"),
                                spacing="2", align="center",
                            ),
                            rx.box(),
                        ),
                        rx.cond(
                            ProfileState.edit_save_error != "",
                            rx.hstack(
                                rx.icon("circle-x", size=14, color="#ef4444"),
                                rx.text(ProfileState.edit_save_error, size="1", color="#ef4444"),
                                spacing="1", align="center",
                            ),
                            rx.box(),
                        ),
                        rx.hstack(
                            rx.button(
                                "Cancel",
                                on_click=ProfileState.close_edit_profile,
                                variant="ghost",
                                color_scheme="gray",
                                size="3",
                                cursor="pointer",
                            ),
                            rx.button(
                                rx.icon("save", size=16),
                                "Save Changes",
                                on_click=ProfileState.save_profile_edits,
                                loading=ProfileState.edit_saving,
                                size="3",
                                background="linear-gradient(135deg, #7c3aed, #a855f7)",
                                color="white",
                                border_radius="12px",
                                cursor="pointer",
                                box_shadow="0 4px 16px rgba(124,58,237,0.4)",
                                _hover={"opacity": "0.9"},
                            ),
                            justify="end",
                            width="100%",
                            spacing="3",
                        ),
                        spacing="3",
                        width="100%",
                    ),

                    spacing="5",
                    width="100%",
                ),
                padding="36px",
                background="rgba(8,4,22,0.98)",
                border="1px solid rgba(124,58,237,0.35)",
                border_radius="24px",
                box_shadow="0 40px 80px rgba(0,0,0,0.8), 0 0 0 1px rgba(124,58,237,0.1)",
                width="540px",
                max_width="95vw",
                position="relative",
                z_index="4001",
                backdrop_filter="blur(24px)",
            ),
            position="fixed",
            top="0", left="0",
            width="100vw", height="100vh",
            display="flex",
            align_items="center",
            justify_content="center",
            z_index="4000",
        ),
        rx.box(),
    )
