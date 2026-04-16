"""Import/Export page UI — shown after Google login."""

import reflex as rx
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
                # Coloured icon
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
                    color="white",
                    flex="1",
                ),
                rx.button(
                    rx.icon("x", size=14),
                    on_click=UploadState.dismiss_toast,
                    size="1",
                    variant="ghost",
                    color_scheme="gray",
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
            background="rgba(12,7,30,0.97)",
            backdrop_filter="blur(16px)",
            border_left=rx.cond(
                UploadState.upload_status == "success",
                "4px solid #22c55e",
                rx.cond(
                    UploadState.upload_status == "warning",
                    "4px solid #f59e0b",
                    "4px solid #ef4444",
                ),
            ),
            border_top="1px solid rgba(255,255,255,0.07)",
            border_right="1px solid rgba(255,255,255,0.07)",
            border_bottom="1px solid rgba(255,255,255,0.07)",
            box_shadow="0 8px 32px rgba(0,0,0,0.5), 0 0 0 1px rgba(124,58,237,0.1)",
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
                        rx.heading("Duplicate Images Detected", size="5", color="white"),
                        spacing="3",
                        align="center",
                    ),
                    rx.text(
                        "The following files already exist in your library:",
                        size="3",
                        color="#c4b5fd",
                    ),
                    rx.box(
                        rx.foreach(
                            UploadState.pending_duplicates,
                            lambda name: rx.hstack(
                                rx.icon("image", size=14, color="#f59e0b"),
                                rx.text(name, size="2", color="#fde68a"),
                                spacing="2",
                                align="center",
                            ),
                        ),
                        padding="12px 16px",
                        background="rgba(245,158,11,0.1)",
                        border="1px solid rgba(245,158,11,0.25)",
                        border_radius="10px",
                        width="100%",
                        max_height="200px",
                        overflow_y="auto",
                    ),
                    rx.text(
                        "Do you want to overwrite these files?",
                        size="3",
                        color="#e2e8f0",
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
                background="rgba(15,10,40,0.98)",
                border="1px solid rgba(124,58,237,0.4)",
                border_radius="20px",
                width="480px",
                box_shadow="0 25px 60px rgba(0,0,0,0.7)",
            ),
            position="fixed",
            top="0",
            left="0",
            width="100vw",
            height="100vh",
            background="rgba(0,0,0,0.6)",
            backdrop_filter="blur(6px)",
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
        rx.box(
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
                        src=rx.get_upload_url(UploadState.preview_filename),
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
                                    rx.icon("image", size=14, color="#a78bfa"),
                                    rx.text(
                                        UploadState.lightbox_name,
                                        size="2", weight="medium", color="white",
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
                                    rx.icon("hard-drive", size=13, color="#6b7280"),
                                    rx.text(UploadState.lightbox_size, size="1", color="#9ca3af"),
                                    spacing="1", align="center",
                                ),
                                rx.box(width="1px", height="16px", background="rgba(255,255,255,0.12)"),
                                # date
                                rx.hstack(
                                    rx.icon("calendar", size=13, color="#6b7280"),
                                    rx.text(UploadState.lightbox_date, size="1", color="#9ca3af"),
                                    spacing="1", align="center",
                                ),
                                rx.box(width="1px", height="16px", background="rgba(255,255,255,0.12)"),
                                # folder
                                rx.hstack(
                                    rx.icon("folder", size=13, color="#6b7280"),
                                    rx.text(UploadState.lightbox_folder, size="1", color="#9ca3af"),
                                    spacing="1", align="center",
                                ),
                                rx.box(width="1px", height="16px", background="rgba(255,255,255,0.12)"),
                                # tags
                                rx.hstack(
                                    rx.icon("tag", size=13, color="#6b7280"),
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
                                        rx.icon("lock", size=14, color="#6b7280"),
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
                                            "#6b7280",
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
                                border_top="1px solid rgba(255,255,255,0.06)",
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
                                        background="rgba(255,255,255,0.08)",
                                        border="1px solid rgba(168,85,247,0.5)",
                                        border_radius="8px",
                                        color="white",
                                        _placeholder={"color": "#6b7280"},
                                        _focus={"outline": "none", "border_color": "#a855f7"},
                                        on_key_down=rx.cond(
                                            UploadState.lightbox_caption_draft != "",
                                            UploadState.save_lightbox_caption,
                                            UploadState.cancel_edit_caption,
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
                                    rx.icon("message-circle", size=13, color="#6b7280"),
                                    rx.text(
                                        rx.cond(
                                            UploadState.lightbox_caption != "",
                                            UploadState.lightbox_caption,
                                            "Add a caption…",
                                        ),
                                        size="1",
                                        color=rx.cond(
                                            UploadState.lightbox_caption != "",
                                            "#d1d5db",
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
                                        color="#6b7280",
                                        cursor="pointer",
                                        on_click=UploadState.start_edit_caption,
                                        _hover={"color": "#a78bfa"},
                                    ),
                                    spacing="2", align="center", width="100%",
                                ),
                            ),
                            spacing="2",
                            width="100%",
                        ),
                        padding="12px 18px",
                        background="rgba(8,4,22,0.92)",
                        border_radius="10px",
                        border="1px solid rgba(124,58,237,0.2)",
                        backdrop_filter="blur(12px)",
                        width="100%",
                        max_width="70vw",
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
                    src=rx.get_upload_url(img.filename),
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
                # 🌐 Public badge (top-left)
                rx.cond(
                    img.is_public,
                    rx.box(
                        rx.icon("globe", size=12, color="white"),
                        position="absolute",
                        top="8px", left="8px",
                        background="rgba(34,197,94,0.85)",
                        border_radius="999px",
                        padding="3px 7px",
                        display="flex",
                        align_items="center",
                        justify_content="center",
                        backdrop_filter="blur(4px)",
                        border="1px solid rgba(255,255,255,0.2)",
                    ),
                    rx.box(),
                ),
                width="100%",
                overflow="hidden",
                border_radius="10px",
                cursor="pointer",
                on_click=UploadState.on_image_click(img.id, img.filename),
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
                    color="white",
                    white_space="nowrap",
                    overflow="hidden",
                    text_overflow="ellipsis",
                    max_width="160px",
                ),
                rx.cond(
                    img.folder_name != "",
                    rx.hstack(
                        rx.icon("folder", size=12, color="#a78bfa"),
                        rx.text(img.folder_name, size="1", color="#a78bfa"),
                        spacing="1",
                        align="center",
                    ),
                    rx.box(),
                ),
                rx.hstack(
                    rx.cond(
                        img.is_large,
                        rx.text(img.size_mb, " MB", size="1", color="#6b7280"),
                        rx.text(img.size_kb, " KB", size="1", color="#6b7280"),
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
                background="rgba(255,255,255,0.06)",
                border="1px solid rgba(124,58,237,0.3)",
                border_radius="8px",
                color="#a78bfa",
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
                        rx.text(t.name, size="1", color="white"),
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
                        background="rgba(124,58,237,0.18)",
                        border_radius="999px",
                        border="1px solid rgba(124,58,237,0.3)",
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
                background="rgba(255,255,255,0.06)",
                border="1px solid rgba(124,58,237,0.3)",
                border_radius="8px",
                color="#a78bfa",
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
        background="rgba(255,255,255,0.04)",
        border=rx.cond(
            UploadState.selected_image_ids.contains(img.id),
            "2px solid #a855f7",
            "1px solid rgba(124,58,237,0.2)",
        ),
        border_radius="16px",
        width=UploadState.card_width,
        _hover={
            "border_color": "rgba(124,58,237,0.5)",
            "background": "rgba(124,58,237,0.08)",
            "transform": "translateY(-2px)",
            "box_shadow": "0 8px 30px rgba(124,58,237,0.2)",
        },
        transition="all 0.2s ease",
    )


def image_list_row(img: rx.Base) -> rx.Component:
    """Compact list-view row for a single image."""
    return rx.hstack(
        rx.image(
            src=rx.get_upload_url(img.filename),
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
            color="white",
            flex="1",
            overflow="hidden",
            text_overflow="ellipsis",
            white_space="nowrap",
            min_width="0",
        ),
        rx.cond(
            img.folder_name != "",
            rx.hstack(
                rx.icon("folder", size=12, color="#a78bfa"),
                rx.text(img.folder_name, size="1", color="#a78bfa", white_space="nowrap"),
                spacing="1",
                align="center",
            ),
            rx.text("—", size="1", color="#4b5563"),
        ),
        rx.cond(
            img.is_large,
            rx.text(img.size_mb, " MB", size="1", color="#6b7280", white_space="nowrap"),
            rx.text(img.size_kb, " KB", size="1", color="#6b7280", white_space="nowrap"),
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
        padding="10px 16px",
        background="rgba(255,255,255,0.03)",
        border="1px solid rgba(124,58,237,0.12)",
        border_radius="10px",
        _hover={"background": "rgba(124,58,237,0.07)", "border_color": "rgba(124,58,237,0.3)"},
        transition="all 0.15s ease",
    )

def folder_chip(folder: str) -> rx.Component:
    return rx.box(
        rx.hstack(
            rx.icon("folder", size=14, color="#a78bfa"),
            rx.text(folder, size="2", color="#e2e8f0"),
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
                color_scheme="purple",
                title="Export folder as ZIP",
            ),
            rx.button(
                rx.icon("trash-2", size=12),
                on_click=UploadState.delete_folder(folder),
                size="1",
                variant="ghost",
                color_scheme="red",
                title="Delete folder",
            ),
            spacing="2",
            align="center",
        ),
        padding="8px 14px",
        background="rgba(124,58,237,0.12)",
        border="1px solid rgba(124,58,237,0.25)",
        border_radius="999px",
        cursor="pointer",
        on_click=UploadState.set_folder_filter(folder),
        _hover={"background": "rgba(124,58,237,0.22)"},
        transition="all 0.15s ease",
    )


def folder_filter_btn(folder: str) -> rx.Component:
    return rx.button(
        folder,
        on_click=UploadState.set_folder_filter(folder),
        size="1",
        variant=rx.cond(UploadState.folder_filter == folder, "solid", "ghost"),
        color_scheme="purple",
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
        rx.text(tag.name, size="2", color="white", flex="1"),
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
        background="rgba(255,255,255,0.03)",
        border="1px solid rgba(124,58,237,0.15)",
    )


def tag_management_panel() -> rx.Component:
    """Tasks A/B/C/D/F/G: Tag Management panel."""
    return rx.box(
        rx.vstack(
            rx.hstack(
                rx.icon("tag", size=18, color="#a78bfa"),
                rx.text("Tags", size="3", weight="bold", color="white"),
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
                    background="rgba(255,255,255,0.06)",
                    border="1px solid rgba(124,58,237,0.3)",
                    border_radius="10px",
                    color="white",
                    flex="1",
                ),
                rx.input(
                    type="color",
                    value=UploadState.new_tag_color,
                    on_change=UploadState.set_new_tag_color,
                    width="40px",
                    height="36px",
                    padding="2px",
                    border="1px solid rgba(124,58,237,0.3)",
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
                background="rgba(255,255,255,0.04)",
                border="1px solid rgba(124,58,237,0.2)",
                border_radius="8px",
                color="white",
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
                rx.text("No tags yet.", size="2", color="#6b7280", text_align="center"),
            ),
            spacing="3",
            width="100%",
        ),
        padding="24px",
        background="rgba(255,255,255,0.03)",
        border="1px solid rgba(124,58,237,0.2)",
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
                    rx.box(
                        rx.icon("cloud_upload", size=48, color="#7c3aed"),
                        padding="20px",
                        background="rgba(124,58,237,0.1)",
                        border_radius="50%",
                    ),
                    rx.text("Drag & drop images here", size="4", weight="bold", color="white"),
                    rx.text("or click to browse", size="2", color="#6b7280"),
                    rx.hstack(
                        rx.badge("JPG", color_scheme="purple"),
                        rx.badge("PNG", color_scheme="purple"),
                        rx.badge("Max 10 MB", color_scheme="gray"),
                        spacing="2",
                    ),
                    spacing="3",
                    align="center",
                ),
            ),
            justify="center",
            align="center",
            min_height="200px",
            width="100%",
        ),
        id="image-upload",
        multiple=True,
        accept={
            "image/jpeg": [".jpg", ".jpeg"],
            "image/png": [".png"],
        },
        on_drop=UploadState.handle_upload(rx.upload_files(upload_id="image-upload")),
        border="2px dashed rgba(124,58,237,0.4)",
        border_radius="20px",
        padding="0",
        background="rgba(124,58,237,0.04)",
        width="100%",
        _hover={
            "border_color": "rgba(168,85,247,0.7)",
            "background": "rgba(124,58,237,0.1)",
        },
        transition="all 0.2s ease",
    )


