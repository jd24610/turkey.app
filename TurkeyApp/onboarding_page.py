"""Onboarding wizard — multi-step profile setup that appears on first login."""

import reflex as rx
from TurkeyApp.profile_state import ProfileState
from TurkeyApp.upload_state import UploadState


# ─── Step indicator ────────────────────────────────────────────────────────────

def _step_dot(n: int) -> rx.Component:
    active = ProfileState.onboarding_step == n
    done = ProfileState.onboarding_step > n
    return rx.box(
        rx.cond(
            done,
            rx.icon("check", size=11, color="white"),
            rx.box(),
        ),
        width="28px", height="28px",
        border_radius="50%",
        background=rx.cond(
            active | done,
            "linear-gradient(135deg, #7c3aed, #a855f7)",
            "#f3f4f6",
        ),
        border=rx.cond(
            active,
            "2px solid #a855f7",
            "2px solid transparent",
        ),
        box_shadow=rx.cond(active, "0 0 12px rgba(168,85,247,0.4)", "none"),
        display="flex",
        align_items="center",
        justify_content="center",
        transition="all 0.3s ease",
    )


def _step_line(active: rx.Var) -> rx.Component:
    return rx.box(
        rx.box(
            height="100%",
            background="linear-gradient(90deg,#7c3aed,#a855f7)",
            width=rx.cond(active, "100%", "0%"),
            transition="width 0.4s ease",
            border_radius="2px",
        ),
        height="2px",
        flex="1",
        background="#f1f1f1",
        border_radius="2px",
        overflow="hidden",
    )


def step_indicator() -> rx.Component:
    return rx.hstack(
        _step_dot(1),
        _step_line(ProfileState.onboarding_step > 1),
        _step_dot(2),
        _step_line(ProfileState.onboarding_step > 2),
        _step_dot(3),
        _step_line(ProfileState.onboarding_step > 3),
        _step_dot(4),
        align="center",
        width="260px",
        spacing="0",
    )


# ─── Step 1: Username + display name ───────────────────────────────────────────

def step_one() -> rx.Component:
    return rx.vstack(
        rx.vstack(
            rx.text("@username", size="1", color="#7c3aed", weight="medium", letter_spacing="1px"),
            rx.hstack(
                rx.text("@", size="4", color="#7c3aed", weight="bold", padding_top="2px"),
                rx.input(
                    value=ProfileState.username_input,
                    on_change=ProfileState.set_username_input,
                    placeholder="your_handle",
                    size="3",
                    flex="1",
                    background=UploadState.bg_theme,
                    border="1px solid #e2e2e2",
                    border_radius="12px",
                    color=UploadState.text_color,
                    _placeholder={"color": "#9ca3af"},
                    _focus={"border_color": "#7c3aed", "box_shadow": "0 0 0 3px rgba(124,58,237,0.1)"},
                ),
                spacing="2",
                width="100%",
                align="center",
            ),
            rx.cond(
                ProfileState.username_error != "",
                rx.hstack(
                    rx.icon("circle-x", size=14, color="#ef4444"),
                    rx.text(ProfileState.username_error, size="1", color="#ef4444"),
                    spacing="1", align="center",
                ),
                rx.text(
                    "3–20 chars · lowercase, numbers, underscores",
                    size="1", color=UploadState.sub_text_color,
                ),
            ),
            spacing="2", width="100%", align="start",
        ),

        rx.vstack(
            rx.text("Display Name", size="1", color="#7c3aed", weight="medium", letter_spacing="1px"),
            rx.input(
                value=ProfileState.display_name_input,
                on_change=ProfileState.set_display_name_input,
                placeholder="Your full name or nickname",
                size="3",
                width="100%",
                background=UploadState.bg_theme,
                border="1px solid #e2e2e2",
                border_radius="12px",
                color=UploadState.text_color,
                _placeholder={"color": "#9ca3af"},
                _focus={"border_color": "#7c3aed", "box_shadow": "0 0 0 3px rgba(124,58,237,0.1)"},
            ),
            rx.text(
                "This is how your name appears on your profile",
                size="1", color=UploadState.sub_text_color,
            ),
            spacing="2", width="100%", align="start",
        ),

        spacing="5", width="100%",
    )


# ─── Step 2: Bio + DOB + Location + Website ────────────────────────────────────

