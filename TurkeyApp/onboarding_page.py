"""Onboarding wizard — multi-step profile setup that appears on first login."""

import reflex as rx
from TurkeyApp.profile_state import ProfileState


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
            "rgba(255,255,255,0.1)",
        ),
        border=rx.cond(
            active,
            "2px solid #a855f7",
            "2px solid transparent",
        ),
        box_shadow=rx.cond(active, "0 0 12px rgba(168,85,247,0.6)", "none"),
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
        background="rgba(255,255,255,0.08)",
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
        align="center",
        width="200px",
        spacing="0",
    )


# ─── Step 1: Username + display name ───────────────────────────────────────────

def step_one() -> rx.Component:
    return rx.vstack(
        rx.vstack(
            rx.text("@username", size="1", color="#a78bfa", weight="medium", letter_spacing="1px"),
            rx.hstack(
                rx.text("@", size="4", color="#7c3aed", weight="bold", padding_top="2px"),
                rx.input(
                    value=ProfileState.username_input,
                    on_change=ProfileState.set_username_input,
                    placeholder="your_handle",
                    size="3",
                    flex="1",
                    background="rgba(255,255,255,0.06)",
                    border="1px solid rgba(124,58,237,0.4)",
                    border_radius="12px",
                    color="white",
                    _placeholder={"color": "#4b5563"},
                    _focus={"border_color": "#a855f7", "box_shadow": "0 0 0 3px rgba(168,85,247,0.2)"},
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
                    size="1", color="#6b7280",
                ),
            ),
            spacing="2", width="100%", align="start",
        ),

        rx.vstack(
            rx.text("Display Name", size="1", color="#a78bfa", weight="medium", letter_spacing="1px"),
            rx.input(
                value=ProfileState.display_name_input,
                on_change=ProfileState.set_display_name_input,
                placeholder="Your full name or nickname",
                size="3",
                width="100%",
                background="rgba(255,255,255,0.06)",
                border="1px solid rgba(124,58,237,0.4)",
                border_radius="12px",
                color="white",
                _placeholder={"color": "#4b5563"},
                _focus={"border_color": "#a855f7", "box_shadow": "0 0 0 3px rgba(168,85,247,0.2)"},
            ),
            rx.text(
                "This is how your name appears on your profile",
                size="1", color="#6b7280",
            ),
            spacing="2", width="100%", align="start",
        ),

        spacing="5", width="100%",
    )


# ─── Step 2: Bio + DOB + Location + Website ────────────────────────────────────

def step_two() -> rx.Component:
    def field_label(text: str) -> rx.Component:
        return rx.text(text, size="1", color="#a78bfa", weight="medium", letter_spacing="1px")

    input_style = {
        "background": "rgba(255,255,255,0.06)",
        "border": "1px solid rgba(124,58,237,0.4)",
        "border_radius": "12px",
        "color": "white",
        "_placeholder": {"color": "#4b5563"},
        "_focus": {"border_color": "#a855f7", "box_shadow": "0 0 0 3px rgba(168,85,247,0.2)"},
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
                rx.icon("globe", size=16, color="#6b7280", flex_shrink="0"),
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


# ─── Step 3: Privacy + finish ──────────────────────────────────────────────────

def step_three() -> rx.Component:
    return rx.vstack(
        # Profile preview card
        rx.box(
            rx.vstack(
                rx.hstack(
                    # Initials avatar
                    rx.box(
                        rx.text(
                            ProfileState.own_initials,
                            size="5", weight="bold", color="white",
                        ),
                        width="64px", height="64px",
                        border_radius="50%",
                        background="linear-gradient(135deg, #7c3aed, #a855f7)",
                        display="flex",
                        align_items="center",
                        justify_content="center",
                        box_shadow="0 4px 20px rgba(124,58,237,0.5)",
                    ),
                    rx.vstack(
                        rx.hstack(
                            rx.text(ProfileState.display_name_input, size="4", weight="bold", color="white"),
                            spacing="0",
                        ),
                        rx.text("@" + ProfileState.username_input, size="2", color="#a78bfa"),
                        rx.cond(
                            ProfileState.bio_input != "",
                            rx.text(ProfileState.bio_input, size="2", color="#9ca3af", max_width="200px",
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
            background="rgba(124,58,237,0.08)",
            border="1px solid rgba(124,58,237,0.25)",
            border_radius="16px",
            width="100%",
        ),

        # Privacy toggle
        rx.box(
            rx.hstack(
                rx.vstack(
                    rx.hstack(
                        rx.icon("globe", size=16, color="#a78bfa"),
                        rx.text("Public Library", size="3", weight="medium", color="white"),
                        spacing="2", align="center",
                    ),
                    rx.text(
                        "Anyone can view your profile and images at turkey.app/@you",
                        size="2", color="#6b7280",
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
            background="rgba(255,255,255,0.03)",
            border="1px solid rgba(124,58,237,0.2)",
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
                background="rgba(0,0,0,0.7)",
                backdrop_filter="blur(8px)",
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
                            rx.text("Welcome to turkey.app", size="2", color="#a78bfa"),
                            spacing="3", align="center",
                        ),
                        rx.heading(
                            ProfileState.step_title,
                            size="6", color="white", text_align="center",
                        ),
                        rx.text(
                            ProfileState.step_subtitle,
                            size="2", color="#9ca3af", text_align="center",
                            max_width="340px",
                        ),
                        step_indicator(),
                        spacing="3",
                        align="center",
                    ),

                    rx.divider(color="rgba(124,58,237,0.2)"),

                    # Step content
                    rx.cond(
                        ProfileState.onboarding_step == 1,
                        step_one(),
                        rx.cond(
                            ProfileState.onboarding_step == 2,
                            step_two(),
                            step_three(),
                        ),
                    ),

                    rx.divider(color="rgba(124,58,237,0.15)"),

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
                            ProfileState.onboarding_step < 3,
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
                                box_shadow="0 4px 20px rgba(124,58,237,0.5)",
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
                background="rgba(8,4,22,0.98)",
                border="1px solid rgba(124,58,237,0.3)",
                border_radius="28px",
                box_shadow="0 40px 80px rgba(0,0,0,0.8), 0 0 0 1px rgba(124,58,237,0.1)",
                width="520px",
                max_width="95vw",
                position="relative",
                z_index="3001",
                backdrop_filter="blur(24px)",
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
