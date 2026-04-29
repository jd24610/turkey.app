"""Import/Export page UI — shown after Google login."""

import reflex as rx
from rxconfig import config
from TurkeyApp.state import State
from TurkeyApp.upload_state import UploadState


# ─────────────────────────────────────────────
#  Helpers / small components
# ─────────────────────────────────────────────

def toast_notification() -> rx.Component:
    """Fixed bottom-right toast that appears whenever upload_message is set."""
    return rx.cond(
        UploadState.toast_visible,
        rx.box(
            rx.hstack(

                rx.cond(
                    UploadState.upload_status == "success",
                    rx.icon("circle-check", color="#22c55e", size=22, flex_shrink="0"),
                    rx.cond(
                        UploadState.upload_status == "warning",
                        rx.icon("triangle-alert", color="#f59e0b", size=22, flex_shrink="0"),
                        rx.icon("circle-x", color="#ef4444", size=22, flex_shrink="0"),
                    ),
                ),
                rx.text(
                    UploadState.upload_message,
                    size="2",
                    weight="medium",
                    color=UploadState.text_color,
                    flex="1",
                ),
                rx.button(
                    rx.icon("x", size=14),
                    on_click=UploadState.dismiss_toast,
                    size="1",
                    variant="ghost",
                    color_scheme="gray",
                    color=UploadState.sub_text_color,
                    flex_shrink="0",
                ),
                spacing="3",
                align="center",
                width="100%",
            ),
            position="fixed",
            bottom="28px",
            right="28px",
            z_index="9999",
            min_width="280px",
            max_width="400px",
            padding="14px 18px",
            border_radius="14px",
            background=UploadState.bg_theme,
            border="1px solid #e5e7eb",
            box_shadow="0 10px 40px rgba(0,0,0,0.08), 0 0 0 1px rgba(0,0,0,0.02)",
            border_left=rx.cond(
                UploadState.upload_status == "success",
                "4px solid #22c55e",
                rx.cond(
                    UploadState.upload_status == "warning",
                    "4px solid #f59e0b",
                    "4px solid #ef4444",
                ),
            ),
        ),
        rx.box(),
    )


def storage_bar() -> rx.Component:
    return rx.box(
        rx.vstack(
            rx.hstack(
                rx.hstack(
                    rx.icon("database", size=16, color="#a78bfa"),
                    rx.text("Storage", size="2", color="#a78bfa", weight="medium"),
                    spacing="1",
                    align="center",
                ),
                rx.text(
                    UploadState.used_storage_mb,
                    " MB / ",
                    UploadState.quota_mb,
                    " MB",
                    size="2",
                    color="#c4b5fd",
                ),
                justify="between",
                width="100%",
            ),
            rx.box(
                rx.box(
                    height="8px",
                    border_radius="4px",
                    background="linear-gradient(90deg, #7c3aed, #a855f7)",
                    width=UploadState.storage_percent.to(str) + "%",
                    transition="width 0.5s ease",
                ),
                background="rgba(124,58,237,0.2)",
                border_radius="4px",
                height="8px",
                width="100%",
                overflow="hidden",
            ),
            rx.text(
                UploadState.storage_percent,
                "% used",
                size="1",
                color="#7c3aed",
                weight="medium",
            ),
            spacing="2",
            width="100%",
        ),
        padding="16px 20px",
        background="rgba(124,58,237,0.08)",
        border="1px solid rgba(124,58,237,0.2)",
        border_radius="14px",
        width="100%",
        max_width="420px",
    )


def duplicate_modal() -> rx.Component:
    return rx.cond(
        UploadState.show_duplicate_modal,
        rx.box(
            rx.box(
                rx.vstack(
                    rx.hstack(
                        rx.icon("copy", size=24, color="#f59e0b"),
                        rx.heading("Duplicate Images Detected", size="5", color=UploadState.text_color),
                        spacing="3",
                        align="center",
                    ),
                    rx.text(
                        "The following files already exist in your library:",
                        size="3",
                        color="#4b5563",
                    ),
                    rx.box(
                        rx.foreach(
                            UploadState.pending_duplicates,
                            lambda name: rx.hstack(
                                rx.icon("image", size=14, color="#f59e0b"),
                                rx.text(name, size="2", color="#92400e"),
                                spacing="2",
                                align="center",
                            ),
                        ),
                        padding="12px 16px",
                        background="#fef3c7",
                        border="1px solid #fde68a",
                        border_radius="10px",
                        width="100%",
                        max_height="200px",
                        overflow_y="auto",
                    ),
                    rx.text(
                        "Do you want to overwrite these files?",
                        size="3",
                        color=UploadState.text_color,
                        weight="medium",
                    ),
                    rx.hstack(
                        rx.button(
                            "Skip Duplicates",
                            on_click=UploadState.cancel_duplicate_upload,
                            variant="outline",
                            color_scheme="gray",
                            size="3",
                        ),
                        rx.button(
                            "Overwrite All",
                            on_click=UploadState.confirm_duplicate_upload,
                            color_scheme="amber",
                            size="3",
                        ),
                        spacing="3",
                        justify="end",
                        width="100%",
                    ),
                    spacing="4",
                    width="100%",
                ),
                padding="32px",
                background=UploadState.bg_theme,
                border="1px solid #e5e7eb",
                border_radius="20px",
                width="480px",
                box_shadow="0 25px 60px rgba(0,0,0,0.15)",
            ),
            position="fixed",
            top="0",
            left="0",
            width="100vw",
            height="100vh",
            background="rgba(0,0,0,0.1)",
            backdrop_filter="blur(4px)",
            display="flex",
            align_items="center",
            justify_content="center",
            z_index="1000",
        ),
        rx.box(),
    )