def step_two() -> rx.Component:
    def field_label(text: str) -> rx.Component:
        return rx.text(text, size="1", color="#7c3aed", weight="medium", letter_spacing="1px")

    input_style = {
        "background": "#ffffff",
        "border": "1px solid #e2e2e2",
        "border_radius": "12px",
        "color": UploadState.text_color,
        "_placeholder": {"color": "#9ca3af"},
        "_focus": {"border_color": "#7c3aed", "box_shadow": "0 0 0 3px rgba(124,58,237,0.1)"},
    }

    return rx.vstack(
        rx.vstack(
            field_label("Bio"),
            rx.text_area(
                value=ProfileState.bio_input,
                on_change=ProfileState.set_bio_input,
                placeholder="A short intro about you and your photography…",
                rows="3",
                width="100%",
                resize="none",
                **input_style,
            ),
            spacing="2", width="100%", align="start",
        ),

        rx.hstack(
            rx.vstack(
                field_label("Date of Birth"),
                rx.input(
                    type="date",
                    value=ProfileState.dob_input,
                    on_change=ProfileState.set_dob_input,
                    size="3",
                    width="100%",
                    **input_style,
                ),
                spacing="2", width="100%", align="start",
            ),
            rx.vstack(
                field_label("Location"),
                rx.input(
                    value=ProfileState.location_input,
                    on_change=ProfileState.set_location_input,
                    placeholder="City, Country",
                    size="3",
                    width="100%",
                    **input_style,
                ),
                spacing="2", width="100%", align="start",
            ),
            spacing="4", width="100%",
        ),

        rx.vstack(
            field_label("Website"),
            rx.hstack(
                rx.icon("globe", size=16, color=UploadState.sub_text_color, flex_shrink="0"),
                rx.input(
                    value=ProfileState.website_input,
                    on_change=ProfileState.set_website_input,
                    placeholder="https://yourwebsite.com",
                    size="3",
                    flex="1",
                    **input_style,
                ),
                spacing="2", width="100%", align="center",
            ),
            spacing="2", width="100%", align="start",
        ),

        spacing="4", width="100%",
    )


# ─── Step 3: Avatar + Banner ───────────────────────────────────────────────────

def step_media() -> rx.Component:
    return rx.vstack(
        rx.hstack(
            rx.vstack(
                rx.text("Avatar", size="1", color="#7c3aed", weight="medium", letter_spacing="1px"),
                rx.upload(
                    rx.cond(
                        ProfileState.own_avatar != "",
                        rx.image(
                            src=ProfileState.own_avatar_url,
                            width="100px", height="100px",
                            border_radius="50%", object_fit="cover",
                        ),
                        rx.center(
                            rx.icon("user", size=32, color="#d1d5db"),
                            width="100px", height="100px",
                            border_radius="50%", background="#f3f4f6",
                        ),
                    ),
                    id="avatar_upload",
                    on_drop=ProfileState.handle_avatar_upload(rx.upload_files(upload_id="avatar_upload")),
                    border="none",
                    padding="0",
                    border_radius="50%",
                ),
                rx.text("Click to Change", size="1", color=UploadState.sub_text_color),
                spacing="2", align="center",
            ),
            rx.vstack(
                rx.text("Profile Banner", size="1", color="#7c3aed", weight="medium", letter_spacing="1px"),
                rx.upload(
                    rx.cond(
                        ProfileState.own_banner != "",
                        rx.image(
                            src=ProfileState.own_banner_url,
                            width="300px", height="100px",
                            border_radius="12px", object_fit="cover",
                        ),
                        rx.center(
                            rx.icon("image", size=32, color="#d1d5db"),
                            width="300px", height="100px",
                            border_radius="12px", background="#f3f4f6",
                        ),
                    ),
                    id="banner_upload",
                    on_drop=ProfileState.handle_banner_upload(rx.upload_files(upload_id="banner_upload")),
                    border="none",
                    padding="0",
                    border_radius="12px",
                ),
                rx.text("Ideal: 1200x400", size="1", color=UploadState.sub_text_color),
                spacing="2", align="center",
            ),
            spacing="6", align="center", width="100%",
        ),
        rx.cond(
            ProfileState.avatar_error != "",
            rx.text(ProfileState.avatar_error, size="1", color="#ef4444"),
            rx.cond(
                ProfileState.banner_error != "",
                rx.text(ProfileState.banner_error, size="1", color="#ef4444"),
                rx.box(),
            ),
        ),
        spacing="5", width="100%",
    )


# ─── Step 4: Privacy + finish ──────────────────────────────────────────────────

