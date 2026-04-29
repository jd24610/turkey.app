"""State management for Import/Export functionality."""
from typing import Optional

import reflex as rx
import datetime
import json
import os
import io
import base64
from pydantic import BaseModel
from TurkeyApp.models import ImageRecord, Folder, Tag, ImageTag
from TurkeyApp.portfolio_utils import generate_portfolio_html
from TurkeyApp.image_support import get_image_data_uri
from TurkeyApp.ai_utils import get_image_embeddings, upsert_to_pinecone

# Constants
MAX_FILE_SIZE_BYTES = 10 * 1024 * 1024        # 10 MB hard limit
COMPRESS_THRESHOLD_BYTES = 10 * 1024 * 1024   # start compressing at 10 MB
COMPRESS_MAX_BYTES = 20 * 1024 * 1024         # up to 20 MB gets auto-compressed
STORAGE_QUOTA_BYTES = 1 * 1024 * 1024 * 1024  # 1 GB quota
UPLOAD_DIR = os.path.join("assets", "uploaded_files")
os.makedirs(UPLOAD_DIR, exist_ok=True)


class TagData(BaseModel):
    """Typed tag record for the UI."""
    id: int = 0
    name: str = ""
    color: str = "#7c3aed"


class ImageData(BaseModel):
    """Typed image record for the UI."""
    id: int = 0
    owner_email: str = ""

    filename: str = ""
    original_filename: str = ""
    folder_name: str = ""
    mime_type: str = "image/jpeg"
    size_bytes: int = 0
    size_mb: float = 0.0
    size_kb: float = 0.0
    is_large: bool = False       # size_bytes > 1MB
    was_compressed: bool = False
    created_at: Optional[str] = ""
    tag_ids: list[int] = []
    is_public: bool = False      # shared on public profile & feed
    caption: Optional[str] = ""  # optional public caption
    exif_info: Optional[str] = None  # JSON-stringified EXIF metadata

    @property
    def img_url(self) -> str:
        """Construct the full URL for the image."""
        backend = os.getenv("API_URL", "http://localhost:8000")
        return f"{backend}/uploaded_files/{self.filename}"