def lightbox_modal() -> rx.Component:
    """Fullscreen image preview with metadata sidebar and prev/next navigation."""
    return rx.cond(
        UploadState.show_preview,
        rx.el.div(
            # ── Hidden key-capture input (auto-focused for keyboard nav) ──
            rx.input(
                auto_focus=True,
                read_only=True,
                style={
                    "position": "absolute",
                    "opacity": "0",
                    "width": "0",
                    "height": "0",
                    "pointer_events": "none",
                },
                on_key_down=lambda key: rx.cond(
                    key == "ArrowLeft",
                    UploadState.prev_image,
                    rx.cond(
                        key == "ArrowRight",
                        UploadState.next_image,
                        rx.cond(
                            key == "Escape",
                            UploadState.close_preview,
                            rx.noop(),
                        ),
                    ),
                ),
            ),
            # ── Dark backdrop (click outside to close) ──
            rx.box(
                position="absolute",
                top="0", left="0",
                width="100%", height="100%",
                on_click=UploadState.close_preview,
            ),

            # ── Main row: [prev] [image + meta] [next] ──
            rx.hstack(
                # ── Prev arrow ──
                rx.box(
                    rx.button(
                        rx.icon("chevron-left", size=28),
                        on_click=UploadState.prev_image,
                        size="3",
                        variant="ghost",
                        color_scheme="gray",
                        border_radius="50%",
                        background="rgba(255,255,255,0.08)",
                        _hover={"background": "rgba(255,255,255,0.18)"},
                        disabled=~UploadState.preview_has_prev,
                        opacity=rx.cond(UploadState.preview_has_prev, "1", "0.2"),
                        cursor=rx.cond(UploadState.preview_has_prev, "pointer", "default"),
                    ),
                    position="relative",
                    z_index="2",
                ),

                # ── Image + metadata card ──
                rx.vstack(
                    # Image
                    rx.image(
                        src=(State.backend_url + "/uploaded_files/" + UploadState.preview_filename).replace(" ", "%20"),
                        max_width="70vw",
                        max_height="72vh",
                        object_fit="contain",
                        border_radius="12px",
                        box_shadow="0 30px 80px rgba(0,0,0,0.8)",
                        position="relative",
                        z_index="1",
                    ),
                    # ── Metadata bar ──
                    rx.box(
                        rx.vstack(
                            rx.hstack(
                                # filename
                                rx.hstack(
                                    rx.icon("image", size=14, color="#7c3aed"),
                                    rx.text(
                                        UploadState.lightbox_name,
                                        size="2", weight="medium", color=UploadState.text_color,
                                        max_width="240px",
                                        overflow="hidden",
                                        text_overflow="ellipsis",
                                        white_space="nowrap",
                                    ),
                                    spacing="1", align="center",
                                ),
                                rx.box(width="1px", height="16px", background="rgba(255,255,255,0.12)"),
                                # size
                                rx.hstack(
                                    rx.icon("hard-drive", size=13, color=UploadState.sub_text_color),
                                    rx.text(UploadState.lightbox_size, size="1", color="#9ca3af"),
                                    spacing="1", align="center",
                                ),
                                rx.box(width="1px", height="16px", background="rgba(255,255,255,0.12)"),
                                # date
                                rx.hstack(
                                    rx.icon("calendar", size=13, color=UploadState.sub_text_color),
                                    rx.text(UploadState.lightbox_date, size="1", color="#9ca3af"),
                                    spacing="1", align="center",
                                ),
                                rx.box(width="1px", height="16px", background="rgba(255,255,255,0.12)"),
                                # folder
                                rx.hstack(
                                    rx.icon("folder", size=13, color=UploadState.sub_text_color),
                                    rx.text(UploadState.lightbox_folder, size="1", color="#9ca3af"),
                                    spacing="1", align="center",
                                ),
                                rx.box(width="1px", height="16px", background="rgba(255,255,255,0.12)"),
                                # tags
                                rx.hstack(
                                    rx.icon("tag", size=13, color=UploadState.sub_text_color),
                                    rx.text(UploadState.lightbox_tag_count, " tags", size="1", color="#9ca3af"),
                                    spacing="1", align="center",
                                ),
                                # counter spacer
                                rx.spacer(),
                                rx.text(
                                    UploadState.lightbox_counter,
                                    size="1", color="#4b5563", font_variant_numeric="tabular-nums",
                                ),
                                spacing="3",
                                align="center",
                                width="100%",
                            ),
                            # ── Public toggle row ──
                            rx.hstack(
                                rx.hstack(
                                    rx.cond(
                                        UploadState.lightbox_is_public,
                                        rx.icon("globe", size=14, color="#22c55e"),
                                        rx.icon("lock", size=14, color=UploadState.sub_text_color),
                                    ),
                                    rx.text(
                                        rx.cond(
                                            UploadState.lightbox_is_public,
                                            "Public — visible on your profile",
                                            "Private — only visible to you",
                                        ),
                                        size="1",
                                        color=rx.cond(
                                            UploadState.lightbox_is_public,
                                            "#86efac",
                                            UploadState.sub_text_color,
                                        ),
                                    ),
                                    spacing="2", align="center",
                                ),
                                rx.spacer(),
                                rx.switch(
                                    checked=UploadState.lightbox_is_public,
                                    on_change=lambda _: UploadState.toggle_lightbox_public(),
                                    color_scheme="green",
                                    size="1",
                                ),
                                spacing="3",
                                align="center",
                                width="100%",
                                border_top="1px solid rgba(0,0,0,0.06)",
                                padding_top="8px",
                            ),
                            # ── Caption row (always editable) ──
                            rx.cond(
                                UploadState.lightbox_editing_caption,
                                # ── Edit mode ──
                                rx.hstack(
                                    rx.icon("pencil", size=13, color="#a78bfa"),
                                    rx.input(
                                        value=UploadState.lightbox_caption_draft,
                                        on_change=UploadState.set_lightbox_caption_draft,
                                        placeholder="Add a caption…",
                                        size="1",
                                        flex="1",
                                        background="rgba(0,0,0,0.05)",
                                        border="1px solid rgba(124,58,237,0.3)",
                                        border_radius="8px",
                                        color=UploadState.text_color,
                                        _placeholder={"color": UploadState.sub_text_color},
                                        _focus={"outline": "none", "border_color": "#7c3aed"},
                                        on_key_down=lambda key: rx.cond(
                                            key == "Enter",
                                            rx.cond(
                                                UploadState.lightbox_caption_draft != "",
                                                UploadState.save_lightbox_caption,
                                                UploadState.cancel_edit_caption,
                                            ),
                                            rx.cond(
                                                key == "Escape",
                                                UploadState.cancel_edit_caption,
                                                rx.noop(),
                                            ),
                                        ),
                                    ),
                                    rx.button(
                                        "Save",
                                        on_click=UploadState.save_lightbox_caption,
                                        size="1",
                                        background="linear-gradient(135deg,#7c3aed,#a855f7)",
                                        color="white", border_radius="6px", cursor="pointer",
                                        _hover={"opacity": "0.9"},
                                    ),
                                    rx.button(
                                        rx.icon("x", size=12),
                                        on_click=UploadState.cancel_edit_caption,
                                        size="1", variant="ghost",
                                        color_scheme="gray", cursor="pointer",
                                    ),
                                    spacing="2", align="center", width="100%",
                                ),
                                # ── Display mode ──
                                rx.hstack(
                                    rx.icon("message-circle", size=13, color=UploadState.sub_text_color),
                                    rx.text(
                                        rx.cond(
                                            UploadState.lightbox_caption != "",
                                            UploadState.lightbox_caption,
                                            "Add a caption…",
                                        ),
                                        size="1",
                                        color=rx.cond(
                                            UploadState.lightbox_caption != "",
                                            UploadState.text_color,
                                            "#4b5563",
                                        ),
                                        font_style=rx.cond(
                                            UploadState.lightbox_caption != "",
                                            "normal",
                                            "italic",
                                        ),
                                        flex="1",
                                    ),
                                    rx.icon(
                                        "pencil",
                                        size=12,
                                        color=UploadState.sub_text_color,
                                        cursor="pointer",
                                        on_click=UploadState.start_edit_caption,
                                        _hover={"color": "#a78bfa"},
                                    ),
                                    spacing="2", align="center", width="100%",
                                ),
                            ),
                            rx.divider(color="rgba(0,0,0,0.06)", margin_y="8px"),
                            rx.vstack(
                                rx.hstack(
                                    rx.icon("sparkles", size=14, color="#7c3aed"),
                                    rx.text("Similar Discoveries", size="2", weight="bold", color=UploadState.text_color),
                                    rx.cond(UploadState.ai_loading, rx.spinner(size="1")),
                                    spacing="2", align="center",
                                ),
                                rx.hstack(
                                    rx.foreach(UploadState.image_labels, lambda label: rx.badge(label, variant="soft", color_scheme="purple", size="1", border_radius="full")),
                                    wrap="wrap", spacing="1",
                                ),
                                rx.cond(
                                    UploadState.similar_photos.length() > 0,
                                    rx.scroll_area(
                                        rx.hstack(
                                            rx.foreach(UploadState.similar_photos, lambda photo: rx.link(
                                                rx.image(src=photo["thumbnail"], width="140px", height="90px", object_fit="cover", border_radius="10px", transition="transform 0.2s", _hover={"transform": "scale(1.04)", "box_shadow": "0 10px 25px rgba(0,0,0,0.2)"}),
                                                href=photo["url"], is_external=True,
                                            )),
                                            spacing="3", padding="8px 4px 16px 4px",
                                        ),
                                        type="hover", scrollbars="horizontal", style={"width": "100%"},
                                    ),
                                ),
                                spacing="3", align="start", width="100%", padding_top="4px",
                            ),
                            spacing="2",
                            width="100%",
                        ),
                        padding="12px 18px",
                        background="rgba(255,255,255,0.92)",
                        border_radius="10px",
                        border="1px solid rgba(124,58,237,0.2)",
                        backdrop_filter="blur(12px)",
                        width="100%",
                        max_width="70vw",
                    ),
                    # ── Info Icon toggle EXIF ──
                    rx.button(
                        rx.icon("info", size=14),
                        on_click=UploadState.toggle_exif_panel,
                        size="1", variant="ghost",
                        color=UploadState.text_color,
                        opacity="0.6",
                        position="absolute", top="8px", right="8px",
                        cursor="pointer",
                        _hover={"opacity": "1", "background": "rgba(255,255,255,0.1)"},
                    ),

                    # ── EXIF Info Panel ──
                    rx.cond(
                        UploadState.show_exif_panel,
                        rx.box(
                            rx.vstack(
                                rx.hstack(
                                    rx.text("Metadata", size="1", weight="bold", color=UploadState.text_color),
                                    rx.spacer(),
                                    rx.icon("x", size=12, cursor="pointer", on_click=UploadState.toggle_exif_panel),
                                    width="100%", align="center",
                                ),
                                rx.divider(opacity="0.1"),
                                rx.scroll_area(
                                    rx.vstack(
                                        rx.foreach(
                                            UploadState.lightbox_exif,
                                            lambda item: rx.hstack(
                                                rx.text(item[0], size="1", color=UploadState.sub_text_color, width="90px", overflow="hidden", text_overflow="ellipsis"),
                                                rx.text(item[1], size="1", weight="medium", color=UploadState.text_color, flex="1"),
                                                width="100%", align="start", spacing="2",
                                            )
                                        ),
                                        spacing="2", width="100%",
                                    ),
                                    style={"height": "160px"},
                                ),
                                spacing="2",
                            ),
                            position="absolute", bottom="80px", right="-40px",
                            background=UploadState.bg_card,
                            border="1px solid " + UploadState.border_color,
                            border_radius="12px", padding="12px", width="260px",
                            box_shadow="0 10px 40px rgba(0,0,0,0.3)",
                            z_index="10",
                            backdrop_filter="blur(10px)",
                        ),
                        rx.box(),
                    ),
                    spacing="3",
                    align="center",
                    position="relative",
                    z_index="1",
                ),

                # ── Next arrow ──
                rx.box(
                    rx.button(
                        rx.icon("chevron-right", size=28),
                        on_click=UploadState.next_image,
                        size="3",
                        variant="ghost",
                        color_scheme="gray",
                        border_radius="50%",
                        background="rgba(255,255,255,0.08)",
                        _hover={"background": "rgba(255,255,255,0.18)"},
                        disabled=~UploadState.preview_has_next,
                        opacity=rx.cond(UploadState.preview_has_next, "1", "0.2"),
                        cursor=rx.cond(UploadState.preview_has_next, "pointer", "default"),
                    ),
                    position="relative",
                    z_index="2",
                ),

                spacing="6",
                align="center",
                justify="center",
                width="100%",
            ),

            # ── Close button ──
            rx.button(
                rx.icon("x", size=20),
                on_click=UploadState.close_preview,
                position="fixed",
                top="20px", right="24px",
                z_index="2001",
                variant="ghost",
                color_scheme="gray",
                size="3",
                border_radius="50%",
                background="rgba(255,255,255,0.1)",
                _hover={"background": "rgba(255,255,255,0.2)"},
            ),

            # overlay container
            position="fixed",
            top="0", left="0",
            width="100vw", height="100vh",
            background="rgba(0,0,0,0.92)",
            backdrop_filter="blur(14px)",
            display="flex",
            align_items="center",
            justify_content="center",
            z_index="2000",
        ),
        rx.box(),
    )


