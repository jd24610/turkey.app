"""Masonry HTML gallery generator — takes a folder of images and builds a self-contained HTML file."""

import argparse
import sys
from pathlib import Path

from TurkeyApp.image_support import collect_images, SUPPORTED_EXTENSIONS


def build_js_array(images: list) -> str:
    """Build a JS array string of image objects to drop into the HTML template."""
    items = []
    for img in images:
        # Escape backtick / backslash / dollar signs so they don't break the JS template literal
        name = img["name"].replace("\\", "\\\\").replace("`", "\\`").replace("$", "\\$")
        stem = img["stem"].replace("\\", "\\\\").replace("`", "\\`").replace("$", "\\$")
        items.append(
            f'  {{ name: `{name}`, stem: `{stem}`, '
            f'size: `{img["size_kb"]} KB`, src: `{img["data_uri"]}` }}'
        )
    return "[\n" + ",\n".join(items) + "\n]"


def generate_html(images: list, folder_name: str) -> str:
    """Build the full self-contained HTML gallery page."""
    image_js = build_js_array(images)
    count = len(images)
    plural = "s" if count != 1 else ""

    empty_msg = ""
    if not images:
        empty_msg = '<p style="color:#888; font-size:1.2rem;">No images found in this folder.</p>'

    html = f"""<!DOCTYPE html>
<html lang="en">
<head>
  <meta charset="UTF-8" />
  <meta name="viewport" content="width=device-width, initial-scale=1.0" />
  <title>{folder_name} Gallery</title>
  <style>
    * {{ box-sizing: border-box; margin: 0; padding: 0; }}
    body {{
      background: #111;
      color: #eee;
      font-family: system-ui, sans-serif;
      padding: 2rem;
    }}
    header {{
      display: flex;
      align-items: center;
      justify-content: space-between;
      margin-bottom: 1.5rem;
    }}
    h1 {{ font-size: 1.6rem; }}
    .count {{ color: #aaa; font-size: 0.95rem; }}
    .masonry {{
      column-count: 4;
      column-gap: 12px;
    }}
    @media (max-width: 1200px) {{ .masonry {{ column-count: 3; }} }}
    @media (max-width: 800px)  {{ .masonry {{ column-count: 2; }} }}
    @media (max-width: 480px)  {{ .masonry {{ column-count: 1; }} }}
    .masonry-item {{
      break-inside: avoid;
      margin-bottom: 12px;
      position: relative;
      border-radius: 8px;
      overflow: hidden;
      cursor: zoom-in;
    }}
    .masonry-item img {{
      width: 100%;
      display: block;
      border-radius: 8px;
      transition: transform 0.2s ease;
    }}
    .masonry-item:hover img {{ transform: scale(1.03); }}
    .caption {{
      position: absolute;
      bottom: 0; left: 0; right: 0;
      background: linear-gradient(transparent, rgba(0,0,0,0.7));
      color: #fff;
      font-size: 0.75rem;
      padding: 20px 8px 6px;
      opacity: 0;
      transition: opacity 0.2s;
    }}
    .masonry-item:hover .caption {{ opacity: 1; }}
    /* Lightbox */
    #lightbox {{
      display: none;
      position: fixed;
      inset: 0;
      background: rgba(0,0,0,0.92);
      z-index: 999;
      align-items: center;
      justify-content: center;
      flex-direction: column;
      gap: 1rem;
    }}
    #lightbox.active {{ display: flex; }}
    #lightbox img {{ max-width: 90vw; max-height: 85vh; border-radius: 8px; }}
    #lightbox .lb-caption {{ color: #ccc; font-size: 0.85rem; }}
    #lightbox .close {{
      position: absolute;
      top: 1rem; right: 1.5rem;
      font-size: 2rem;
      cursor: pointer;
      color: #fff;
      line-height: 1;
    }}
  </style>
</head>
<body>
  <header>
    <div>
      <h1>📁 {folder_name}</h1>
      <span class="count">{count} image{plural}</span>
    </div>
  </header>

  {empty_msg}

  <div class="masonry" id="gallery"></div>

  <!-- Lightbox -->
  <div id="lightbox">
    <span class="close" onclick="closeLightbox()">✕</span>
    <img id="lb-img" src="" alt="" />
    <div class="lb-caption" id="lb-caption"></div>
  </div>

  <script>
    const images = {image_js};

    const gallery = document.getElementById('gallery');
    images.forEach((img, i) => {{
      const item = document.createElement('div');
      item.className = 'masonry-item';
      item.innerHTML = `
        <img src="${{img.src}}" alt="${{img.name}}" loading="lazy" />
        <div class="caption">${{img.name}} &middot; ${{img.size}}</div>
      `;
      item.addEventListener('click', () => openLightbox(i));
      gallery.appendChild(item);
    }});

    function openLightbox(i) {{
      document.getElementById('lb-img').src = images[i].src;
      document.getElementById('lb-caption').textContent = images[i].name + ' · ' + images[i].size;
      document.getElementById('lightbox').classList.add('active');
    }}
    function closeLightbox() {{
      document.getElementById('lightbox').classList.remove('active');
    }}
    document.getElementById('lightbox').addEventListener('click', e => {{
      if (e.target === e.currentTarget) closeLightbox();
    }});
    document.addEventListener('keydown', e => {{
      if (e.key === 'Escape') closeLightbox();
    }});
  </script>
</body>
</html>"""
    return html


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
        print(f"  Supported formats: {', '.join(sorted(SUPPORTED_EXTENSIONS))}")
    else:
        print(f"\n  Found {len(images)} image(s). Building HTML...")

    html = generate_html(images, folder_name)

    with open(output_path, "w", encoding="utf-8") as f:
        f.write(html)

    size_mb = output_path.stat().st_size / (1024 * 1024)
    print(f"  Saved  -> {output_path}  ({size_mb:.1f} MB)")
    print(f"\n  Open the HTML file in your browser to view your gallery!\n")


if __name__ == "__main__":
    main()