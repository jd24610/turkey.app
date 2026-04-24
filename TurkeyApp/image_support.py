"""Utility helpers for reading and encoding image files."""

import base64
import mimetypes
from pathlib import Path


SUPPORTED_EXTENSIONS = {".jpg", ".jpeg", ".png", ".gif", ".webp", ".bmp", ".svg", ".avif"}


def encode_image(img_path: Path) -> tuple:
    """Turn an image file into a base64 data-URI so we can embed it in HTML."""
    # Auto-detect the mime type (e.g. "image/png")
    mime_type, _ = mimetypes.guess_type(str(img_path))

    # Fallback lookup if auto-detect fails
    if not mime_type:
        fallback = {
            ".jpg": "image/jpeg",
            ".jpeg": "image/jpeg",
            ".png": "image/png",
            ".gif": "image/gif",
            ".webp": "image/webp",
            ".bmp": "image/bmp",
            ".svg": "image/svg+xml",
            ".avif": "image/avif",
        }
        mime_type = fallback.get(img_path.suffix.lower(), "image/jpeg")

    # Read the file and base64-encode it
    with open(img_path, "rb") as f:
        encoded = base64.b64encode(f.read()).decode("utf-8")

    data_uri = f"data:{mime_type};base64,{encoded}"
    return data_uri, mime_type


def get_image_data_uri(img_path: str) -> str:
    """Convenience wrapper to get just the data URI for a filename/path."""
    uri, _ = encode_image(Path(img_path))
    return uri


def collect_images(folder: Path) -> list:
    """Go through a folder and return a list of encoded image dicts."""
    images = []

    # Sort alphabetically so the gallery has a consistent order
    all_files = sorted(folder.iterdir(), key=lambda p: p.name.lower())

    for file in all_files:
        if file.is_file() and file.suffix.lower() in SUPPORTED_EXTENSIONS:
            print(f"  -> Encoding {file.name} ...")
            try:
                data_uri, mime_type = encode_image(file)
                size_kb = file.stat().st_size / 1024
                images.append({
                    "name": file.name,
                    "stem": file.stem,          # filename without extension
                    "data_uri": data_uri,
                    "mime_type": mime_type,
                    "size_kb": round(size_kb, 1),
                })
            except Exception as e:
                print(f"    Warning: Skipping {file.name} — {e}")

    return images
