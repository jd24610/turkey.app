"""Import/Export page UI — shown after Google login."""

import reflex as rx
from TurkeyApp.upload_state import UploadState


# ─────────────────────────────────────────────
#  Helpers / small components
# ─────────────────────────────────────────────

def status_banner() -> rx.Component:
    return rx.cond(
        UploadState.upload_message != "",
        rx.box(
            rx.hstack(
                rx.cond(
                    UploadState.upload_status == "success",
                    rx.icon("circle-check", color="#22c55e", size=20),
                    rx.cond(
                        UploadState.upload_status == "warning",
                        rx.icon("triangle-alert", color="#f59e0b", size=20),
                        rx.icon("circle-x", color="#ef4444", size=20),
                    ),
                ),
                rx.text(UploadState.upload_message, size="2", weight="medium"),
                spacing="2",
                align="center",
            ),
            padding="12px 20px",
            border_radius="12px",
            background=rx.cond(
                UploadState.upload_status == "success",
                "rgba(34,197,94,0.12)",
                rx.cond(
                    UploadState.upload_status == "warning",
                    "rgba(245,158,11,0.12)",
                    "rgba(239,68,68,0.12)",
                ),
            ),
            border=rx.cond(
                UploadState.upload_status == "success",
                "1px solid rgba(34,197,94,0.3)",
                rx.cond(
                    UploadState.upload_status == "warning",
                    "1px solid rgba(245,158,11,0.3)",
                    "1px solid rgba(239,68,68,0.3)",
                ),
            ),
            width="100%",
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


def image_card(img: rx.Base) -> rx.Component:
    """Card for a single image — typed ImageData fields + tag badges."""
    return rx.box(
        rx.vstack(
            # Thumbnail placeholder
            rx.box(
                rx.icon("image", size=40, color="#7c3aed"),
                padding="20px",
                background="rgba(124,58,237,0.1)",
                border_radius="12px",
                display="flex",
                align_items="center",
                justify_content="center",
                width="100%",
            ),
            # File info
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
            # Tag assign dropdown
            rx.select(
                UploadState.tags.pluck("name"),
                placeholder="+ Add tag…",
                on_change=lambda tag_name: UploadState.assign_tag(
                    img.id,
                    UploadState.tags.find(lambda t: t.name == tag_name).id,
                ),
                size="1",
                width="100%",
                background="rgba(255,255,255,0.06)",
                border="1px solid rgba(124,58,237,0.3)",
                border_radius="8px",
                color="#a78bfa",
            ),
            # Assigned tag badges
            rx.cond(
                img.tag_ids.length() > 0,
                rx.box(
                    rx.foreach(
                        UploadState.filtered_tags,
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
                    display="flex",
                    flex_wrap="wrap",
                    gap="4px",
                    width="100%",
                ),
                rx.box(),
            ),
            # Delete
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
        border="1px solid rgba(124,58,237,0.2)",
        border_radius="16px",
        width="200px",
        _hover={
            "border_color": "rgba(124,58,237,0.5)",
            "background": "rgba(124,58,237,0.08)",
            "transform": "translateY(-2px)",
            "box_shadow": "0 8px 30px rgba(124,58,237,0.2)",
        },
        transition="all 0.2s ease",
        cursor="pointer",
    )


def folder_chip(folder: str) -> rx.Component:
    return rx.box(
        rx.hstack(
            rx.icon("folder", size=14, color="#a78bfa"),
            rx.text(folder, size="2", color="#e2e8f0"),
            rx.button(
                rx.icon("download", size=12),
                on_click=UploadState.export_folder(folder),
                size="1",
                variant="ghost",
                color_scheme="purple",
                title="Export folder",
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
#  Main page
# ─────────────────────────────────────────────

def import_export_page() -> rx.Component:
    return rx.box(
        duplicate_modal(),
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
                        status_banner(),
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
                # Folder + Tag filter bar
                        rx.hstack(
                            rx.button(
                                "All",
                                on_click=UploadState.set_folder_filter(""),
                                size="1",
                                variant=rx.cond(UploadState.folder_filter == "", "solid", "ghost"),
                                color_scheme="purple",
                            ),
                            rx.foreach(
                                UploadState.folders,
                                folder_filter_btn,
                            ),
                            rx.box(
                                width="1px",
                                height="20px",
                                background="rgba(124,58,237,0.3)",
                            ),
                            rx.icon("tag", size=14, color="#a78bfa"),
                            rx.button(
                                "All tags",
                                on_click=UploadState.set_tag_filter(""),
                                size="1",
                                variant=rx.cond(UploadState.tag_filter == "", "solid", "ghost"),
                                color_scheme="purple",
                            ),
                            rx.foreach(
                                UploadState.tags,
                                tag_filter_btn,
                            ),
                            spacing="2",
                            flex_wrap="wrap",
                        ),
                        justify="between",
                        align="center",
                        width="100%",
                        flex_wrap="wrap",
                        gap="3",
                    ),
                    rx.divider(color="rgba(124,58,237,0.15)"),
                    rx.cond(
                        UploadState.filtered_images.length() > 0,
                        rx.box(
                            rx.foreach(
                                UploadState.filtered_images,
                                image_card,
                            ),
                            display="flex",
                            flex_wrap="wrap",
                            gap="16px",
                            padding_top="8px",
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