def image_card(img: rx.Base) -> rx.Component:
    """Card for a single image — real thumbnail, tag badges, preview on click."""
    return rx.box(
        rx.vstack(
            # ── Real thumbnail (click to preview or select) ──
            rx.box(
                rx.image(
                    src=img.full_url,
                    width="100%",
                    height=UploadState.thumb_height,
                    object_fit="cover",
                    border_radius="10px",
                    display="block",
                ),
                # Checkmark overlay when selected
                rx.cond(
                    UploadState.selected_image_ids.contains(img.id),
                    rx.box(
                        rx.icon("check", size=16, color="white"),
                        position="absolute",
                        top="8px", right="8px",
                        background="rgba(124,58,237,0.9)",
                        border_radius="50%",
                        width="28px", height="28px",
                        display="flex",
                        align_items="center",
                        justify_content="center",
                    ),
                    rx.box(),
                ),
                # 🌐/🔒 Visibility toggle (top-left) — click to flip
                rx.cond(
                    img.is_public,
                    rx.box(
                        rx.icon("globe", size=12, color="white"),
                        position="absolute",
                        top="8px", left="8px",
                        background="rgba(34,197,94,0.85)",
                        border_radius="999px",
                        padding="3px 8px",
                        display="flex",
                        align_items="center",
                        justify_content="center",
                        backdrop_filter="blur(4px)",
                        border="1px solid rgba(255,255,255,0.2)",
                        cursor="pointer",
                        title="Public — click to make private",
                        _hover={"background": "rgba(239,68,68,0.75)"},
                        transition="background 0.2s ease",
                        on_click=UploadState.toggle_image_public(img.id),
                        z_index="3",
                    ),
                    rx.box(
                        rx.icon("lock", size=12, color="white"),
                        position="absolute",
                        top="8px", left="8px",
                        background="rgba(107,114,128,0.8)",
                        border_radius="999px",
                        padding="3px 8px",
                        display="flex",
                        align_items="center",
                        justify_content="center",
                        backdrop_filter="blur(4px)",
                        border="1px solid rgba(255,255,255,0.15)",
                        cursor="pointer",
                        title="Private — click to make public",
                        _hover={"background": "rgba(34,197,94,0.75)"},
                        transition="background 0.2s ease",
                        on_click=UploadState.toggle_image_public(img.id),
                        z_index="3",
                    ),
                ),
                width="100%",
                overflow="hidden",
                border_radius="10px",
                cursor="pointer",
                on_click=lambda e: UploadState.select_image(img.id, img.filename, e.shift_key),
                _hover={"opacity": "0.82"},
                transition="opacity 0.15s ease",
                position="relative",
            ),
            # ── File info ──
            rx.vstack(
                rx.text(
                    img.original_filename,
                    size="2",
                    weight="bold",
                    color=UploadState.text_color,
                    white_space="nowrap",
                    overflow="hidden",
                    text_overflow="ellipsis",
                    max_width="160px",
                ),
                rx.cond(
                    img.folder_name != "",
                    rx.hstack(
                        rx.icon("folder", size=12, color="#7c3aed"),
                        rx.text(img.folder_name, size="1", color="#7c3aed"),
                        spacing="1",
                        align="center",
                    ),
                    rx.box(),
                ),
                rx.hstack(
                    rx.cond(
                        img.is_large,
                        rx.text(img.size_mb, " MB", size="1", color=UploadState.sub_text_color),
                        rx.text(img.size_kb, " KB", size="1", color=UploadState.sub_text_color),
                    ),
                    rx.cond(
                        img.was_compressed,
                        rx.badge("Compressed", color_scheme="purple", size="1"),
                        rx.box(),
                    ),
                    spacing="2",
                    align="center",
                ),
                spacing="1",
                align="start",
                width="100%",
            ),
            # ── Tag assign dropdown ──
            rx.select(
                UploadState.tag_names,
                placeholder="+ Add tag…",
                on_change=lambda tag_name: UploadState.assign_tag_by_name(
                    img.id, tag_name
                ),
                size="1",
                width="100%",
                background=UploadState.bg_theme,
                border="1px solid #e5e7eb",
                border_radius="8px",
                color="#7c3aed",
            ),
            # ── Assigned tag badges (FIXED: uses .contains()) ──
            rx.foreach(
                UploadState.tags,
                lambda t: rx.cond(
                    img.tag_ids.contains(t.id),
                    rx.hstack(
                        rx.box(
                            width="8px", height="8px",
                            border_radius="50%",
                            background=t.color,
                        ),
                        rx.text(t.name, size="1", color=UploadState.text_color),
                        rx.icon(
                            "x",
                            size=10,
                            color="#9ca3af",
                            cursor="pointer",
                            on_click=UploadState.remove_tag(img.id, t.id),
                        ),
                        spacing="1",
                        align="center",
                        padding="3px 8px",
                        background="#f3f4f6",
                        border_radius="999px",
                        border="1px solid #e5e7eb",
                    ),
                    rx.box(),
                ),
            ),
            # ── Move to folder ──
            rx.select(
                UploadState.folders_with_none,
                placeholder="Move to folder…",
                on_change=lambda f: UploadState.assign_folder(img.id, f),
                size="1",
                width="100%",
                background=UploadState.bg_theme,
                border="1px solid #e5e7eb",
                border_radius="8px",
                color="#7c3aed",
            ),
            # ── Delete ──
            rx.button(
                rx.icon("trash-2", size=14),
                "Delete",
                on_click=UploadState.delete_image(img.id),
                size="1",
                variant="ghost",
                color_scheme="red",
                width="100%",
            ),
            spacing="3",
            align="start",
            width="100%",
        ),
        padding="16px",
        background=UploadState.bg_theme,
        border=rx.cond(
            UploadState.selected_image_ids.contains(img.id),
            "2px solid #7c3aed",
            "1px solid #f1f1f1",
        ),
        border_radius="16px",
        width=UploadState.card_width,
        _hover={
            "border_color": "#7c3aed",
            "background": "#f9fafb",
            "transform": "translateY(-2px)",
            "box_shadow": "0 8px 30px rgba(0,0,0,0.05)",
        },
        transition="all 0.2s ease",
    )