class UploadState(rx.State):
    """State for the Import/Export page."""

    # ---- Auth info ----
    user_email: str = ""
    user_name: str = ""

    # ---- Upload feedback / toast ----
    upload_status: str = ""   # "success" | "warning" | "error"
    upload_message: str = ""
    is_uploading: bool = False
    toast_visible: bool = False

    # ---- Data ----
    images: list[ImageData] = []
    folders: list[str] = []
    public_folders: list[str] = []  # names of folders that are public
    selected_folder: str = ""
    new_folder_name: str = ""
    folder_filter: str = ""

    # ---- Tags ----
    tags: list[TagData] = []
    new_tag_name: str = ""
    new_tag_color: str = "#7c3aed"
    tag_filter: str = ""        # filter by tag_id string, "" = all
    tag_search: str = ""        # search tag names

    used_storage_bytes: int = 0

    # ---- Export ----
    export_status: str = ""

    # ---- Duplicate handling ----
    pending_duplicates: list[str] = []
    show_duplicate_modal: bool = False
    pending_upload_data: list[dict] = []

    # ---- Image preview (lightbox) ----
    preview_filename: str = ""
    show_preview: bool = False
    preview_index: int = -1
    lightbox_editing_caption: bool = False
    lightbox_caption_draft: str = ""

    # ---- Gallery controls ----
    search_query: str = ""
    sort_by: str = "Newest first"
    view_mode: str = "grid"  # "grid" | "list"

    # ---- Rename folder ----
    renaming_folder: str = ""
    rename_folder_input: str = ""

    # ---- Bulk selection ----
    selected_image_ids: list[int] = []
    last_selected_id: int = 0
    selection_mode: bool = False
    show_exif_panel: bool = False

    # ---- User preferences (cookie-persisted) ----
    settings_open: bool = False
    bg_theme: str = rx.Cookie(
        "#ffffff",
        name="pref_bg_theme",
        max_age=31536000,
    )
    accent_hex: str = rx.Cookie("#7c3aed", name="pref_accent_hex", max_age=31536000)
    accent_light: str = rx.Cookie("#a855f7", name="pref_accent_light", max_age=31536000)
    card_size: str = rx.Cookie("medium", name="pref_card_size", max_age=31536000)
    show_stats_bar: bool = True

    # ── Theme Vars ────────────────────────────
    @rx.var
    def is_dark_mode(self) -> bool:
        return self.bg_theme != "#ffffff"

    @rx.var
    def text_color(self) -> str:
        return "#ffffff" if self.bg_theme != "#ffffff" else "#111827"

    @rx.var
    def sub_text_color(self) -> str:
        return "#9ca3af" if self.bg_theme != "#ffffff" else "#6b7280"

    @rx.var
    def bg_card(self) -> str:
        return "#1f2937" if self.bg_theme != "#ffffff" else "#ffffff"

    @rx.var
    def border_color(self) -> str:
        return "#374151" if self.bg_theme != "#ffffff" else "#f1f1f1"

    @rx.var
    def input_bg(self) -> str:
        return "#111827" if self.bg_theme != "#ffffff" else "#f1f1f1"

    @rx.var
    def nav_bg(self) -> str:
        return "#111827" if self.bg_theme != "#ffffff" else "#ffffff"

    def toggle_dark_mode(self):
        if self.is_dark_mode:
            self.bg_theme = "#ffffff"
        else:
            self.bg_theme = "#0a0a0a" # Pure dark for brutalist feel


    # ── Computed ──────────────────────────────
    @rx.var
    def used_storage_mb(self) -> float:
        return round(self.used_storage_bytes / (1024 * 1024), 2)

    @rx.var
    def quota_mb(self) -> int:
        return STORAGE_QUOTA_BYTES // (1024 * 1024)

    @rx.var
    def storage_percent(self) -> float:
        if STORAGE_QUOTA_BYTES == 0:
            return 0.0
        return round(min((self.used_storage_bytes / STORAGE_QUOTA_BYTES) * 100, 100), 1)

    @rx.var
    def filtered_images(self) -> list[ImageData]:
        imgs = self.images
        if self.folder_filter:
            imgs = [img for img in imgs if img.folder_name == self.folder_filter]
        if self.tag_filter:
            try:
                tid = int(self.tag_filter)
                imgs = [img for img in imgs if tid in img.tag_ids]
            except ValueError:
                pass
        if self.search_query:
            q = self.search_query.lower()
            imgs = [img for img in imgs if q in img.original_filename.lower()]
        if self.sort_by == "Newest first":
            imgs = sorted(imgs, key=lambda x: x.created_at, reverse=True)
        elif self.sort_by == "Oldest first":
            imgs = sorted(imgs, key=lambda x: x.created_at)
        elif self.sort_by == "A → Z":
            imgs = sorted(imgs, key=lambda x: x.original_filename.lower())
        elif self.sort_by == "Z → A":
            imgs = sorted(imgs, key=lambda x: x.original_filename.lower(), reverse=True)
        elif self.sort_by == "Largest first":
            imgs = sorted(imgs, key=lambda x: x.size_bytes, reverse=True)
        return imgs

    @rx.var
    def image_count(self) -> int:
        return len(self.filtered_images)

    @rx.var
    def filtered_tags(self) -> list[TagData]:
        """Tags filtered by search query."""
        if not self.tag_search:
            return self.tags
        q = self.tag_search.lower()
        return [t for t in self.tags if q in t.name.lower()]

    @rx.var
    def tag_names(self) -> list[str]:
        """Plain list of tag names for use in rx.select."""
        return [t.name for t in self.tags]

    @rx.var
    def tag_name_to_id(self) -> dict[str, int]:
        """Map tag name → tag id for assign_tag_by_name lookup."""
        return {t.name: t.id for t in self.tags}

    @rx.var
    def folders_with_none(self) -> list[str]:
        """Folder list with '(No folder)' sentinel for the move-to dropdown."""
        return ["(No folder)"] + self.folders

    @rx.var
    def folder_image_counts(self) -> dict[str, int]:
        """Images-per-folder counts for badge display."""
        counts: dict[str, int] = {f: 0 for f in self.folders}
        for img in self.images:
            if img.folder_name and img.folder_name in counts:
                counts[img.folder_name] = counts[img.folder_name] + 1
        return counts

    @rx.var
    def total_images(self) -> int:
        """Total images across all filters."""
        return len(self.images)

    @rx.var
    def folder_count(self) -> int:
        return len(self.folders)

    @rx.var
    def tag_count(self) -> int:
        return len(self.tags)

    @rx.var
    def bulk_count(self) -> int:
        return len(self.selected_image_ids)

    # ── Lightbox computed vars ─────────────────
    @rx.var
    def preview_has_prev(self) -> bool:
        return self.preview_index > 0

    @rx.var
    def preview_has_next(self) -> bool:
        return self.preview_index < len(self.filtered_images) - 1

    @rx.var
    def lightbox_name(self) -> str:
        imgs = self.filtered_images
        if 0 <= self.preview_index < len(imgs):
            return imgs[self.preview_index].original_filename
        return self.preview_filename

    @rx.var
    def lightbox_size(self) -> str:
        imgs = self.filtered_images
        if 0 <= self.preview_index < len(imgs):
            img = imgs[self.preview_index]
            if img.size_mb >= 1:
                return f"{img.size_mb} MB"
            return f"{int(img.size_kb)} KB"
        return ""

    @rx.var
    def lightbox_date(self) -> str:
        imgs = self.filtered_images
        if 0 <= self.preview_index < len(imgs):
            raw = imgs[self.preview_index].created_at
            # raw is ISO-like string: take first 10 chars (YYYY-MM-DD)
            return raw[:10] if raw else ""
        return ""

    @rx.var
    def lightbox_exif(self) -> dict:
        imgs = self.filtered_images
        if 0 <= self.preview_index < len(imgs):
            info = imgs[self.preview_index].exif_info
            if info:
                try: 
                    import json
                    return json.loads(info)
                except: pass
        return {}

    @rx.var
    def lightbox_folder(self) -> str:
        imgs = self.filtered_images
        if 0 <= self.preview_index < len(imgs):
            return imgs[self.preview_index].folder_name or "—"
        return "—"

    @rx.var
    def lightbox_tag_count(self) -> int:
        imgs = self.filtered_images
        if 0 <= self.preview_index < len(imgs):
            return len(imgs[self.preview_index].tag_ids)
        return 0

    @rx.var
    def lightbox_counter(self) -> str:
        """e.g. '3 / 12'"""
        total = len(self.filtered_images)
        if total == 0:
            return ""
        idx = self.preview_index + 1
        return f"{idx} / {total}"

    @rx.var
    def lightbox_is_public(self) -> bool:
        imgs = self.filtered_images
        if 0 <= self.preview_index < len(imgs):
            return imgs[self.preview_index].is_public
        return False

    @rx.var
    def lightbox_caption(self) -> str:
        imgs = self.filtered_images
        if 0 <= self.preview_index < len(imgs):
            return imgs[self.preview_index].caption or ""
        return ""

    # ── Lifecycle ─────────────────────────────
    def on_load(self):
        self._refresh_images()
        self._refresh_folders()
        self._refresh_tags()
        self._recalc_storage()

    def set_user_email(self, email: str):
        self.user_email = email

    def set_user_name(self, name: str):
        self.user_name = name

    # ── Preferences ───────────────────────────
    def toggle_settings(self):
        self.settings_open = not self.settings_open

    def close_settings(self):
        self.settings_open = False

    def set_accent(self, main: str, light: str):
        self.accent_hex = main
        self.accent_light = light

    def toggle_stats_bar(self, checked: bool):
        self.show_stats_bar = checked

    def toggle_exif_panel(self):
        self.show_exif_panel = not self.show_exif_panel

    def set_card_size(self, size: str):
        self.card_size = size

    def set_view_mode(self, mode: str):
        self.view_mode = mode

    def set_selected_folder(self, folder: str):
        self.selected_folder = folder

    def set_new_folder_name(self, name: str):
        self.new_folder_name = name

    def set_folder_filter(self, folder: str):
        self.folder_filter = folder

    def set_tag_filter(self, tag_id: str):
        self.tag_filter = tag_id

    def set_tag_search(self, q: str):
        self.tag_search = q

    def set_new_tag_name(self, name: str):
        self.new_tag_name = name

    def set_new_tag_color(self, color: str):
        self.new_tag_color = color

    def assign_tag_by_name(self, image_id: int, tag_name: str):
        """Assign a tag to an image using its name (for use with rx.select)."""
        tag_id = self.tag_name_to_id.get(tag_name)
        if tag_id is not None:
            self.assign_tag(image_id, tag_id)

    def open_preview(self, filename: str):
        """Open the lightbox preview for a given image filename."""
        self.preview_filename = filename
        self.show_preview = True

    def close_preview(self):
        """Close the lightbox preview."""
        self.show_preview = False
        self.preview_filename = ""
        self.preview_index = -1

    def prev_image(self):
        """Navigate to the previous image in lightbox."""
        if self.preview_index > 0:
            self.preview_index -= 1
            self.preview_filename = self.filtered_images[self.preview_index].filename

    def next_image(self):
        """Navigate to the next image in lightbox."""
        if self.preview_index < len(self.filtered_images) - 1:
            self.preview_index += 1
            self.preview_filename = self.filtered_images[self.preview_index].filename

    def toggle_image_public(self, image_id: int):
        """Flip is_public for a single image."""
        with rx.session() as session:
            rec = session.get(ImageRecord, image_id)
            if rec:
                rec.is_public = not rec.is_public
                session.add(rec)
                session.commit()
        self._refresh_images()

    def set_image_caption(self, image_id: int, caption: str):
        """Save a caption for a single image."""
        with rx.session() as session:
            rec = session.get(ImageRecord, image_id)
            if rec:
                rec.caption = caption.strip()
                session.add(rec)
                session.commit()
        self._refresh_images()

    def toggle_lightbox_public(self):
        """Toggle is_public for the image currently open in the lightbox."""
        imgs = self.filtered_images
        if 0 <= self.preview_index < len(imgs):
            self.toggle_image_public(imgs[self.preview_index].id)

    def start_edit_caption(self):
        """Enter inline caption edit mode for the current lightbox image."""
        imgs = self.filtered_images
        if 0 <= self.preview_index < len(imgs):
            self.lightbox_caption_draft = imgs[self.preview_index].caption
            self.lightbox_editing_caption = True

    def set_lightbox_caption_draft(self, val: str):
        self.lightbox_caption_draft = val

    def cancel_edit_caption(self):
        self.lightbox_editing_caption = False
        self.lightbox_caption_draft = ""

    def save_lightbox_caption(self):
        """Save the draft caption to the DB."""
        imgs = self.filtered_images
        if 0 <= self.preview_index < len(imgs):
            self.set_image_caption(imgs[self.preview_index].id, self.lightbox_caption_draft)
        self.lightbox_editing_caption = False
        self.lightbox_caption_draft = ""

    def dismiss_toast(self):
        """Clear the toast notification."""
        self.toast_visible = False
        self.upload_message = ""
        self.upload_status = ""


    def set_search_query(self, q: str):
        self.search_query = q

    def set_sort_by(self, sort: str):
        self.sort_by = sort

    def set_view_mode(self, mode: str):
        self.view_mode = mode

    def assign_folder(self, image_id: int, folder_name: str):
        """Move an image to a different (or no) folder."""
        actual = "" if folder_name == "(No folder)" else folder_name
        with rx.session() as session:
            record = session.get(ImageRecord, image_id)
            if record:
                record.folder_name = actual
                session.add(record)
                session.commit()
        self._refresh_images()
        self.upload_status = "success"
        self.upload_message = (
            f'📁 Moved to "{actual}"!' if actual else "📁 Removed from folder."
        )
        self.toast_visible = True

    # ── Toggle public/private per image ───────

    def toggle_image_public(self, image_id: int):
        """Flip the is_public flag on a single image."""
        new_state = False
        with rx.session() as session:
            record = session.get(ImageRecord, image_id)
            if record and record.owner_email == self._owner_email():
                record.is_public = not record.is_public
                new_state = record.is_public
                session.add(record)
                session.commit()
        self._refresh_images()
        if new_state:
            self.upload_status = "success"
            self.upload_message = "🌐 Image is now public."
        else:
            self.upload_status = "warning"
            self.upload_message = "🔒 Image set to private."
        self.toast_visible = True

    # ── Rename folder ─────────────────────────
    def set_rename_folder_input(self, val: str):
        self.rename_folder_input = val

    def start_rename_folder(self, folder_name: str):
        self.renaming_folder = folder_name
        self.rename_folder_input = folder_name

    def cancel_rename_folder(self):
        self.renaming_folder = ""
        self.rename_folder_input = ""

    def confirm_rename_folder(self):
        old = self.renaming_folder
        new = self.rename_folder_input.strip()
        if not new or new == old:
            self.renaming_folder = ""
            self.rename_folder_input = ""
            return
        if new in self.folders:
            self.upload_status = "error"
            self.upload_message = f'Folder "{new}" already exists.'
            self.toast_visible = True
            return
        with rx.session() as session:
            folder_rec = session.exec(
                Folder.select().where(
                    Folder.name == old,
                    Folder.owner_email == self._owner_email(),
                )
            ).first()
            if folder_rec:
                folder_rec.name = new
                session.add(folder_rec)
            records = session.exec(
                ImageRecord.select().where(
                    ImageRecord.folder_name == old,
                    ImageRecord.owner_email == self._owner_email(),
                )
            ).all()
            for r in records:
                r.folder_name = new
                session.add(r)
            session.commit()
        if self.folder_filter == old:
            self.folder_filter = new
        self.renaming_folder = ""
        self.rename_folder_input = ""
        self._refresh_folders()
        self._refresh_images()
        self.upload_status = "success"
        self.upload_message = f'✏️ Folder renamed to "{new}"!'
        self.toast_visible = True

    # ── Bulk selection ─────────────────────────
    def toggle_selection_mode(self):
        self.selection_mode = not self.selection_mode
        self.selected_image_ids = []

    def on_image_click(self, image_id: int, filename: str):
        """Route click to selection toggle or lightbox (with index) depending on mode."""
        if self.selection_mode:
            if image_id in self.selected_image_ids:
                self.selected_image_ids = [
                    i for i in self.selected_image_ids if i != image_id
                ]
            else:
                self.selected_image_ids = self.selected_image_ids + [image_id]
        else:
            # Find position in the filtered list so lightbox nav works
            self.preview_index = next(
                (i for i, img in enumerate(self.filtered_images) if img.id == image_id),
                -1,
            )
            return self.open_preview(filename)

    def select_image(self, image_id: int, filename: str, is_shift: bool = False):
        """Advanced selection with Shift+Click support."""
        if not self.selection_mode:
            self.on_image_click(image_id, filename)
            return

        active_ids = [img.id for img in self.filtered_images if img.id is not None]
        
        if not is_shift or self.last_selected_id not in active_ids:
            # Single toggle
            if image_id in self.selected_image_ids:
                self.selected_image_ids = [i for i in self.selected_image_ids if i != image_id]
            else:
                self.selected_image_ids = self.selected_image_ids + [image_id]
            self.last_selected_id = image_id
            return

        # Range toggle
        try:
            start_idx = active_ids.index(self.last_selected_id)
            end_idx = active_ids.index(image_id)
            low, high = min(start_idx, end_idx), max(start_idx, end_idx)
            
            range_set = set(active_ids[low : high + 1])
            current_set = set(self.selected_image_ids)
            
            # If the clicked item is already selected, deselect the range
            if image_id in current_set:
                self.selected_image_ids = list(current_set - range_set)
            else:
                self.selected_image_ids = list(current_set | range_set)
                
            self.last_selected_id = image_id
        except Exception:
            pass

    def select_all(self):
        self.selected_image_ids = [img.id for img in self.filtered_images]

    def clear_selection(self):
        self.selected_image_ids = []

    def copy_public_folder_link(self):
        """Generates and copies a public link to the current folder on the user's profile."""
        if not self.folder_filter: return
        # Using a friendly URL structure
        url = f"https://turkey.app/u/{self.user_name}?folder={self.folder_filter}"
        self.upload_status = "success"
        self.upload_message = "🚀 Public collection link copied!"
        self.toast_visible = True
        return rx.set_clipboard(url)

    def bulk_delete(self):
        ids = list(self.selected_image_ids)
        for image_id in ids:
            with rx.session() as session:
                assocs = session.exec(
                    ImageTag.select().where(ImageTag.image_id == image_id)
                ).all()
                for a in assocs:
                    session.delete(a)
                record = session.get(ImageRecord, image_id)
                if record:
                    fp = os.path.join(UPLOAD_DIR, record.filename)
                    if os.path.exists(fp):
                        os.remove(fp)
                    session.delete(record)
                session.commit()
        count = len(ids)
        self.selected_image_ids = []
        self.selection_mode = False
        self._refresh_images()
        self._recalc_storage()
        self.upload_status = "success"
        self.upload_message = f"🗑️ {count} image(s) deleted."
        self.toast_visible = True

    def bulk_move(self, folder_name: str):
        actual = "" if folder_name == "(No folder)" else folder_name
        with rx.session() as session:
            for image_id in self.selected_image_ids:
                record = session.get(ImageRecord, image_id)
                if record:
                    record.folder_name = actual
                    session.add(record)
            session.commit()
        count = len(self.selected_image_ids)
        self.selected_image_ids = []
        self.selection_mode = False
        self._refresh_images()
        dest = f'"{actual}"' if actual else "no folder"
        self.upload_status = "success"
        self.upload_message = f"📁 {count} image(s) moved to {dest}."
        self.toast_visible = True

    # ── User preferences ──────────────────────
    def toggle_settings(self):
        self.settings_open = not self.settings_open

    def close_settings(self):
        self.settings_open = False

    def set_bg_theme(self, gradient: str):
        self.bg_theme = gradient

    def set_accent(self, main: str, light: str):
        self.accent_hex = main
        self.accent_light = light

    def set_card_size(self, size: str):
        self.card_size = size

    def toggle_stats_bar(self):
        self.show_stats_bar = not self.show_stats_bar

    @rx.var
    def card_width(self) -> str:
        if self.card_size == "small":
            return "155px"
        elif self.card_size == "large":
            return "260px"
        return "200px"

    @rx.var
    def thumb_height(self) -> str:
        if self.card_size == "small":
            return "110px"
        elif self.card_size == "large":
            return "175px"
        return "140px"

    # ── Helpers ───────────────────────────────
    def _owner_email(self) -> str:
        return self.user_email or "anonymous"

    def _make_image_data(self, r: ImageRecord, tag_ids: list[int] | None = None) -> ImageData:
        sb = r.size_bytes
        return ImageData(
            id=r.id or 0,
            filename=r.filename,
            original_filename=r.original_filename,
            folder_name=r.folder_name,
            mime_type=r.mime_type,
            size_bytes=sb,
            size_mb=round(sb / (1024 * 1024), 1),
            size_kb=round(sb / 1024, 0),
            is_large=sb > 1024 * 1024,
            was_compressed=r.was_compressed,
            created_at=r.created_at,
            tag_ids=tag_ids or [],
            is_public=r.is_public,
            caption=r.caption,
            exif_info=r.exif_info,
        )

    def _refresh_images(self):
        with rx.session() as session:
            records = session.exec(
                ImageRecord.select().where(
                    ImageRecord.owner_email == self._owner_email()
                )
            ).all()
            # Build a map of image_id -> [tag_ids]
            all_image_tags = session.exec(ImageTag.select()).all()
            tag_map: dict[int, list[int]] = {}
            for it in all_image_tags:
                tag_map.setdefault(it.image_id, []).append(it.tag_id)
            self.images = [
                self._make_image_data(r, tag_map.get(r.id or 0, []))
                for r in records
            ]

    def _refresh_folders(self):
        with rx.session() as session:
            records = session.exec(
                Folder.select().where(
                    Folder.owner_email == self._owner_email()
                )
            ).all()
            self.folders = [r.name for r in records]
            self.public_folders = [r.name for r in records if r.is_public]

    def toggle_folder_public(self, folder_name: str):
        """Toggle whether a folder (and its content) is public."""
        with rx.session() as session:
            record = session.exec(
                Folder.select().where(
                    Folder.owner_email == self._owner_email(),
                    Folder.name == folder_name
                )
            ).first()
            if record:
                record.is_public = not record.is_public
                session.add(record)
                
                # Option: Also toggle all images in this folder?
                # For now, just the folder metadata.
                session.commit()
        self._refresh_folders()
        status = "public" if folder_name in self.public_folders else "private"
        self.upload_status = "success"
        self.upload_message = f'📁 Folder "{folder_name}" is now {status}.'
        self.toast_visible = True

    def _refresh_tags(self):
        with rx.session() as session:
            records = session.exec(
                Tag.select().where(Tag.owner_email == self._owner_email())
            ).all()
            self.tags = [TagData(id=r.id or 0, name=r.name, color=r.color) for r in records]

    def _recalc_storage(self):
        self.used_storage_bytes = sum(img.size_bytes for img in self.images)

    def _existing_filenames(self) -> set:
        return {img.original_filename for img in self.images}

    def _would_exceed_quota(self, additional: int) -> bool:
        return (self.used_storage_bytes + additional) > STORAGE_QUOTA_BYTES

    # ── Folder actions ────────────────────────
    def create_folder(self):
        name = self.new_folder_name.strip()
        if not name:
            self.upload_status = "error"
            self.upload_message = "Folder name cannot be empty."
            self.toast_visible = True
            return
        if name in self.folders:
            self.upload_status = "error"
            self.upload_message = f'Folder "{name}" already exists.'
            self.toast_visible = True
            return
        with rx.session() as session:
            session.add(Folder(
                name=name,
                owner_email=self._owner_email(),
                created_at=datetime.datetime.now().isoformat(),
            ))
            session.commit()
            self.folders.append(name) 
            self.selected_folder = name 
            
        self.new_folder_name = ""
        self._refresh_folders()
        self.upload_status = "success"
        self.upload_message = f' Folder "{name}" created!'
        self.toast_visible = True

    def delete_folder(self, folder_name: str):
        """Delete a folder, moving its images back to 'no folder'."""
        with rx.session() as session:
            records = session.exec(
                ImageRecord.select().where(
                    ImageRecord.folder_name == folder_name,
                    ImageRecord.owner_email == self._owner_email(),
                )
            ).all()
            for r in records:
                r.folder_name = ""
                session.add(r)
            folder_rec = session.exec(
                Folder.select().where(
                    Folder.name == folder_name,
                    Folder.owner_email == self._owner_email(),
                )
            ).first()
            if folder_rec:
                session.delete(folder_rec)
            session.commit()
        if self.folder_filter == folder_name:
            self.folder_filter = ""
        self._refresh_folders()
        self._refresh_images()
        self.upload_status = "success"
        self.upload_message = f'🗑️ Folder "{folder_name}" deleted.'
        self.toast_visible = True

    def delete_image(self, image_id: int):
        with rx.session() as session:
            # Also remove all tag associations for this image
            assocs = session.exec(
                ImageTag.select().where(ImageTag.image_id == image_id)
            ).all()
            for a in assocs:
                session.delete(a)
            record = session.get(ImageRecord, image_id)
            if record:
                filepath = os.path.join(UPLOAD_DIR, record.filename)
                if os.path.exists(filepath):
                    os.remove(filepath)
                session.delete(record)
            session.commit()
        self._refresh_images()
        self._recalc_storage()
        self.upload_status = "success"
        self.upload_message = "🗑️ Image deleted."
        self.toast_visible = True

    # ── Tag actions ───────────────────────────
    def set_new_tag_name(self, name: str):
        self.new_tag_name = name

    def set_new_tag_color(self, color: str):
        self.new_tag_color = color

    def set_tag_filter(self, tag_id: str):
        self.tag_filter = tag_id

    def set_tag_search(self, q: str):
        self.tag_search = q

    def create_tag(self):
        """Task B: Create a new tag."""
        name = self.new_tag_name.strip()
        if not name:
            self.upload_status = "error"
            self.upload_message = "Tag name cannot be empty."
            self.toast_visible = True
            return
        if any(t.name.lower() == name.lower() for t in self.tags):
            self.upload_status = "error"
            self.upload_message = f'Tag "{name}" already exists.'
            self.toast_visible = True
            return
        with rx.session() as session:
            session.add(Tag(
                name=name,
                color=self.new_tag_color,
                owner_email=self._owner_email(),
                created_at=datetime.datetime.now().isoformat(),
            ))
            session.commit()
        self.new_tag_name = ""
        self.new_tag_color = "#7c3aed"
        self._refresh_tags()
        self.upload_status = "success"
        self.upload_message = f'🏷️ Tag "{name}" created!'
        self.toast_visible = True

    def delete_tag(self, tag_id: int):
        """Task G: Delete a tag and all its assignments."""
        with rx.session() as session:
            assocs = session.exec(
                ImageTag.select().where(ImageTag.tag_id == tag_id)
            ).all()
            for a in assocs:
                session.delete(a)
            tag = session.get(Tag, tag_id)
            if tag:
                session.delete(tag)
            session.commit()
        self._refresh_tags()
        self._refresh_images()
        if self.tag_filter == str(tag_id):
            self.tag_filter = ""
        self.upload_status = "success"
        self.upload_message = "🗑️ Tag deleted."
        self.toast_visible = True

    def assign_tag(self, image_id: int, tag_id: int):
        """Task C: Assign a tag to an image."""
        with rx.session() as session:
            existing = session.exec(
                ImageTag.select().where(
                    ImageTag.image_id == image_id,
                    ImageTag.tag_id == tag_id,
                )
            ).first()
            if not existing:
                session.add(ImageTag(image_id=image_id, tag_id=tag_id))
                session.commit()
        self._refresh_images()

    def remove_tag(self, image_id: int, tag_id: int):
        """Task D: Remove a tag from an image."""
        with rx.session() as session:
            assoc = session.exec(
                ImageTag.select().where(
                    ImageTag.image_id == image_id,
                    ImageTag.tag_id == tag_id,
                )
            ).first()
            if assoc:
                session.delete(assoc)
                session.commit()
        self._refresh_images()

    # ── Upload ─────────────────────────────────
    async def handle_upload(self, files: list[rx.UploadFile]):
        self.is_uploading = True
        self.upload_status = ""
        self.upload_message = ""
        self.pending_duplicates = []

        successes = 0
        errors: list[str] = []
        buffered: list[dict] = []
        existing = self._existing_filenames()

        for file in files:
            name = file.filename
            data = await file.read()
            size = len(data)
            ext = os.path.splitext(name)[1].lower()

            # 1. Type check
            if ext not in (".jpg", ".jpeg", ".png", ".webp"):
                errors.append(f"{name}: Only JPG, PNG and WEBP are allowed.")
                continue

            # 2. Size hard reject (>20 MB)
            if size > COMPRESS_MAX_BYTES:
                errors.append(f"{name}: Exceeds 20 MB limit.")
                continue

            # 3. Size hard reject (>10 MB, no compression yet)
            if size > MAX_FILE_SIZE_BYTES:
                errors.append(f"{name}: Exceeds 10 MB. Files 10–20 MB are auto-compressed.")
                continue

            # 4. Quota check
            if self._would_exceed_quota(size):
                errors.append(f"{name}: Would exceed your 1 GB storage quota.")
                continue

            # 5. Duplicate check
            if name in existing:
                buffered.append({
                    "name": name,
                    "data_b64": base64.b64encode(data).decode(),
                    "size": size,
                    "ext": ext,
                })
                continue

            # 6. Compress if 10–20 MB
            was_compressed = False
            final_data = data
            final_mime = "image/jpeg" if ext in (".jpg", ".jpeg") else "image/png"
            if COMPRESS_THRESHOLD_BYTES <= size <= COMPRESS_MAX_BYTES:
                try:
                    final_data, final_mime = self._compress_image(data)
                    was_compressed = True
                except Exception as e:
                    errors.append(f"{name}: Compression failed — {e}")
                    continue

            await self._save_image(name, final_data, final_mime, size, was_compressed)
            existing.add(name)
            successes += 1

        self.is_uploading = False

        if buffered:
            self.pending_duplicates = [b["name"] for b in buffered]
            self.pending_upload_data = buffered
            self.show_duplicate_modal = True

        parts = []
        if successes:
            parts.append(f"✅ {successes} image(s) uploaded!")
        if errors:
            parts.append("⚠️ " + " | ".join(errors))

        if parts:
            self.upload_status = "error" if (errors and not successes) else "success"
            self.upload_message = " ".join(parts)
            self.toast_visible = True

        self._refresh_images()
        self._recalc_storage()

    async def confirm_duplicate_upload(self):
        self.show_duplicate_modal = False
        for item in self.pending_upload_data:
            data = base64.b64decode(item["data_b64"])
            size = item["size"]
            name = item["name"]
            ext = item["ext"]
            final_data = data
            final_mime = "image/jpeg" if ext in (".jpg", ".jpeg") else "image/png"
            was_compressed = False
            if COMPRESS_THRESHOLD_BYTES <= size <= COMPRESS_MAX_BYTES:
                try:
                    final_data, final_mime = self._compress_image(data)
                    was_compressed = True
                except Exception:
                    pass
            await self._save_image(name, final_data, final_mime, size, was_compressed)
        self.pending_upload_data = []
        self.pending_duplicates = []
        self._refresh_images()
        self._recalc_storage()
        self.upload_status = "success"
        self.upload_message = "✅ Duplicates overwritten!"
        self.toast_visible = True

    def cancel_duplicate_upload(self):
        self.show_duplicate_modal = False
        self.pending_upload_data = []
        self.pending_duplicates = []
        self.upload_message = "⚠️ Duplicate images were skipped."
        self.toast_visible = True
        self.upload_status = "warning"

    def _compress_image(self, data: bytes) -> tuple[bytes, str]:
        from PIL import Image as PILImage
        img = PILImage.open(io.BytesIO(data))
        if img.mode in ("RGBA", "P"):
            img = img.convert("RGB")
        buf = io.BytesIO()
        img.save(buf, format="JPEG", optimize=True, quality=75)
        return buf.getvalue(), "image/jpeg"

    async def _save_image(self, original_name: str, data: bytes, mime: str, original_size: int, was_compressed: bool):
        ts = datetime.datetime.now().strftime("%Y%m%d_%H%M%S_%f")
        safe_name = f"{ts}_{original_name.replace(' ', '_')}"
        filepath = os.path.join(UPLOAD_DIR, safe_name)
        with open(filepath, "wb") as f:
            f.write(data)
        import json
        exif_json = self._extract_exif(data)
        
        with rx.session() as session:
            new_image = ImageRecord(
                filename=safe_name,
                original_filename=original_name,
                folder_name=self.selected_folder,
                owner_email=self._owner_email(),
                mime_type=mime,
                size_bytes=len(data),
                was_compressed=was_compressed,
                created_at=datetime.datetime.now().isoformat(),
                exif_info=exif_json,
            )
            session.add(new_image)
            session.commit()
            session.refresh(new_image)
            image_id = str(new_image.id)

        # ─── B. Trigger the AI Pipeline (Capstone Logic) ───────────────────────────
        try:
            # 1. Get Embeddings from Hugging Face
            vector = await get_image_embeddings(data)
            
            # 2. Upsert to Pinecone if vector is valid
            if vector and isinstance(vector, list):
                metadata = {
                    "filename": original_name,
                    "folder": self.selected_folder,
                    "location": "TurkeyApp_Library", # Custom tag for your Capstone
                    "upload_date": datetime.datetime.now().isoformat()
                }
                await upsert_to_pinecone(image_id, vector, metadata)
                print(f"AI: Successfully indexed image {image_id}")
        except Exception as ai_err:
            print(f"AI Pipeline Warning: {ai_err}")
            # We don't block the upload if AI fails, as per your "Consistency" rule.

    def _extract_exif(self, data: bytes) -> str:
        """Helper to extract EXIF metadata from image bytes."""
        try:
            import json, io
            from PIL import Image as PILImage
            from PIL.ExifTags import TAGS
            
            img = PILImage.open(io.BytesIO(data))
            info = img.getexif()
            if not info: return ""
            
            exif_data = {}
            for tag, value in info.items():
                decoded = TAGS.get(tag, tag)
                # Convert common non-serializable types to string
                if isinstance(value, bytes):
                    try: value = value.decode()
                    except: value = str(value)
                elif not isinstance(value, (str, int, float, bool)):
                    value = str(value)
                exif_data[str(decoded)] = value
            return json.dumps(exif_data)
        except:
            return ""

    # ── Export ────────────────────────────────────────
    def export_folder(self, folder_name: str):
        """Bundle all images in a folder into a ZIP and trigger a browser download."""
        import zipfile as _zip
        to_export = [img for img in self.images if img.folder_name == folder_name]
        if not to_export:
            self.export_status = f'No images in folder "{folder_name}".'
            return
        ts = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
        safe = folder_name.replace(" ", "_")
        zip_filename = f"export_{safe}_{ts}.zip"
        zip_path = os.path.join(UPLOAD_DIR, zip_filename)
        try:
            with _zip.ZipFile(zip_path, "w", _zip.ZIP_DEFLATED) as zf:
                for img in to_export:
                    fp = os.path.join(UPLOAD_DIR, img.filename)
                    if os.path.exists(fp):
                        zf.write(fp, img.original_filename)
            self.export_status = f'✅ {len(to_export)} image(s) zipped — downloading…'
            return rx.download(
                url=rx.get_upload_url(zip_filename),
                filename=f"{folder_name}.zip",
            )
        except Exception as e:
            self.export_status = f'❌ Export failed: {e}'

    def export_portfolio(self):
        """Generate a self-contained HTML portfolio of the current view."""
        current_images = self.images
        if not current_images:
            self.upload_status = "error"
            self.upload_message = "No images to export in this view."
            self.toast_visible = True
            return

        self.upload_status = "success"
        self.upload_message = "Generating your digital portfolio..."
        self.toast_visible = True

        export_data = []
        for img in current_images:
            # Read image and convert to data URI
            full_path = os.path.join(UPLOAD_DIR, img.filename)
            if os.path.exists(full_path):
                data_uri = get_image_data_uri(full_path)
                export_data.append({
                    "name": img.original_filename,
                    "stem": os.path.splitext(img.original_filename)[0],
                    "size_kb": f"{img.size_kb:.1f}",
                    "data_uri": data_uri
                })

        title = self.selected_folder if self.selected_folder else "All Media"
        html_content = generate_portfolio_html(export_data, title)
        
        return rx.download(
            data=html_content,
            filename=f"portfolio_{title.lower().replace(' ', '_')}.html"
        )
