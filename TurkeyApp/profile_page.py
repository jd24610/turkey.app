"""Public Profile Page UI — /u/[username]"""

import reflex as rx
from TurkeyApp.profile_state import ProfileState
from TurkeyApp.upload_state import UploadState
from TurkeyApp.navbar import navbar
from TurkeyApp.edit_profile_modal import edit_profile_modal


# ─── Components ─────────────────────────────────────────────────────────────

def profile_toast() -> rx.Component:
    """General feedback toast for profiles."""
    return rx.cond(
        ProfileState.profile_toast_visible,
        rx.box(
            rx.hstack(
                rx.icon("sparkles", size=18, color="#a855f7"),
                rx.text(
                    ProfileState.profile_toast_message,
                    size="2", weight="medium", color="white",
                ),
                rx.button(
                    rx.icon("x", size=13),
                    on_click=ProfileState.dismiss_profile_toast,
                    size="1", variant="ghost", color_scheme="gray",
                ),
                spacing="3", align="center",
            ),
            position="fixed",
            bottom="28px", left="50%",
            transform="translateX(-50%)",
            z_index="9999",
            padding="12px 20px",
            background=UploadState.text_color,
            border_radius="14px",
            box_shadow="0 8px 32px rgba(0,0,0,0.25)",
            white_space="nowrap",
        ),
        rx.box(),
    )


def profile_header() -> rx.Component:
    """Banner and identity section."""
    return rx.box(
        # Banner
        rx.box(
            rx.cond(
                ProfileState.viewed_banner != "",
                rx.image(
                    src=ProfileState.viewed_banner_url,
                    width="100%", height="320px",
                    object_fit="cover",
                ),
                rx.box(
                    width="100%", height="240px",
                    background="linear-gradient(135deg, #7c3aed 0%, #a855f7 100%)",
                    opacity="0.9",
                ),
            ),
            width="100%", overflow="hidden",
        ),
        # Identity
        rx.vstack(
            rx.box(
                rx.cond(
                    ProfileState.viewed_avatar != "",
                    rx.image(
                        src=ProfileState.viewed_avatar_url,
                        width="160px", height="160px",
                        border_radius="50%", object_fit="cover",
                        border="4px solid white",
                    ),
                    rx.center(
                        rx.text(ProfileState.viewed_initials, size="8", weight="bold", color="white"),
                        width="160px", height="160px",
                        border_radius="50%",
                        background="linear-gradient(135deg, #7c3aed, #a855f7)",
                        border="4px solid white",
                    ),
                ),
                margin_top="-80px",
                z_index="10",
            ),
            rx.heading(ProfileState.viewed_display_name, size="8", color=UploadState.text_color, weight="bold"),
            rx.text("@" + ProfileState.viewed_username, size="3", color="#7c3aed", weight="medium"),
            rx.text(ProfileState.viewed_bio, size="4", color="#4b5563", text_align="center", max_width="600px", margin_top="12px"),
            
            # Follow / Unfollow logic
            rx.box(
                rx.cond(
                    # If viewing own profile, show nothing or edit
                    ProfileState.viewed_email == ProfileState.own_email,
                    rx.button(
                        rx.icon("pencil", size=18),
                        "Edit Profile",
                        on_click=ProfileState.toggle_edit_profile,
                        size="3",
                        background="linear-gradient(135deg, #7c3aed, #a855f7)",
                        color="white",
                        border_radius="12px",
                        cursor="pointer",
                        _hover={"opacity": "0.9"},
                    ),
                    rx.cond(
                        ProfileState.viewer_is_following,
                        rx.button(
                            "Following",
                            on_click=ProfileState.unfollow_user,
                            size="3", variant="outline", color_scheme="gray",
                            cursor="pointer",
                        ),
                        rx.button(
                            rx.icon("user-plus", size=18),
                            "Follow",
                            on_click=ProfileState.follow_user,
                            size="3",
                            background="#7c3aed", color="white",
                            border_radius="12px",
                            cursor="pointer",
                        ),
                    ),
                ),
                margin_top="24px",
            ),

            spacing="2", align="center", width="100%", padding_top="4px",
        ),
        width="100%", padding_bottom="32px",
    )