def image_list_row(img: rx.Base) -> rx.Component:
    """Compact list-view row for a single image."""
    return rx.hstack(
        rx.image(
            src=img.full_url,
            width="56px",
            height="42px",
            object_fit="cover",
            border_radius="6px",
            cursor="pointer",
            on_click=UploadState.on_image_click(img.id, img.filename),
            flex_shrink="0",
            _hover={"opacity": "0.8"},
            transition="opacity 0.15s ease",
        ),
        rx.text(
            img.original_filename,
            size="2",
            weight="medium",
            color=UploadState.text_color,
            flex="1",
            overflow="hidden",
            text_overflow="ellipsis",
            white_space="nowrap",
            min_width="0",
        ),
        rx.cond(
            img.folder_name != "",
            rx.hstack(
                rx.icon("folder", size=12, color="#7c3aed"),
                rx.text(img.folder_name, size="1", color="#7c3aed", white_space="nowrap"),
                spacing="1",
                align="center",
            ),
            rx.text("—", size="1", color="#9ca3af"),
        ),
        rx.cond(
            img.is_large,
            rx.text(img.size_mb, " MB", size="1", color=UploadState.sub_text_color, white_space="nowrap"),
            rx.text(img.size_kb, " KB", size="1", color=UploadState.sub_text_color, white_space="nowrap"),
        ),
        rx.hstack(
            rx.foreach(
                UploadState.tags,
                lambda t: rx.cond(
                    img.tag_ids.contains(t.id),
                    rx.box(width="10px", height="10px", border_radius="50%", background=t.color, flex_shrink="0"),
                    rx.box(),
                ),
            ),
            spacing="1",
        ),
        rx.cond(img.was_compressed, rx.badge("Compressed", color_scheme="purple", size="1"), rx.box()),
        rx.button(
            rx.icon("trash-2", size=14),
            on_click=UploadState.delete_image(img.id),
            size="1",
            variant="ghost",
            color_scheme="red",
            flex_shrink="0",
        ),
        spacing="4",
        align="center",
        width="100%",
        padding="8px 12px",
        border_radius="10px",
        _hover={"background": "#f9fafb"},
        transition="background 0.2s ease",
    )

def tag_row(t: rx.Base) -> rx.Component:
    return rx.hstack(
        rx.box(width="12px", height="12px", border_radius="50%", background=t.color),
        rx.text(t.name, size="2", color=UploadState.text_color, flex="1"),
        rx.button(
            rx.icon("trash-2", size=12),
            on_click=UploadState.delete_tag(t.id),
            size="1",
            variant="ghost",
            color_scheme="red",
        ),
        spacing="2",
        align="center",
        width="100%",
        padding="6px 8px",
        border_radius="8px",
        _hover={"background": "#f9fafb"},
        transition="background 0.2s ease",
    )

def folder_chip(folder: str) -> rx.Component:
    is_public = UploadState.public_folders.contains(folder)
    return rx.box(
        rx.hstack(
            rx.hstack(
                rx.icon("folder", size=14, color=UploadState.accent_hex),
                rx.text(folder, size="2", color=UploadState.text_color, flex="1"),
                spacing="2",
                align="center",
                cursor="pointer",
                on_click=UploadState.set_folder_filter(folder),
            ),
            rx.spacer(),
            # Public/Private Toggle
            rx.button(
                rx.cond(
                    is_public,
                    rx.icon("globe", size=12, color="#22c55e"),
                    rx.icon("lock", size=12, color=UploadState.sub_text_color),
                ),
                on_click=lambda: UploadState.toggle_folder_public(folder),
                size="1",
                variant="ghost",
                color_scheme=rx.cond(is_public, "green", "gray"),
                title=rx.cond(is_public, "Public collection", "Private collection"),
                cursor="pointer",
            ),
            rx.button(
                rx.icon("pencil", size=12),
                on_click=UploadState.start_rename_folder(folder),
                size="1",
                variant="ghost",
                color_scheme="purple",
                title="Rename folder",
            ),
            rx.button(
                rx.icon("download", size=12),
                on_click=UploadState.export_folder(folder),
                size="1",
                variant="ghost",
                color_scheme="green",
                title="Download folder (ZIP)",
            ),
            rx.button(
                rx.icon("trash-2", size=12),
                on_click=UploadState.delete_folder(folder),
                size="1",
                variant="ghost",
                color_scheme="red",
                title="Delete folder",
            ),
            spacing="1",
            align="center",
            width="100%",
        ),
        padding="8px 12px",
        background=UploadState.bg_theme,
        border="1px solid " + UploadState.border_color,
        border_radius="10px",
        width="100%",
        _hover={"background": "#f9fafb", "border_color": "#e2e2e2"},
        transition="all 0.2s ease",
    )


def folder_filter_btn(folder: str) -> rx.Component:
    is_active = UploadState.folder_filter == folder
    return rx.button(
        folder,
        on_click=UploadState.set_folder_filter(folder),
        size="1",
        variant=rx.cond(is_active, "solid", "ghost"),
        color_scheme="purple",
        color=rx.cond(is_active, "white", UploadState.sub_text_color),
    )