# ─────────────────────────────────────────────
#  Extra components
# ─────────────────────────────────────────────

# Theme / accent preset data
_THEMES = [
    ("Deep Space", "#1a0a3e", "#3d1a7a", "radial-gradient(ellipse at 20% 0%, #1a0a3e 0%, #080514 60%, #030208 100%)"),
    ("Midnight",   "#0a1438", "#1a2a5e", "radial-gradient(ellipse at 20% 0%, #0a1438 0%, #050a19 60%, #020408 100%)"),
    ("Void",       "#111111", "#222222", "linear-gradient(160deg, #141414 0%, #060606 100%)"),
    ("Slate",      "#1a1a2e", "#2a2a4e", "radial-gradient(ellipse at 20% 0%, #1a1a2e 0%, #0f0f18 60%, #070714 100%)"),
    ("Forest",     "#0a2420", "#1a4440", "radial-gradient(ellipse at 20% 0%, #0a2420 0%, #051413 60%, #020808 100%)"),
]
_ACCENTS = [
    ("Violet", "#7c3aed", "#a855f7"),
    ("Cobalt", "#1d4ed8", "#60a5fa"),
    ("Teal",   "#0d9488", "#2dd4bf"),
    ("Rose",   "#be185d", "#f472b6"),
    ("Amber",  "#b45309", "#fbbf24"),
]


