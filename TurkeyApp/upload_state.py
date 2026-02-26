"""State management for Import/Export functionality."""

import reflex as rx
import datetime
import json
import os
import io
import base64
from pydantic import BaseModel
from TurkeyApp.models import ImageRecord, Folder

# Constants
MAX_FILE_SIZE_BYTES = 10 * 1024 * 1024        # 10 MB hard limit
COMPRESS_THRESHOLD_BYTES = 10 * 1024 * 1024   # start compressing at 10 MB
COMPRESS_MAX_BYTES = 20 * 1024 * 1024         # up to 20 MB gets auto-compressed
STORAGE_QUOTA_BYTES = 1 * 1024 * 1024 * 1024  # 1 GB quota
UPLOAD_DIR = "uploaded_images"

os.makedirs(UPLOAD_DIR, exist_ok=True)


class ImageData(BaseModel):
    """Typed image record for the UI."""
    id: int = 0
    filename: str = ""
    original_filename: str = ""
    folder_name: str = ""
    mime_type: str = "image/jpeg"
    size_bytes: int = 0
    size_mb: float = 0.0
    size_kb: float = 0.0
    is_large: bool = False       # size_bytes > 1MB
    was_compressed: bool = False
    created_at: str = ""


class UploadState(rx.State):
    """State for the Import/Export page."""

    # ---- Auth info ----
    user_email: str = ""
    user_name: str = ""

    # ---- Upload feedback ----
    upload_status: str = ""
    upload_message: str = ""
    is_uploading: bool = False

    # ---- Data ----
    images: list[ImageData] = []
    folders: list[str] = []
    selected_folder: str = ""
    new_folder_name: str = ""
    folder_filter: str = ""

    # ---- Storage ----
    used_storage_bytes: int = 0

    # ---- Export ----
    export_status: str = ""

    # ---- Duplicate handling ----
    pending_duplicates: list[str] = []
    show_duplicate_modal: bool = False
    pending_upload_data: list[dict] = []

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
        if not self.folder_filter:
            return self.images
        return [img for img in self.images if img.folder_name == self.folder_filter]

    @rx.var
    def image_count(self) -> int:
        return len(self.filtered_images)

    # ── Lifecycle ─────────────────────────────
    def on_load(self):
        self._refresh_images()
        self._refresh_folders()
        self._recalc_storage()

    def set_selected_folder(self, folder: str):
        self.selected_folder = folder

    def set_new_folder_name(self, name: str):
        self.new_folder_name = name

    def set_folder_filter(self, folder: str):
        self.folder_filter = folder

    # ── Helpers ───────────────────────────────
    def _owner_email(self) -> str:
        return self.user_email or "anonymous"

    def _make_image_data(self, r: ImageRecord) -> ImageData:
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
        )

    def _refresh_images(self):
        with rx.session() as session:
            records = session.exec(
                ImageRecord.select().where(
                    ImageRecord.owner_email == self._owner_email()
                )
            ).all()
            self.images = [self._make_image_data(r) for r in records]

    def _refresh_folders(self):
        with rx.session() as session:
            records = session.exec(
                Folder.select().where(
                    Folder.owner_email == self._owner_email()
                )
            ).all()
            self.folders = [r.name for r in records]

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
            return
        if name in self.folders:
            self.upload_status = "error"
            self.upload_message = f'Folder "{name}" already exists.'
            return
        with rx.session() as session:
            session.add(Folder(
                name=name,
                owner_email=self._owner_email(),
                created_at=datetime.datetime.now().isoformat(),
            ))
            session.commit()
        self.new_folder_name = ""
        self._refresh_folders()
        self.upload_status = "success"
        self.upload_message = f'✅ Folder "{name}" created!'

    def delete_image(self, image_id: int):
        with rx.session() as session:
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
            if ext not in (".jpg", ".jpeg", ".png"):
                errors.append(f"{name}: Only JPG and PNG are allowed.")
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

            self._save_image(name, final_data, final_mime, size, was_compressed)
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

        self._refresh_images()
        self._recalc_storage()

    def confirm_duplicate_upload(self):
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
            self._save_image(name, final_data, final_mime, size, was_compressed)
        self.pending_upload_data = []
        self.pending_duplicates = []
        self._refresh_images()
        self._recalc_storage()
        self.upload_status = "success"
        self.upload_message = "✅ Duplicates overwritten!"

    def cancel_duplicate_upload(self):
        self.show_duplicate_modal = False
        self.pending_upload_data = []
        self.pending_duplicates = []
        self.upload_message = "⚠️ Duplicate images were skipped."
        self.upload_status = "warning"

    def _compress_image(self, data: bytes) -> tuple[bytes, str]:
        from PIL import Image as PILImage
        img = PILImage.open(io.BytesIO(data))
        if img.mode in ("RGBA", "P"):
            img = img.convert("RGB")
        buf = io.BytesIO()
        img.save(buf, format="JPEG", optimize=True, quality=75)
        return buf.getvalue(), "image/jpeg"

    def _save_image(self, original_name: str, data: bytes, mime: str, original_size: int, was_compressed: bool):
        ts = datetime.datetime.now().strftime("%Y%m%d_%H%M%S_%f")
        safe_name = f"{ts}_{original_name.replace(' ', '_')}"
        filepath = os.path.join(UPLOAD_DIR, safe_name)
        with open(filepath, "wb") as f:
            f.write(data)
        with rx.session() as session:
            session.add(ImageRecord(
                filename=safe_name,
                original_filename=original_name,
                folder_name=self.selected_folder,
                owner_email=self._owner_email(),
                mime_type=mime,
                size_bytes=len(data),
                was_compressed=was_compressed,
                created_at=datetime.datetime.now().isoformat(),
            ))
            session.commit()

    # ── Export ────────────────────────────────
    def export_folder(self, folder_name: str):
        to_export = [img for img in self.images if img.folder_name == folder_name]
        if not to_export:
            self.export_status = f'No images in folder "{folder_name}".'
            return
        manifest = {
            "folder": folder_name,
            "owner": self._owner_email(),
            "exported_at": datetime.datetime.now().isoformat(),
            "images": [img.dict() for img in to_export],
        }
        ts = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
        export_path = os.path.join(UPLOAD_DIR, f"export_{folder_name}_{ts}.json")
        with open(export_path, "w") as f:
            json.dump(manifest, f, indent=2)
        self.export_status = f'✅ "{folder_name}" exported → {export_path}'
