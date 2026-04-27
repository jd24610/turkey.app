"""Edit Profile modal — accessible from the library navbar."""

import reflex as rx
from TurkeyApp.profile_state import ProfileState
from TurkeyApp.upload_state import UploadState


def _input_style() -> dict:
    return {
        "background": "#ffffff",
        "border": "1px solid #e2e2e2",
        "border_radius": "12px",
        "color": UploadState.text_color,
        "_placeholder": {"color": "#9ca3af"},
        "_focus": {"border_color": "#7c3aed", "box_shadow": "0 0 0 3px rgba(124,58,237,0.1)"},
    }


def _field_label(text: str) -> rx.Component:
    return rx.text(text, size="1", color="#7c3aed", weight="medium", letter_spacing="1px")


# ── Full modal ─────────────────────────────────────────────────────────────────

def edit_profile_modal() -> rx.Component:
    """Modal to edit display name, bio, visibility, and avatar initials."""
    return rx.cond(
        ProfileState.show_edit_profile,
        rx.box(
            # Backdrop
            rx.box(
                position="fixed", top="0", left="0",
                width="100vw", height="100vh",
                background="rgba(255,255,255,0.1)",
                backdrop_filter="blur(16px)",
                z_index="2000",
                on_click=ProfileState.toggle_edit_profile,
            ),
            # Modal content
            rx.box(
                rx.vstack(
                    # Header
                    rx.hstack(
                        rx.vstack(
                            rx.heading("Edit Profile", size="6", color=UploadState.text_color),
                            rx.text("Update your personal information and privacy", size="2", color=UploadState.sub_text_color),
                            spacing="1", align="start",
                        ),
                        rx.button(
                            rx.icon("x", size=20),
                            on_click=ProfileState.toggle_edit_profile,
                            variant="ghost",
                            color_scheme="gray",
                            color=UploadState.sub_text_color,
                        ),
                        justify="between",
                        width="100%",
                        align="start",
                    ),

                    rx.divider(color="#f1f1f1"),

                    # Scrollable body
                    rx.box(
                        rx.vstack(
                            # Avatar section
                            rx.hstack(
                                rx.box(
                                    rx.cond(
                                        ProfileState.own_avatar_url != "",
                                        rx.image(
                                            src=ProfileState.own_avatar_url,
                                            width="80px", height="80px",
                                            object_fit="cover",
                                            border_radius="50%",
                                            border="2px solid #7c3aed",
                                        ),
                                        rx.box(
                                            rx.text(
                                                ProfileState.own_initials,
                                                size="6", weight="bold", color="white",
                                            ),
                                            width="80px", height="80px",
                                            border_radius="50%",
                                            background="linear-gradient(135deg, #7c3aed, #a855f7)",
                                            display="flex",
                                            align_items="center",
                                            justify_content="center",
                                        ),
                                    ),
                                    box_shadow="0 8px 30px rgba(124,58,237,0.3)",
                                ),
                                rx.vstack(
                                    _field_label("PHOTOS / INITIALS"),
                                    rx.hstack(
                                        rx.input(
                                            value=ProfileState.own_initials,
                                            on_change=ProfileState.set_own_initials,
                                            placeholder="Me",
                                            max_length=2,
                                            width="70px",
                                            **_input_style(),
                                        ),
                                        rx.upload(
                                            rx.button(
                                                rx.cond(
                                                    ProfileState.avatar_uploading,
                                                    rx.spinner(size="1"),
                                                    rx.icon("camera", size=14),
                                                ),
                                                "Upload",
                                                size="2",
                                                variant="outline",
                                                color_scheme="purple",
                                                disabled=ProfileState.avatar_uploading,
                                            ),
                                            id="avatar_upload_modal",
                                            accept={"image/*": [".jpg", ".jpeg", ".png", ".gif", ".webp"]},
                                            max_files=1,
                                            on_drop=ProfileState.handle_avatar_upload(
                                                rx.upload_files(upload_id="avatar_upload_modal")
                                            ),
                                        ),
                                        spacing="2",
                                    ),
                                    spacing="2", align="start",
                                ),
                                spacing="6", align="center",
                                width="100%",
                                padding="12px 0",
                            ),

                            # Banner section
                            rx.vstack(
                                _field_label("PROFILE BANNER"),
                                rx.box(
                                    rx.cond(
                                        ProfileState.own_banner_url != "",
                                        rx.image(
                                            src=ProfileState.own_banner_url,
                                            width="100%", height="120px",
                                            object_fit="cover",
                                            border_radius="14px",
                                        ),
                                        rx.box(
                                            width="100%", height="120px",
                                            background="#f3f4f6",
                                            border_radius="14px",
                                            display="flex", align_items="center", justify_content="center",
                                            border="2px dashed #e5e7eb",
                                        ),
                                    ),
                                    width="100%",
                                    overflow="hidden",
                                    position="relative",
                                ),
                                rx.upload(
                                    rx.button(
                                        rx.cond(
                                            ProfileState.banner_uploading,
                                            rx.spinner(size="1"),
                                            rx.icon("image", size=14),
                                        ),
                                        "Change Banner",
                                        size="2", variant="outline", color_scheme="purple",
                                        disabled=ProfileState.banner_uploading,
                                    ),
                                    id="banner_upload_modal",
                                    accept={"image/*": [".jpg", ".jpeg", ".png", ".webp"]},
                                    max_files=1,
                                    on_drop=ProfileState.handle_banner_upload(
                                        rx.upload_files(upload_id="banner_upload_modal")
                                    ),
                                ),
                                rx.cond(
                                    ProfileState.banner_error != "",
                                    rx.text(ProfileState.banner_error, size="1", color="#ef4444"),
                                    rx.text("Recommended: 1500x500px or wide aspect ratio", size="1", color=UploadState.sub_text_color),
                                ),
                                spacing="2", align="start", width="100%",
                                padding="12px 0",
                                border_bottom="1px solid " + UploadState.border_color,
                            ),

                            # Display name
                            rx.vstack(
                                _field_label("DISPLAY NAME"),
                                rx.input(
                                    value=ProfileState.display_name_input,
                                    on_change=ProfileState.set_display_name_input,
                                    width="100%",
                                    **_input_style(),
                                ),
                                spacing="2", align="start", width="100%",
                            ),

                            # Bio
                            rx.vstack(
                                _field_label("BIO"),
                                    rx.text_area(
                                        value=ProfileState.bio_input,
                                        on_change=ProfileState.set_bio_input,
                                        placeholder="Tell the world about yourself…",
                                        width="100%",
                                        height="80px",
                                        **_input_style(),
                                    ),
                                spacing="2", align="start", width="100%",
                            ),

                            # Location + Website
                            rx.hstack(
                                rx.vstack(
                                    _field_label("LOCATION"),
                                    rx.input(
                                        value=ProfileState.location_input,
                                        on_change=ProfileState.set_location_input,
                                        placeholder="City, Country",
                                        width="100%",
                                        **_input_style(),
                                    ),
                                    spacing="2", align="start", width="100%",
                                ),
                                rx.vstack(
                                    _field_label("WEBSITE"),
                                    rx.input(
                                        value=ProfileState.website_input,
                                        on_change=ProfileState.set_website_input,
                                        placeholder="https://…",
                                        width="100%",
                                        **_input_style(),
                                    ),
                                    spacing="2", align="start", width="100%",
                                ),
                                spacing="4", width="100%",
                            ),

                            # Public toggle
                            rx.box(
                                rx.hstack(
                                    rx.vstack(
                                        rx.hstack(
                                            rx.icon("globe", size=16, color="#7c3aed"),
                                            rx.text("Public Profile", size="3", weight="medium", color=UploadState.text_color),
                                            spacing="2", align="center",
                                        ),
                                        rx.text(
                                            "Allow others to find and view your library",
                                            size="2", color=UploadState.sub_text_color,
                                        ),
                                        spacing="1", align="start",
                                    ),
                                    rx.switch(
                                        checked=ProfileState.is_public_input,
                                        on_change=ProfileState.toggle_is_public,
                                        color_scheme="purple",
                                    ),
                                    justify="between",
                                    align="center",
                                    width="100%",
                                ),
                                padding="16px 20px",
                                background="#f9fafb",
                                border="1px solid " + UploadState.border_color,
                                border_radius="14px",
                                width="100%",
                            ),
                            spacing="5", width="100%",
                        ),
                        max_height="60vh",
                        overflow_y="auto",
                        padding_right="8px",
                        width="100%",
                    ),

                    rx.cond(
                        ProfileState.save_error != "",
                        rx.hstack(
                            rx.icon("circle-x", size=14, color="#ef4444"),
                            rx.text(ProfileState.save_error, size="1", color="#ef4444"),
                            spacing="1", align="center",
                        ),
                        rx.box(),
                    ),

                    rx.divider(color="#f1f1f1"),

                    # Footer
                    rx.hstack(
                        rx.button(
                            "Cancel",
                            on_click=ProfileState.toggle_edit_profile,
                            variant="ghost",
                            color_scheme="gray",
                            size="3",
                        ),
                        rx.spacer(),
                        rx.button(
                            rx.icon("check", size=16),
                            "Save Changes",
                            on_click=ProfileState.complete_onboarding, # Reuses same logic
                            loading=ProfileState.onboarding_saving,
                            size="3",
                            background="linear-gradient(135deg, #7c3aed, #a855f7)",
                            color="white",
                            border_radius="12px",
                            cursor="pointer",
                            box_shadow="0 4px 20px rgba(124,58,237,0.3)",
                            _hover={"opacity": "0.9", "transform": "translateY(-1px)"},
                            transition="all 0.2s ease",
                        ),
                        width="100%",
                    ),

                    spacing="5",
                    width="100%",
                ),
                padding="32px",
                background=UploadState.bg_theme,
                border="1px solid #e5e7eb",
                border_radius="24px",
                box_shadow="0 30px 60px rgba(0,0,0,0.12), 0 0 0 1px rgba(0,0,0,0.02)",
                width="540px",
                max_width="95vw",
                position="relative",
                z_index="2001",
            ),
            position="fixed",
            top="0", left="0",
            width="100vw", height="100vh",
            display="flex",
            align_items="center",
            justify_content="center",
            z_index="2000",
        ),
        rx.box(),
    )