def tag_filter_btn(tag: rx.Base) -> rx.Component:
    """Task F: Filter gallery by tag."""
    return rx.button(
        rx.hstack(
            rx.box(width="8px", height="8px", border_radius="50%", background=tag.color),
            rx.text(tag.name, size="1"),
            spacing="1",
            align="center",
        ),
        on_click=UploadState.set_tag_filter(tag.id.to_string()),
        size="1",
        variant=rx.cond(UploadState.tag_filter == tag.id.to_string(), "solid", "ghost"),
        color_scheme="purple",
    )


def tag_row(tag: rx.Base) -> rx.Component:
    """A single tag row in the management panel."""
    return rx.hstack(
        rx.box(
            width="12px", height="12px",
            border_radius="50%",
            background=tag.color,
            flex_shrink="0",
            
        ),
        rx.text(tag.name, size="2", color=UploadState.text_color, flex="1"),
        rx.icon(
            "trash-2", size=14, color="#ef4444",
            cursor="pointer",
            on_click=UploadState.delete_tag(tag.id),
        ),
        spacing="2",
        align="center",
        width="100%",
        padding="6px 10px",
        border_radius="8px",
        background="#f9fafb",
        border="1px solid #e5e7eb",
    )


def tag_management_panel() -> rx.Component:
    """Tasks A/B/C/D/F/G: Tag Management panel."""
    return rx.box(
        rx.vstack(
            rx.hstack(
                rx.icon("tag", size=18, color=UploadState.accent_hex),
                rx.text("Tags", size="3", weight="bold", color=UploadState.text_color),
                spacing="2",
                align="center",
            ),
            # Create tag row
            rx.hstack(
                rx.input(
                    placeholder="New tag name…",
                    value=UploadState.new_tag_name,
                    on_change=UploadState.set_new_tag_name,
                    size="2",
                    background=UploadState.bg_theme,
                    border="1px solid #e2e2e2",
                    border_radius="10px",
                    color=UploadState.text_color,
                    flex="1",
                ),
                rx.input(
                    type="color",
                    value=UploadState.new_tag_color,
                    on_change=UploadState.set_new_tag_color,
                    width="40px",
                    height="36px",
                    padding="2px",
                    border="1px solid #e2e2e2",
                    border_radius="8px",
                    background="transparent",
                    cursor="pointer",
                ),
                rx.button(
                    rx.icon("plus", size=16),
                    "Create",
                    on_click=UploadState.create_tag,
                    size="2",
                    background="linear-gradient(135deg, #7c3aed, #a855f7)",
                    color="white",
                    border_radius="10px",
                    cursor="pointer",
                ),
                spacing="2",
                width="100%",
            ),
            # Search tags (Task F)
            rx.input(
                placeholder="Search tags…",
                value=UploadState.tag_search,
                on_change=UploadState.set_tag_search,
                size="1",
                background="#f9fafb",
                border="1px solid #e5e7eb",
                border_radius="8px",
                color=UploadState.text_color,
                width="100%",
            ),
            # Tag list
            rx.cond(
                UploadState.filtered_tags.length() > 0,
                rx.box(
                    rx.vstack(
                        rx.foreach(UploadState.filtered_tags, tag_row),
                        spacing="2",
                    ),
                    max_height="200px",
                    overflow_y="auto",
                    width="100%",
                ),
                rx.text("No tags yet.", size="2", color=UploadState.sub_text_color, text_align="center"),
            ),
            spacing="3",
            width="100%",
        ),
        padding="24px",
        background=UploadState.bg_theme,
        border="1px solid " + UploadState.border_color,
        border_radius="20px",
        width="320px",
        flex_shrink="0",
    )


def upload_zone() -> rx.Component:
    return rx.upload(
        rx.vstack(
            rx.cond(
                UploadState.is_uploading,
                rx.vstack(
                    rx.spinner(size="3", color="#a855f7"),
                    rx.text("Uploading…", size="3", color="#a78bfa"),
                    spacing="3",
                    align="center",
                ),
                rx.vstack(
                    rx.icon("cloud-upload", size=48, color=UploadState.accent_hex, opacity="0.6"),
                    rx.text("Drop images here or click to browse", size="3", color=UploadState.text_color, weight="medium"),
                    rx.text("PNG, JPG, GIF or WEBP · up to 10MB each", size="2", color=UploadState.sub_text_color),
                    spacing="2",
                    align="center",
                ),
            ),
            justify="center",
            align="center",
            min_height="200px",
            width="100%",
        ),
        id="upload_dropzone",
        multiple=True,
        accept={
            "image/jpeg": [".jpg", ".jpeg"],
            "image/png": [".png"],
            "image/gif": [".gif"],
            "image/webp": [".webp"],
        },
        max_files=50,
        on_drop=UploadState.handle_upload(rx.upload_files(upload_id="upload_dropzone")),
        border="2px dashed #e2e8f0",
        padding="40px",
        border_radius="16px",
        background=UploadState.bg_theme,
        _hover={"border_color": UploadState.accent_hex, "background": "#f9fafb"},
        transition="all 0.2s ease",
        cursor="pointer",
        width="100%",
    )


# ─────────────────────────────────────────────
#  Extra components
# ─────────────────────────────────────────────

# ── Preferences panel data ────────────────────────────────────────────────────────────────
_THEMES = [
    ("Snow",       "#ffffff", "#f3f4f6", "#ffffff"),
    ("Cloud",      "#f9fafb", "#f3f4f6", "#f9fafb"),
    ("Deep Space", "#1a0a3e", "#3d1a7a", "radial-gradient(ellipse at 20% 0%, #1a0a3e 0%, #080514 60%, #030208 100%)"),
    ("Midnight",   "#0a1438", "#1a2a5e", "radial-gradient(ellipse at 20% 0%, #0a1438 0%, #050a19 60%, #020408 100%)"),
    ("Void",       "#111111", "#222222", "linear-gradient(160deg, #141414 0%, #060606 100%)"),
]
_ACCENTS = [
    ("Violet", "#7c3aed", "#a855f7"),
    ("Cobalt", "#1d4ed8", "#60a5fa"),
    ("Teal",   "#0d9488", "#2dd4bf"),
    ("Rose",   "#be185d", "#f472b6"),
    ("Amber",  "#b45309", "#fbbf24"),
]


def _theme_swatch(name: str, dark: str, mid: str, gradient: str) -> rx.Component:
    is_active = UploadState.bg_theme == gradient
    return rx.tooltip(
        rx.box(
            # Checkmark shown when active
            rx.cond(
                is_active,
                rx.center(
                    rx.icon("check", size=14, color="white"),
                    position="absolute",
                    top="0", left="0",
                    width="100%", height="100%",
                    background="rgba(0,0,0,0.35)",
                    border_radius="12px",
                ),
                rx.box(),
            ),
            position="relative",
            width="44px",
            height="44px",
            border_radius="12px",
            background=f"linear-gradient(135deg, {mid} 0%, {dark} 100%)",
            border=rx.cond(
                is_active,
                "2.5px solid white",
                "2.5px solid rgba(255,255,255,0.08)",
            ),
            cursor="pointer",
            on_click=UploadState.set_bg_theme(gradient),
            _hover={"transform": "scale(1.1)", "border_color": "rgba(255,255,255,0.5)", "z_index": "1"},
            transition="all 0.18s ease",
            box_shadow=rx.cond(
                is_active,
                f"0 0 0 3px {mid}55, 0 4px 14px rgba(0,0,0,0.5)",
                "0 3px 10px rgba(0,0,0,0.5)",
            ),
        ),
        content=name,
    )