def profile_stats() -> rx.Component:
    """Horizontal stats bar below identity."""
    def stat(icon: str, value: rx.Var, label: str) -> rx.Component:
        return rx.hstack(
            rx.icon(icon, size=16, color="#7c3aed"),
            rx.text(value.to_string(), size="2", weight="bold", color=UploadState.text_color),
            rx.text(label, size="2", color=UploadState.sub_text_color),
            spacing="2", align="center",
        )

    return rx.center(
        rx.hstack(
            stat("image", ProfileState.viewed_image_count, "Photos"),
            rx.box(width="1px", height="16px", background="#e5e7eb"),
            stat("heart", ProfileState.viewed_total_likes, "Likes"),
            rx.box(width="1px", height="16px", background="#e5e7eb"),
            stat("users", ProfileState.viewed_follower_count, "Followers"),
            rx.box(width="1px", height="16px", background="#e5e7eb"),
            stat("user-check", ProfileState.viewed_following_count, "Following"),
            rx.box(width="1px", height="16px", background="#e5e7eb"),
            rx.hstack(
                rx.icon("calendar", size=16, color="#7c3aed"),
                rx.text(ProfileState.viewed_member_since_text, size="2", color=UploadState.sub_text_color),
                spacing="2", align="center",
            ),
            # Share
            rx.spacer(),
            rx.button(
                rx.icon("link", size=14),
                "Copy Link",
                on_click=ProfileState.copy_profile_link,
                size="1", variant="ghost",
            ),
            spacing="5", align="center", width="100%", max_width="1200px", padding_x="24px",
        ),
        width="100%", border_top="1px solid #f1f1f1", border_bottom="1px solid " + UploadState.border_color, padding_y="16px",
    )


def profile_tabs() -> rx.Component:
    """Tab switcher for All Posts vs Collections."""
    def nav_tab(label: str, value: str) -> rx.Component:
        is_active = ProfileState.active_profile_tab == value
        return rx.box(
            rx.text(label, size="3", weight=rx.cond(is_active, "bold", "medium")),
            on_click=lambda: ProfileState.set_profile_tab(value),
            padding="12px 24px",
            height="100%",
            display="flex", align_items="center",
            cursor="pointer",
            border_bottom=rx.cond(is_active, "2px solid #7c3aed", "2px solid transparent"),
            color=rx.cond(is_active, UploadState.text_color, UploadState.sub_text_color),
            _hover={"color": UploadState.text_color},
            transition="all 0.2s ease",
        )
    return rx.center(
        rx.hstack(
            nav_tab("All Posts", "all"),
            nav_tab("Collections", "collections"),
            spacing="1", align="center", height="50px",
        ),
        width="100%",
        border_bottom="1px solid " + UploadState.border_color,
        margin_bottom="32px",
    )


def profile_gallery_card(img: rx.Base, index: int) -> rx.Component:
    """A card for human-viewable content."""
    return rx.box(
        # ── Fixed-height thumbnail ──────────────────────────────────────
        rx.box(
            rx.image(
                src=img["url"],
                width="100%",
                height="100%",
                object_fit="cover",
                display="block",
                transition="transform 0.35s ease",
                _hover={"transform": "scale(1.04)"},
            ),
            width="100%",
            height="220px",
            overflow="hidden",
            border_radius="14px",
        ),
        # ── Caption ─────────────────────────────────────────────────────
        rx.cond(
            img["caption"] != "",
            rx.text(
                img["caption"],
                size="2",
                color="#374151",
                margin_top="8px",
                padding_x="2px",
                line_limit=2,
            ),
            rx.box(),
        ),
        on_click=lambda: ProfileState.open_viewed_image({"index": index}),
        cursor="pointer",
        width="100%",
        margin_bottom="20px",
        border_radius="16px",
        padding="0",
        box_shadow="0 2px 12px rgba(0,0,0,0.06)",
        transition="box-shadow 0.2s ease, transform 0.2s ease",
        _hover={"box_shadow": "0 8px 28px rgba(124,58,237,0.15)", "transform": "translateY(-2px)"},
    )


