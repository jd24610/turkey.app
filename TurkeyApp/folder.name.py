"""Masonry HTML gallery generator — takes a folder of images and builds a self-contained HTML file."""

import argparse
import sys
from pathlib import Path
from TurkeyApp.image_support import collect_images
from TurkeyApp.portfolio_utils import generate_portfolio_html


def main():
    parser = argparse.ArgumentParser(
        description="Generate a masonry HTML gallery from a folder of images."
    )
    parser.add_argument(
        "folder",
        nargs="?",
        default=".",
        help="Path to the image folder (default: current directory)",
    )
    parser.add_argument(
        "-o", "--output",
        default=None,
        help="Output HTML filename (default: <folder>_gallery.html)",
    )
    args = parser.parse_args()

    folder = Path(args.folder).resolve()

    if not folder.is_dir():
        print(f"Error: '{folder}' is not a valid folder.")
        sys.exit(1)

    folder_name = folder.name
    output_name = args.output or f"{folder_name}_gallery.html"
    output_path = Path(output_name).resolve()

    print(f"\n  Masonry Gallery Generator")
    print(f"  Folder : {folder}")
    print(f"  Output : {output_path}\n")

    images = collect_images(folder)

    if not images:
        print(f"\n  Warning: No supported images found.")
    else:
        print(f"\n  Found {len(images)} image(s). Building HTML...")

    html = generate_portfolio_html(images, folder_name)

    with open(output_path, "w", encoding="utf-8") as f:
        f.write(html)

    size_mb = output_path.stat().st_size / (1024 * 1024)
    print(f"  Saved  -> {output_path}  ({size_mb:.1f} MB)")
    print(f"\n  Open the HTML file in your browser to view your gallery!\n")


if __name__ == "__main__":
    main()