def _accent_swatch(name: str, main: str, light: str) -> rx.Component:
    is_active = UploadState.accent_hex == main
    return rx.tooltip(
        rx.box(
            rx.cond(
                is_active,
                rx.center(
                    rx.icon("check", size=13, color="white"),
                    position="absolute",
                    top="0", left="0",
                    width="100%", height="100%",
                    border_radius="50%",
                ),
                rx.box(),
            ),
            position="relative",
            width="38px",
            height="38px",
            border_radius="50%",
            background=f"linear-gradient(135deg, {main}, {light})",
            border=rx.cond(
                is_active,
                "2.5px solid white",
                "2.5px solid rgba(255,255,255,0.08)",
            ),
            cursor="pointer",
            on_click=UploadState.set_accent(main, light),
            _hover={"transform": "scale(1.15)", "border_color": f"{light}"},
            transition="all 0.18s ease",
            box_shadow=rx.cond(
                is_active,
                f"0 0 0 3px {main}55, 0 4px 14px {main}66",
                f"0 3px 10px {main}44",
            ),
        ),
        content=name,
    )


def _pref_row(label: str, control: rx.Component, sublabel: str = "") -> rx.Component:
    return rx.hstack(
        rx.vstack(
            rx.text(label, size="2", color=UploadState.text_color, weight="medium"),
            rx.cond(
                sublabel != "",
                rx.text(sublabel, size="1", color=UploadState.sub_text_color),
                rx.box(),
            ),
            spacing="0", align="start",
        ),
        rx.spacer(),
        control,
        align="center",
        width="100%",
        padding="12px 16px",
        border_radius="10px",
        _hover={"background": "#f1f1f1"},
        transition="all 0.2s ease",
    )


def _section_header(title: str) -> rx.Component:
    return rx.text(
        title,
        size="2",
        weight="bold",
        color=UploadState.sub_text_color,
        padding="16px 16px 8px 16px",
    )



def settings_panel() -> rx.Component:
    """Slide-in Preferences drawer."""
    return rx.cond(
        UploadState.settings_open,
        rx.box(
            # ─ Backdrop ──────────────────────────────────────────────────
            rx.box(
                position="fixed", top="0", left="0",
                width="100vw", height="100vh",
                background="rgba(0,0,0,0.1)",
                z_index="1499",
                on_click=UploadState.close_settings,
            ),
            # ─ Panel ─────────────────────────────────────────────────────
            rx.box(
                rx.vstack(

                    # ── Header ───────────────────────────────────────────
                    rx.hstack(
                        rx.heading("Settings & Support", size="5", weight="bold", color=UploadState.text_color),
                        rx.button(
                            rx.icon("x", size=20),
                            on_click=UploadState.close_settings,
                            size="2", variant="ghost",
                            color=UploadState.text_color,
                            border_radius="50%",
                            cursor="pointer",
                            _hover={"background": "rgba(0,0,0,0.05)"},
                        ),
                        justify="between", width="100%", align="center",
                        padding="12px 16px",
                        border_bottom="1px solid " + UploadState.border_color,
                    ),

                    rx.box(
                        rx.vstack(
                            _section_header("Settings"),
                            _pref_row(
                                "Profile Visibility",
                                rx.switch(
                                    checked=True, # Placeholder
                                    checked_track_color="black",
                                ),
                                sublabel="Show your profile in search",
                            ),
                            _pref_row(
                                "Stats Bar",
                                rx.switch(
                                    checked=UploadState.show_stats_bar,
                                    on_change=UploadState.toggle_stats_bar,
                                    checked_track_color="black",
                                ),
                                sublabel="Show storage & image stats",
                            ),

                            rx.divider(color="#f1f1f1", margin="8px 0"),

                            _section_header("Appearance"),
                            rx.vstack(
                                rx.text("Accent Color", size="2", color=UploadState.text_color, weight="medium", padding_left="16px"),
                                rx.hstack(
                                    *[_accent_swatch(n, m, l) for n, m, l in _ACCENTS],
                                    spacing="3",
                                    padding="8px 16px",
                                ),
                                spacing="2", align="start", width="100%",
                            ),

                            rx.divider(color="#f1f1f1", margin="8px 0"),

                            _section_header("Gallery Layout"),
                            _pref_row(
                                "Card Size",
                                rx.select(
                                    ["Small", "Medium", "Large"],
                                    value=UploadState.card_size.capitalize(),
                                    on_change=lambda v: UploadState.set_card_size(v.lower()),
                                    size="1",
                                    variant="soft",
                                    color_scheme="gray",
                                ),
                            ),
                            _pref_row(
                                "Sort By",
                                rx.select(
                                    ["Newest first", "Oldest first", "A → Z", "Z → A", "Largest first"],
                                    value=UploadState.sort_by,
                                    on_change=UploadState.set_sort_by,
                                    size="1",
                                    variant="soft",
                                    color_scheme="gray",
                                ),
                            ),

                            rx.divider(color="#f1f1f1", margin="8px 0"),

                            _section_header("Support"),
                            rx.hstack(
                                rx.text("Help Center", size="2", color=UploadState.text_color, weight="medium"),
                                rx.spacer(),
                                rx.icon("external-link", size=14, color=UploadState.sub_text_color),
                                padding="12px 16px",
                                border_radius="10px",
                                width="100%",
                                cursor="pointer",
                                _hover={"background": "#f1f1f1"},
                            ),
                            rx.hstack(
                                rx.text("Privacy Policy", size="2", color=UploadState.text_color, weight="medium"),
                                rx.spacer(),
                                rx.icon("external-link", size=14, color=UploadState.sub_text_color),
                                padding="12px 16px",
                                border_radius="10px",
                                width="100%",
                                cursor="pointer",
                                _hover={"background": "#f1f1f1"},
                            ),

                            rx.divider(color="#f1f1f1", margin="8px 0"),

                            _section_header("Export & Backup"),
                            rx.hstack(
                                rx.vstack(
                                    rx.text("Digital Portfolio", size="2", color=UploadState.text_color, weight="medium"),
                                    rx.text("Self-contained HTML gallery", size="1", color=UploadState.sub_text_color),
                                    spacing="0", align="start",
                                ),
                                rx.spacer(),
                                rx.button(
                                    rx.icon("download", size=14),
                                    "Export",
                                    on_click=UploadState.export_portfolio,
                                    size="2", variant="surface", color_scheme="purple",
                                    cursor="pointer",
                                ),
                                padding="12px 16px",
                                width="100%",
                            ),
                            rx.cond(
                                UploadState.export_status != "",
                                rx.box(
                                    rx.text(UploadState.export_status, size="1", color="#7c3aed", padding_left="16px"),
                                    padding_bottom="8px",
                                ),
                            ),

                            rx.divider(color="#f1f1f1", margin="8px 0"),

                            _section_header("Resources"),
                            rx.hstack(
                                rx.text("About", size="1", color=UploadState.sub_text_color, weight="bold", cursor="pointer", _hover={"text_decoration": "underline"}),
                                rx.text("Blog", size="1", color=UploadState.sub_text_color, weight="bold", cursor="pointer", _hover={"text_decoration": "underline"}),
                                rx.text("Careers", size="1", color=UploadState.sub_text_color, weight="bold", cursor="pointer", _hover={"text_decoration": "underline"}),
                                spacing="4",
                                padding="8px 16px",
                            ),

                            spacing="0",
                            width="100%",
                            padding_bottom="40px",
                        ),
                        width="100%",
                        overflow_y="auto",
                    ),

                    spacing="5",
                    align="start",
                    width="100%",
                    padding_bottom="40px",
                ),
                # Panel styles
                background=UploadState.bg_theme,
                border_left="1px solid #f1f1f1",
                width="380px",
                height="100vh",
                position="fixed",
                top="0",
                right="0",
                z_index="1500",
                box_shadow="-10px 0 30px rgba(0,0,0,0.05)",
                transition="all 0.3s ease-in-out",
            ),
        ),
        rx.box(),
    )