def profile_gallery_header() -> rx.Component:
    """Shows active folder filter information if any."""
    return rx.cond(
        ProfileState.viewed_active_folder != "",
        rx.hstack(
            rx.vstack(
                rx.hstack(
                    rx.icon("folder-open", size=18, color="#7c3aed"),
                    rx.heading(
                        ProfileState.viewed_active_folder,
                        size="5", color=UploadState.text_color, weight="bold"
                    ),
                    spacing="2", align="center",
                ),
                rx.text(
                    "Showing images from this collection",
                    size="2", color=UploadState.sub_text_color
                ),
                spacing="1", align="start",
            ),
            rx.spacer(),
            rx.button(
                "Show all photos",
                on_click=ProfileState.clear_collection_filter,
                size="2", variant="ghost", color_scheme="purple",
                cursor="pointer",
            ),
            width="100%", max_width="1400px", padding_x="24px",
            margin_bottom="32px",
            background="rgba(124,58,237,0.03)",
            padding_y="16px",
            border_radius="16px",
            border="1px solid rgba(124,58,237,0.1)",
        ),
        rx.box(),
    )


def profile_gallery() -> rx.Component:
    """Masonry-style photo grid."""
    return rx.box(
        rx.cond(
            ProfileState.viewed_images.length() > 0,
            rx.vstack(
                profile_gallery_header(),
                rx.box(
                    rx.foreach(
                        ProfileState.viewed_images,
                        lambda img, i: profile_gallery_card(img, i)
                    ),
                    column_count=rx.breakpoints(initial="1", sm="2", md="3", lg="4"),
                    column_gap="24px",
                    width="100%",
                ),
                spacing="0", width="100%",
            ),
            rx.center(
                rx.text("No public photos yet.", size="3", color="#9ca3af"),
                padding_y="100px",
            ),
        ),
        width="100%", max_width="1400px", padding_x="24px", margin="0 auto",
    )


def collections_grid() -> rx.Component:
    """Grid of public folders/collections."""
    return rx.box(
        rx.cond(
            ProfileState.viewed_collections.length() > 0,
            rx.grid(
                rx.foreach(
                    ProfileState.viewed_collections,
                    lambda c: rx.vstack(
                        rx.box(
                            rx.cond(
                                c["cover"] != "",
                                rx.image(
                                    src=c["cover_url"],
                                    width="100%", height="240px",
                                    object_fit="cover",
                                    border_radius="14px",
                                ),
                                rx.center(
                                    rx.icon("folder", size=32, color="#d1d5db"),
                                    width="100%", height="240px",
                                    background="#f3f4f6",
                                    border_radius="14px",
                                ),
                            ),
                            width="100%", overflow="hidden",
                        ),
                        rx.vstack(
                            rx.text(c["name"], size="4", weight="bold", color=UploadState.text_color),
                            rx.cond(
                                c["description"] != "",
                                rx.text(c["description"], size="2", color="#4b5563", line_limit=2),
                                rx.box(),
                            ),
                            rx.text(c["count_text"], size="2", color=UploadState.sub_text_color),
                            spacing="1", align="start",
                        ),
                        spacing="3", align="start", width="100%",
                        cursor="pointer",
                        _hover={"opacity": "0.8"},
                        on_click=ProfileState.goto_collection(ProfileState.viewed_username, c["name"]),
                    ),
                ),
                columns=rx.breakpoints(initial="1", sm="2", md="3", lg="4"),
                spacing="6",
                width="100%",
            ),
            rx.center(
                rx.text("No public collections yet.", size="3", color="#9ca3af"),
                padding_y="100px",
            ),
        ),
        width="100%", max_width="1400px", padding_x="24px", margin="0 auto",
    )