def step_three() -> rx.Component:
    return rx.vstack(
        # Profile preview card
        rx.box(
            rx.vstack(
                rx.hstack(
                    # Avatar (Initials or Uploaded)
                    rx.box(
                        rx.cond(
                            ProfileState.own_avatar != "",
                            rx.image(
                                src=ProfileState.own_avatar_url,
                                width="64px", height="64px",
                                border_radius="50%", object_fit="cover",
                            ),
                            rx.text(
                                ProfileState.own_initials,
                                size="5", weight="bold", color="white",
                            ),
                        ),
                        width="64px", height="64px",
                        border_radius="50%",
                        background="linear-gradient(135deg, #7c3aed, #a855f7)",
                        display="flex",
                        align_items="center",
                        justify_content="center",
                        box_shadow="0 4px 20px rgba(124,58,237,0.3)",
                    ),
                    rx.vstack(
                        rx.hstack(
                            rx.text(ProfileState.display_name_input, size="4", weight="bold", color=UploadState.text_color),
                            spacing="0",
                        ),
                        rx.text("@", ProfileState.username_input, size="2", color="#7c3aed"),
                        rx.cond(
                            ProfileState.bio_input != "",
                            rx.text(ProfileState.bio_input, size="2", color="#4b5563", max_width="200px",
                                    overflow="hidden", text_overflow="ellipsis", white_space="nowrap"),
                            rx.box(),
                        ),
                        spacing="1", align="start",
                    ),
                    spacing="4", align="center",
                ),
                spacing="3",
            ),
            padding="20px 24px",
            background="#f9fafb",
            border="1px solid " + UploadState.border_color,
            border_radius="16px",
            width="100%",
        ),

        # Privacy toggle
        rx.box(
            rx.hstack(
                rx.vstack(
                    rx.hstack(
                        rx.icon("globe", size=16, color="#7c3aed"),
                        rx.text("Public Library", size="3", weight="medium", color=UploadState.text_color),
                        spacing="2", align="center",
                    ),
                    rx.text(
                        "Anyone can view your profile and images at turkey.app/@you",
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
            background=UploadState.bg_theme,
            border="1px solid " + UploadState.border_color,
            border_radius="14px",
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

        spacing="4", width="100%",
    )


# ─── Main onboarding modal ─────────────────────────────────────────────────────

def onboarding_modal() -> rx.Component:
    """Full-screen onboarding wizard overlay shown on first login."""
    return rx.cond(
        ProfileState.show_onboarding,
        rx.box(
            # Blurred backdrop
            rx.box(
                position="fixed", top="0", left="0",
                width="100vw", height="100vh",
                background="rgba(255,255,255,0.1)",
                backdrop_filter="blur(16px)",
                z_index="3000",
            ),
            # Wizard card
            rx.box(
                rx.vstack(
                    # Header
                    rx.vstack(
                        rx.hstack(
                            rx.box(
                                rx.icon("sparkles", size=20, color="white"),
                                padding="8px",
                                background="linear-gradient(135deg, #7c3aed, #a855f7)",
                                border_radius="10px",
                            ),
                            rx.text("Welcome to turkey.app", size="2", color="#7c3aed"),
                            spacing="3", align="center",
                        ),
                        rx.heading(
                            ProfileState.step_title,
                            size="6", color=UploadState.text_color, text_align="center",
                        ),
                        rx.text(
                            ProfileState.step_subtitle,
                            size="2", color=UploadState.sub_text_color, text_align="center",
                            max_width="340px",
                        ),
                        step_indicator(),
                        spacing="3",
                        align="center",
                    ),

                    rx.divider(color="#f1f1f1"),

                    # Step content
                    rx.cond(
                        ProfileState.onboarding_step == 1,
                        step_one(),
                        rx.cond(
                            ProfileState.onboarding_step == 2,
                            step_two(),
                            rx.cond(
                                ProfileState.onboarding_step == 3,
                                step_media(),
                                step_three(),
                            ),
                        ),
                    ),

                    rx.divider(color="#f1f1f1"),

                    # Navigation buttons
                    rx.hstack(
                        rx.cond(
                            ProfileState.onboarding_step > 1,
                            rx.button(
                                rx.icon("chevron-left", size=16),
                                "Back",
                                on_click=ProfileState.prev_step,
                                variant="ghost",
                                color_scheme="gray",
                                size="3",
                                cursor="pointer",
                            ),
                            rx.box(flex="1"),
                        ),
                        rx.spacer(),
                        rx.cond(
                            ProfileState.onboarding_step < 4,
                            rx.button(
                                "Continue",
                                rx.icon("chevron-right", size=16),
                                on_click=ProfileState.next_step,
                                size="3",
                                background="linear-gradient(135deg, #7c3aed, #a855f7)",
                                color="white",
                                border_radius="12px",
                                cursor="pointer",
                                _hover={"opacity": "0.9"},
                            ),
                            rx.button(
                                rx.icon("rocket", size=16),
                                "Launch My Library",
                                on_click=ProfileState.complete_onboarding,
                                loading=ProfileState.onboarding_saving,
                                size="3",
                                background="linear-gradient(135deg, #7c3aed, #a855f7)",
                                color="white",
                                border_radius="12px",
                                cursor="pointer",
                                box_shadow="0 4px 20px rgba(124,58,237,0.4)",
                                _hover={"opacity": "0.9", "transform": "translateY(-1px)"},
                                transition="all 0.2s ease",
                            ),
                        ),
                        width="100%",
                        align="center",
                    ),

                    spacing="6",
                    width="100%",
                ),
                padding="40px",
                background=UploadState.bg_theme,
                border="1px solid #e5e7eb",
                border_radius="28px",
                box_shadow="0 40px 80px rgba(0,0,0,0.1), 0 0 0 1px rgba(0,0,0,0.02)",
                width="520px",
                max_width="95vw",
                position="relative",
                z_index="3001",
            ),
            position="fixed",
            top="0", left="0",
            width="100vw", height="100vh",
            display="flex",
            align_items="center",
            justify_content="center",
            z_index="3000",
        ),
        rx.box(),
    )