def stats_bar() -> rx.Component:
    """Live stats: total images, storage used, folders, tags."""
    def tile(icon: str, value: rx.Var, label: str) -> rx.Component:
        return rx.box(
            rx.vstack(
                rx.hstack(
                    rx.icon(icon, size=18, color=UploadState.accent_hex),
                    rx.text(value, size="5", weight="bold", color=UploadState.text_color),
                    spacing="2",
                    align="center",
                ),
                rx.text(label, size="1", color=UploadState.sub_text_color),
                spacing="1",
                align="start",
            ),
            padding="16px 20px",
            background=UploadState.bg_theme,
            border="1px solid " + UploadState.border_color,
            border_radius="14px",
            flex="1",
            min_width="110px",
        )
    return rx.hstack(
        tile("images", UploadState.total_images, "Images"),
        tile("database", UploadState.used_storage_mb, "MB Used"),
        tile("folder", UploadState.folder_count, "Folders"),
        tile("tag", UploadState.tag_count, "Tags"),
        spacing="4",
        width="100%",
        flex_wrap="wrap",
    )


def rename_folder_modal() -> rx.Component:
    return rx.cond(
        UploadState.renaming_folder != "",
        rx.box(
            rx.box(
                rx.vstack(
                    rx.hstack(
                        rx.icon("pencil", size=22, color=UploadState.accent_hex),
                        rx.heading("Rename Folder", size="5", color=UploadState.text_color),
                        spacing="3",
                        align="center",
                    ),
                    rx.text(
                        'Renaming: "', UploadState.renaming_folder, '"',
                        size="2", color=UploadState.sub_text_color,
                    ),
                    rx.input(
                        value=UploadState.rename_folder_input,
                        on_change=UploadState.set_rename_folder_input,
                        size="3",
                        background=UploadState.bg_theme,
                        border="1px solid #e2e2e2",
                        border_radius="10px",
                        color=UploadState.text_color,
                        width="100%",
                        auto_focus=True,
                    ),
                    rx.hstack(
                        rx.button(
                            "Cancel",
                            on_click=UploadState.cancel_rename_folder,
                            variant="ghost",
                            color_scheme="gray",
                            size="3",
                        ),
                        rx.button(
                            rx.icon("check", size=16),
                            "Rename",
                            on_click=UploadState.confirm_rename_folder,
                            size="3",
                            background=rx.color_mode_cond(
                                light=f"linear-gradient(135deg, {UploadState.accent_hex}, {UploadState.accent_light})",
                                dark=f"linear-gradient(135deg, {UploadState.accent_hex}, {UploadState.accent_light})",
                            ),
                            color="white",
                            border_radius="10px",
                            cursor="pointer",
                        ),
                        spacing="3",
                        justify="end",
                        width="100%",
                    ),
                    spacing="4",
                    width="100%",
                ),
                padding="32px",
                background=UploadState.bg_theme,
                border="1px solid #e5e7eb",
                border_radius="20px",
                width="400px",
                box_shadow="0 25px 60px rgba(0,0,0,0.1)",
            ),
            position="fixed",
            top="0", left="0",
            width="100vw", height="100vh",
            background="rgba(0,0,0,0.1)",
            backdrop_filter="blur(4px)",
            display="flex",
            align_items="center",
            justify_content="center",
            z_index="1500",
        ),
        rx.box(),
    )


def bulk_action_bar() -> rx.Component:
    return rx.cond(
        UploadState.selection_mode,
        rx.box(
            rx.hstack(
                rx.hstack(
                    rx.icon("square-check", size=18, color=UploadState.accent_hex),
                    rx.text(UploadState.bulk_count, " selected", size="2", weight="medium", color=UploadState.text_color),
                    spacing="2",
                    align="center",
                ),
                rx.hstack(
                    rx.button("Select All", on_click=UploadState.select_all, size="2", variant="ghost", color_scheme="purple"),
                    rx.button("Clear", on_click=UploadState.clear_selection, size="2", variant="ghost", color_scheme="gray"),
                    rx.select(
                        UploadState.folders_with_none,
                        placeholder="Move selected to…",
                        on_change=UploadState.bulk_move,
                        size="2",
                        background=UploadState.bg_theme,
                        border="1px solid #e5e7eb",
                        border_radius="8px",
                        color=UploadState.text_color,
                    ),
                    rx.button(
                        rx.icon("trash-2", size=14),
                        "Delete Selected",
                        on_click=UploadState.bulk_delete,
                        size="2",
                        background="rgba(239,68,68,0.08)",
                        border="1px solid rgba(239,68,68,0.2)",
                        border_radius="8px",
                        color="#ef4444",
                        cursor="pointer",
                    ),
                    rx.button("Done", on_click=UploadState.toggle_selection_mode, size="2", variant="ghost", color_scheme="gray"),
                    spacing="2",
                    align="center",
                    flex_wrap="wrap",
                ),
                justify="between",
                align="center",
                width="100%",
                flex_wrap="wrap",
                gap="3",
            ),
            padding="14px 20px",
            background="#f9fafb",
            border="1px solid " + UploadState.border_color,
            border_radius="14px",
            width="100%",
        ),
        rx.box(),
    )


# ─────────────────────────────────────────────
#  Main page
# ─────────────────────────────────────────────