def _theme_swatch(name: str, dark: str, mid: str, gradient: str) -> rx.Component:
    return rx.tooltip(
        rx.box(
            width="38px",
            height="38px",
            border_radius="10px",
            background=f"linear-gradient(135deg, {mid} 0%, {dark} 100%)",
            border=rx.cond(
                UploadState.bg_theme == gradient,
                "2px solid white",
                "2px solid rgba(255,255,255,0.1)",
            ),
            cursor="pointer",
            on_click=UploadState.set_bg_theme(gradient),
            _hover={"transform": "scale(1.12)", "border_color": "rgba(255,255,255,0.6)"},
            transition="all 0.15s ease",
            box_shadow="0 2px 8px rgba(0,0,0,0.4)",
        ),
        content=name,
    )


def _accent_swatch(name: str, main: str, light: str) -> rx.Component:
    return rx.tooltip(
        rx.box(
            width="34px",
            height="34px",
            border_radius="50%",
            background=f"linear-gradient(135deg, {main}, {light})",
            border=rx.cond(
                UploadState.accent_hex == main,
                "2.5px solid white",
                "2.5px solid rgba(255,255,255,0.1)",
            ),
            cursor="pointer",
            on_click=UploadState.set_accent(main, light),
            _hover={"transform": "scale(1.15)"},
            transition="all 0.15s ease",
            box_shadow=f"0 2px 10px {main}66",
        ),
        content=name,
    )