def profile_lightbox() -> rx.Component:
    """Fullscreen lightbox with comments side panel."""
    return rx.cond(
        ProfileState.show_viewed_lightbox,
        rx.box(
            # Image + Side Panel Container
            rx.hstack(
                # LEFT: Image & Metadata
                rx.vstack(
                    rx.image(
                        src=ProfileState.viewed_lightbox_url,
                        max_width="60vw",
                        max_height="76vh",
                        object_fit="contain",
                        border_radius="14px 0 0 14px",
                    ),
                    rx.cond(
                        ProfileState.viewed_lightbox_caption != "",
                        rx.text(ProfileState.viewed_lightbox_caption, size="2", color="#4b5563", text_align="center"),
                        rx.box(),
                    ),
                    # Actions
                    rx.hstack(
                        rx.button(
                            rx.cond(ProfileState.viewed_lightbox_viewer_has_liked, rx.icon("heart", fill="#f43f5e", color="#f43f5e"), rx.icon("heart")),
                            ProfileState.viewed_lightbox_like_count.to_string(),
                            on_click=ProfileState.toggle_profile_like,
                            variant="soft", color_scheme="red",
                        ),
                        rx.button(rx.icon("link"), "Share", on_click=ProfileState.copy_image_link, variant="soft", color_scheme="purple"),
                        spacing="4",
                    ),
                    spacing="4", align="center", padding="24px", flex="1", background="white", border_radius="14px 0 0 14px",
                ),
                # RIGHT: Comments Panel
                rx.box(
                    rx.vstack(
                        rx.text("Comments", size="4", weight="bold", color=UploadState.text_color),
                        rx.divider(),
                        rx.box(
                            rx.foreach(
                                ProfileState.viewed_lightbox_comments,
                                lambda c: rx.vstack(
                                    rx.hstack(
                                        rx.text("@", c["author_username"], size="2", weight="bold", color="#7c3aed"),
                                        rx.spacer(),
                                        rx.text(c["created_at"], size="1", color="#9ca3af"),
                                    ),
                                    rx.text(c["text"], size="2", color="#374151"),
                                    spacing="1", align="start", width="100%", padding="8px", background="#f9fafb", border_radius="8px", margin_bottom="8px",
                                )
                            ),
                            flex="1", overflow_y="auto", width="100%",
                        ),
                        rx.vstack(
                            rx.text_area(value=ProfileState.comment_input, on_change=ProfileState.set_comment_input, placeholder="Add a comment...", width="100%", size="2"),
                            rx.button("Post", on_click=ProfileState.add_comment, loading=ProfileState.comment_loading, width="100%", color_scheme="purple"),
                            spacing="2", width="100%",
                        ),
                        spacing="4", height="100%",
                    ),
                    width="340px", background="white", border_left="1px solid #f1f1f1", padding="24px", border_radius="0 14px 14px 0",
                ),
                spacing="0", background="white", border_radius="14px", box_shadow="0 30px 80px rgba(0,0,0,0.2)",
            ),
            # Close / Nav
            rx.button(rx.icon("chevron-left"), on_click=ProfileState.prev_viewed_image, position="fixed", left="4%", z_index="2002"),
            rx.button(rx.icon("chevron-right"), on_click=ProfileState.next_viewed_image, position="fixed", right="4%", z_index="2002"),
            rx.button(rx.icon("x"), on_click=ProfileState.close_viewed_lightbox, position="fixed", top="20px", right="30px", z_index="2003"),
            
            position="fixed", inset="0", background="rgba(0,0,0,0.8)", backdrop_filter="blur(8px)", display="flex", align_items="center", justify_content="center", z_index="2000",
        ),
        rx.box(),
    )


def profile_loading() -> rx.Component:
    return rx.center(rx.spinner(size="3", color="#7c3aed"), min_height="60vh")


def profile_not_found() -> rx.Component:
    return rx.center(rx.text("Profile not found", size="5"), min_height="60vh")


def public_profile_page() -> rx.Component:
    return rx.box(
        edit_profile_modal(),
        profile_toast(),
        profile_lightbox(),
        navbar(active_page="profile"),
        rx.cond(
            ProfileState.viewed_is_loading,
            profile_loading(),
            rx.cond(
                ProfileState.viewed_not_found,
                profile_not_found(),
                rx.box(
                    profile_header(),
                    profile_stats(),
                    profile_tabs(),
                    rx.cond(
                        ProfileState.active_profile_tab == "all",
                        profile_gallery(),
                        collections_grid(),
                    ),
                    width="100%",
                ),
            ),
        ),
        min_height="100vh", background=UploadState.bg_theme,
    )