def import_export_page() -> rx.Component:
    return rx.box(
        duplicate_modal(),
        lightbox_modal(),
        rename_folder_modal(),
        settings_panel(),
        toast_notification(),
        rx.vstack(
            # ── Header ──
            rx.hstack(
                rx.hstack(
                    rx.box(
                        rx.icon("layers", size=28, color="white"),
                        padding="10px",
                        background="linear-gradient(135deg, #7c3aed, #a855f7)",
                        border_radius="14px",
                        box_shadow="0 4px 20px rgba(124,58,237,0.4)",
                    ),
                    rx.vstack(
                        rx.heading("Media Library", size="6", color=UploadState.text_color),
                        rx.text("Import · Manage · Export", size="2", color=UploadState.sub_text_color),
                        spacing="0",
                        align="start",
                    ),
                    spacing="4",
                    align="center",
                ),
                storage_bar(),
                justify="between",
                align="center",
                width="100%",
                flex_wrap="wrap",
                gap="4",
            ),

            rx.divider(color="#f1f1f1"),

            # ── Live stats (hideable) ──
            rx.cond(UploadState.show_stats_bar, stats_bar(), rx.box()),

                # Upload + Folder + Tags Row
            rx.hstack(
                # Upload zone
                rx.box(
                    rx.vstack(
                        rx.hstack(
                            rx.icon("upload", size=18, color="#7c3aed"),
                            rx.text("Import Images", size="3", weight="bold", color=UploadState.text_color),
                            spacing="2",
                            align="center",
                        ),
                        upload_zone(),
                        spacing="4",
                        width="100%",
                    ),
                    padding="24px",
                    background="#f9fafb",
                    border="1px solid " + UploadState.border_color,
                    border_radius="20px",
                    flex="1",
                    min_width="320px",
                ),

                # Folder management
                rx.box(
                    rx.vstack(
                        rx.hstack(
                            rx.icon("folder-plus", size=18, color="#7c3aed"),
                            rx.text("Folders", size="3", weight="bold", color=UploadState.text_color),
                            spacing="2",
                            align="center",
                        ),
                        rx.hstack(
                            rx.input(
                                placeholder="New folder name…",
                                value=UploadState.new_folder_name,
                                on_change=UploadState.set_new_folder_name,
                                size="2",
                                background=UploadState.bg_theme,
                                border="1px solid #e2e2e2",
                                border_radius="10px",
                                color=UploadState.text_color,
                                flex="1",
                            ),
                            rx.button(
                                rx.icon("plus", size=16),
                                "Create",
                                on_click=UploadState.create_folder,
                                size="2",
                                background="linear-gradient(135deg, #7c3aed, #a855f7)",
                                color="white",
                                border_radius="10px",
                                cursor="pointer",
                            ),
                            spacing="2",
                            width="100%",
                        ),
                        # Folder list
                        rx.cond(
                            UploadState.folders.length() > 0,
                            rx.box(
                                rx.vstack(
                                    rx.foreach(
                                        UploadState.folders,
                                        folder_chip,
                                    ),
                                    spacing="2",
                                    align="start",
                                ),
                                max_height="220px",
                                overflow_y="auto",
                                padding_right="4px",
                                width="100%",
                            ),
                            rx.box(
                                rx.text("No folders yet. Create one above!", size="2", color=UploadState.sub_text_color),
                                padding="20px",
                                text_align="center",
                                width="100%",
                            ),
                        ),
                        # Export status
                        rx.cond(
                            UploadState.export_status != "",
                            rx.box(
                                rx.hstack(
                                    rx.icon("download", size=14, color="#22c55e"),
                                    rx.text(UploadState.export_status, size="2", color="#86efac"),
                                    spacing="2",
                                    align="center",
                                ),
                                padding="10px 14px",
                                background="rgba(34,197,94,0.1)",
                                border="1px solid rgba(34,197,94,0.25)",
                                border_radius="10px",
                                width="100%",
                            ),
                            rx.box(),
                        ),
                        spacing="4",
                        width="100%",
                    ),
                    padding="24px",
                    background="rgba(255,255,255,0.03)",
                    border="1px solid rgba(124,58,237,0.2)",
                    border_radius="20px",
                    width="320px",
                    flex_shrink="0",
                ),

                # Tag management panel
                tag_management_panel(),

                spacing="5",
                align="start",
                width="100%",
                flex_wrap="wrap",
            ),

            # ── Image Gallery ──
            rx.box(
                rx.vstack(
                    # Title + search + sort + view toggle
                    rx.hstack(
                        rx.hstack(
                            rx.icon("images", size=18, color="#a78bfa"),
                            rx.text(
                                "Images (",
                                UploadState.image_count,
                                ")",
                                size="3",
                                weight="bold",
                                color="white",
                            ),
                            spacing="2",
                            align="center",
                        ),
                        rx.hstack(
                            rx.input(
                                placeholder="Search images…",
                                value=UploadState.search_query,
                                on_change=UploadState.set_search_query,
                                size="1",
                                width="160px",
                                background="rgba(255,255,255,0.06)",
                                border="1px solid rgba(124,58,237,0.3)",
                                border_radius="8px",
                                color="white",
                            ),
                            rx.select(
                                ["Newest first", "Oldest first", "A → Z", "Z → A", "Largest first"],
                                value=UploadState.sort_by,
                                on_change=UploadState.set_sort_by,
                                size="1",
                                background="rgba(255,255,255,0.06)",
                                border="1px solid rgba(124,58,237,0.3)",
                                border_radius="8px",
                                color="white",
                            ),
                            rx.hstack(
                                rx.button(
                                    rx.icon("layout-grid", size=15),
                                    on_click=UploadState.set_view_mode("grid"),
                                    size="1",
                                    variant=rx.cond(UploadState.view_mode == "grid", "solid", "ghost"),
                                    color_scheme="purple",
                                    title="Grid view",
                                ),
                                rx.button(
                                    rx.icon("list", size=15),
                                    on_click=UploadState.set_view_mode("list"),
                                    size="1",
                                    variant=rx.cond(UploadState.view_mode == "list", "solid", "ghost"),
                                    color_scheme="purple",
                                    title="List view",
                                ),
                                rx.button(
                                    rx.cond(
                                        UploadState.selection_mode,
                                        rx.icon("x", size=15),
                                        rx.icon("square-check", size=15),
                                    ),
                                    rx.cond(UploadState.selection_mode, "Cancel", "Select"),
                                    on_click=UploadState.toggle_selection_mode,
                                    size="1",
                                    variant=rx.cond(UploadState.selection_mode, "solid", "ghost"),
                                    color_scheme="purple",
                                    title="Toggle selection mode",
                                ),
                                spacing="1",
                            ),
                            spacing="2",
                            align="center",
                            flex_wrap="wrap",
                        ),
                        justify="between",
                        align="center",
                        width="100%",
                        flex_wrap="wrap",
                        gap="3",
                    ),
                    # Folder + tag filter bar
                    rx.hstack(
                        rx.button(
                            "All",
                            on_click=UploadState.set_folder_filter(""),
                            size="1",
                            variant=rx.cond(UploadState.folder_filter == "", "solid", "ghost"),
                            color_scheme="purple",
                        ),
                        rx.foreach(UploadState.folders, folder_filter_btn),
                        rx.box(width="1px", height="20px", background="rgba(124,58,237,0.3)"),
                        rx.icon("tag", size=14, color="#a78bfa"),
                        rx.button(
                            "All tags",
                            on_click=UploadState.set_tag_filter(""),
                            size="1",
                            variant=rx.cond(UploadState.tag_filter == "", "solid", "ghost"),
                            color_scheme="purple",
                        ),
                        rx.foreach(UploadState.tags, tag_filter_btn),
                        rx.spacer(),
                        rx.cond(
                            UploadState.folder_filter != "",
                            rx.button(
                                rx.icon("share-2", size=14),
                                "Share Folder",
                                on_click=UploadState.copy_public_folder_link,
                                size="1", variant="outline", color_scheme="blue",
                                cursor="pointer",
                                border_radius="8px",
                            ),
                            rx.box(),
                        ),
                        spacing="2",
                        flex_wrap="wrap",
                        width="100%",
                    ),
                    rx.divider(color="rgba(124,58,237,0.15)"),
                    # Bulk action bar (appears in selection mode)
                    bulk_action_bar(),
                    # Images — grid or list
                    rx.cond(
                        UploadState.filtered_images.length() > 0,
                        rx.cond(
                            UploadState.view_mode == "grid",
                            rx.box(
                                rx.foreach(UploadState.filtered_images, image_card),
                                display="flex",
                                flex_wrap="wrap",
                                gap="16px",
                                padding_top="8px",
                            ),
                            rx.vstack(
                                rx.foreach(UploadState.filtered_images, image_list_row),
                                spacing="2",
                                width="100%",
                                padding_top="8px",
                            ),
                        ),
                        rx.vstack(
                            rx.icon("image-off", size=48, color="rgba(124,58,237,0.3)"),
                            rx.text("No images yet.", size="3", color=UploadState.sub_text_color),
                            rx.text("Upload your first image above!", size="2", color="#4b5563"),
                            spacing="3",
                            align="center",
                            padding="40px 0",
                            width="100%",
                        ),
                    ),
                    spacing="4",
                    width="100%",
                ),
                padding="24px",
                background="rgba(255,255,255,0.03)",
                border="1px solid rgba(124,58,237,0.2)",
                border_radius="20px",
                width="100%",
            ),

            spacing="6",
            width="100%",
            max_width="1200px",
            padding="32px 24px",
        ),
        min_height="100vh",
        background=UploadState.bg_theme,
        display="flex",
        justify_content="center",
        on_mount=UploadState.on_load,
    )