def _pref_row(label: str, control: rx.Component) -> rx.Component:
    return rx.hstack(
        rx.text(label, size="2", color="#c4b5fd", flex="1"),
        control,
        justify="between",
        align="center",
        width="100%",
        padding="10px 0",
        border_bottom="1px solid rgba(124,58,237,0.08)",
    )


def settings_panel() -> rx.Component:
    """Pinterest-style slide-in preferences drawer."""
    return rx.cond(
        UploadState.settings_open,
        rx.box(
            # ─ Backdrop ─────────────────────
            rx.box(
                position="fixed", top="0", left="0",
                width="100vw", height="100vh",
                background="rgba(0,0,0,0.45)",
                backdrop_filter="blur(3px)",
                z_index="199",
                on_click=UploadState.close_settings,
            ),
            # ─ Panel ───────────────────────
            rx.box(
                rx.vstack(
                    # Header
                    rx.hstack(
                        rx.hstack(
                            rx.icon("settings", size=20, color="#a78bfa"),
                            rx.text("Preferences", size="5", weight="bold", color="white"),
                            spacing="3", align="center",
                        ),
                        rx.button(
                            rx.icon("x", size=18),
                            on_click=UploadState.close_settings,
                            size="1", variant="ghost", color_scheme="purple",
                        ),
                        justify="between", width="100%", align="center",
                    ),
                    rx.divider(color="rgba(124,58,237,0.25)"),

                    # ――― Appearance Section ―――
                    rx.vstack(
                        rx.text("APPEARANCE", size="1", weight="bold", color="#4b5563", letter_spacing="1.5px"),
                        rx.vstack(
                            rx.text("Background Theme", size="2", color="#c4b5fd"),
                            rx.hstack(
                                *[_theme_swatch(n, d, m, g) for n, d, m, g in _THEMES],
                                spacing="2",
                            ),
                            spacing="2", align="start", width="100%",
                            padding="10px 0",
                            border_bottom="1px solid rgba(124,58,237,0.08)",
                        ),
                        rx.vstack(
                            rx.text("Accent Color", size="2", color="#c4b5fd"),
                            rx.hstack(
                                *[_accent_swatch(n, m, l) for n, m, l in _ACCENTS],
                                spacing="3",
                            ),
                            spacing="2", align="start", width="100%",
                            padding="10px 0",
                        ),
                        spacing="2", align="start", width="100%",
                    ),

                    rx.divider(color="rgba(124,58,237,0.12)"),

                    # ――― Gallery Section ―――
                    rx.vstack(
                        rx.text("GALLERY", size="1", weight="bold", color="#4b5563", letter_spacing="1.5px"),
                        _pref_row(
                            "Stats Bar",
                            rx.switch(
                                checked=UploadState.show_stats_bar,
                                on_change=UploadState.toggle_stats_bar,
                                color_scheme="purple",
                            ),
                        ),
                        _pref_row(
                            "Default Sort",
                            rx.select(
                                ["Newest first", "Oldest first", "A → Z", "Z → A", "Largest first"],
                                value=UploadState.sort_by,
                                on_change=UploadState.set_sort_by,
                                size="1",
                                background="rgba(255,255,255,0.06)",
                                border="1px solid rgba(124,58,237,0.3)",
                                color="white",
                                border_radius="8px",
                                width="140px",
                            ),
                        ),
                        _pref_row(
                            "Card Size",
                            rx.hstack(
                                rx.button(
                                    "S",
                                    on_click=UploadState.set_card_size("small"),
                                    size="1",
                                    variant=rx.cond(UploadState.card_size == "small", "solid", "ghost"),
                                    color_scheme="purple",
                                ),
                                rx.button(
                                    "M",
                                    on_click=UploadState.set_card_size("medium"),
                                    size="1",
                                    variant=rx.cond(UploadState.card_size == "medium", "solid", "ghost"),
                                    color_scheme="purple",
                                ),
                                rx.button(
                                    "L",
                                    on_click=UploadState.set_card_size("large"),
                                    size="1",
                                    variant=rx.cond(UploadState.card_size == "large", "solid", "ghost"),
                                    color_scheme="purple",
                                ),
                                spacing="1",
                            ),
                        ),
                        _pref_row(
                            "Default View",
                            rx.hstack(
                                rx.button(
                                    rx.icon("layout-grid", size=14),
                                    on_click=UploadState.set_view_mode("grid"),
                                    size="1",
                                    variant=rx.cond(UploadState.view_mode == "grid", "solid", "ghost"),
                                    color_scheme="purple",
                                    title="Grid view",
                                ),
                                rx.button(
                                    rx.icon("list", size=14),
                                    on_click=UploadState.set_view_mode("list"),
                                    size="1",
                                    variant=rx.cond(UploadState.view_mode == "list", "solid", "ghost"),
                                    color_scheme="purple",
                                    title="List view",
                                ),
                                spacing="1",
                            ),
                        ),
                        spacing="1", align="start", width="100%",
                    ),

                    rx.divider(color="rgba(124,58,237,0.12)"),

                    # ――― About Section ―――
                    rx.vstack(
                        rx.text("ABOUT", size="1", weight="bold", color="#4b5563", letter_spacing="1.5px"),
                        rx.hstack(
                            rx.image(
                                src="/turkey_icon.png",
                                width="32px", height="32px",
                                border_radius="8px",
                                object_fit="cover",
                            ),
                            rx.vstack(
                                rx.hstack(
                                    rx.text("turkey", size="3", weight="bold", color="white"),
                                    rx.text(".app", size="3", weight="bold", color="#a855f7"),
                                    spacing="0",
                                ),
                                rx.text("v0.1 · Media Library", size="1", color="#4b5563"),
                                spacing="0", align="start",
                            ),
                            spacing="3", align="center",
                        ),
                        rx.text(
                            "Built with Reflex · SQLite · Google OAuth",
                            size="1", color="#374151",
                        ),
                        spacing="3", align="start", width="100%",
                        padding_top="4px",
                    ),

                    spacing="5",
                    align="start",
                    width="100%",
                ),
                # Panel styles
                padding="24px",
                background="rgba(8,4,22,0.98)",
                border_left="1px solid rgba(124,58,237,0.25)",
                width="340px",
                height="100vh",
                position="fixed",
                top="0",
                right="0",
                overflow_y="auto",
                z_index="200",
                box_shadow="-12px 0 50px rgba(0,0,0,0.6)",
                backdrop_filter="blur(20px)",
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
                    rx.icon(icon, size=18, color="#a78bfa"),
                    rx.text(value, size="5", weight="bold", color="white"),
                    spacing="2",
                    align="center",
                ),
                rx.text(label, size="1", color="#6b7280"),
                spacing="1",
                align="start",
            ),
            padding="16px 20px",
            background="rgba(255,255,255,0.03)",
            border="1px solid rgba(124,58,237,0.15)",
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
                        rx.icon("pencil", size=22, color="#a78bfa"),
                        rx.heading("Rename Folder", size="5", color="white"),
                        spacing="3",
                        align="center",
                    ),
                    rx.text(
                        'Renaming: "', UploadState.renaming_folder, '"',
                        size="2", color="#c4b5fd",
                    ),
                    rx.input(
                        value=UploadState.rename_folder_input,
                        on_change=UploadState.set_rename_folder_input,
                        size="3",
                        background="rgba(255,255,255,0.08)",
                        border="1px solid rgba(124,58,237,0.5)",
                        border_radius="10px",
                        color="white",
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
                            background="linear-gradient(135deg, #7c3aed, #a855f7)",
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
                background="rgba(15,10,40,0.98)",
                border="1px solid rgba(124,58,237,0.4)",
                border_radius="20px",
                width="400px",
                box_shadow="0 25px 60px rgba(0,0,0,0.7)",
            ),
            position="fixed",
            top="0", left="0",
            width="100vw", height="100vh",
            background="rgba(0,0,0,0.6)",
            backdrop_filter="blur(6px)",
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
                    rx.icon("square-check", size=18, color="#a855f7"),
                    rx.text(UploadState.bulk_count, " selected", size="2", weight="medium", color="white"),
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
                        background="rgba(255,255,255,0.08)",
                        border="1px solid rgba(124,58,237,0.4)",
                        border_radius="8px",
                        color="white",
                    ),
                    rx.button(
                        rx.icon("trash-2", size=14),
                        "Delete Selected",
                        on_click=UploadState.bulk_delete,
                        size="2",
                        background="rgba(239,68,68,0.12)",
                        border="1px solid rgba(239,68,68,0.35)",
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
            background="rgba(124,58,237,0.12)",
            border="1px solid rgba(124,58,237,0.35)",
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
                        rx.heading("Media Library", size="6", color="white"),
                        rx.text("Import · Manage · Export", size="2", color="#a78bfa"),
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

            rx.divider(color="rgba(124,58,237,0.2)"),

            # ── Live stats (hideable) ──
            rx.cond(UploadState.show_stats_bar, stats_bar(), rx.box()),

                # Upload + Folder + Tags Row
            rx.hstack(
                # Upload zone
                rx.box(
                    rx.vstack(
                        rx.hstack(
                            rx.icon("upload", size=18, color="#a78bfa"),
                            rx.text("Import Images", size="3", weight="bold", color="white"),
                            spacing="2",
                            align="center",
                        ),
                        upload_zone(),
                        spacing="4",
                        width="100%",
                    ),
                    padding="24px",
                    background="rgba(255,255,255,0.03)",
                    border="1px solid rgba(124,58,237,0.2)",
                    border_radius="20px",
                    flex="1",
                    min_width="320px",
                ),

                # Folder management
                rx.box(
                    rx.vstack(
                        rx.hstack(
                            rx.icon("folder-plus", size=18, color="#a78bfa"),
                            rx.text("Folders", size="3", weight="bold", color="white"),
                            spacing="2",
                            align="center",
                        ),
                        rx.hstack(
                            rx.input(
                                placeholder="New folder name…",
                                value=UploadState.new_folder_name,
                                on_change=UploadState.set_new_folder_name,
                                size="2",
                                background="rgba(255,255,255,0.06)",
                                border="1px solid rgba(124,58,237,0.3)",
                                border_radius="10px",
                                color="white",
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
                                rx.text("No folders yet. Create one above!", size="2", color="#6b7280"),
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
                        spacing="2",
                        flex_wrap="wrap",
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
                            rx.text("No images yet.", size="3", color="#6b7280"),
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
        background="radial-gradient(ellipse at top, #130a2e 0%, #0a0515 60%, #050208 100%)",
        display="flex",
        justify_content="center",
        on_mount=UploadState.on_load,
    )
