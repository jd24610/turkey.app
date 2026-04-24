"""Utilities for generating self-contained portfolio galleries."""

import base64
import os

def build_js_array(images: list) -> str:
    """Build a JS array string of image objects for the HTML template."""
    items = []
    for img in images:
        # Escape characters that break JS template literals
        name = img["name"].replace("\\", "\\\\").replace("`", "\\`").replace("$", "\\$")
        stem = img["stem"].replace("\\", "\\\\").replace("`", "\\`").replace("$", "\\$")
        items.append(
            f'  {{ name: `{name}`, stem: `{stem}`, '
            f'size: `{img["size_kb"]} KB`, src: `{img["data_uri"]}` }}'
        )
    return "[\n" + ",\n".join(items) + "\n]"

def generate_portfolio_html(images: list, title: str) -> str:
    """Build the full self-contained HTML gallery page."""
    image_js = build_js_array(images)
    count = len(images)
    
    html = f"""<!DOCTYPE html>
<html lang="en">
<head>
  <meta charset="UTF-8" />
  <meta name="viewport" content="width=device-width, initial-scale=1.0" />
  <title>{title} Portfolio | turkey.app</title>
  <link rel="preconnect" href="https://fonts.googleapis.com">
  <link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
  <link href="https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700&display=swap" rel="stylesheet">
  <style>
    * {{ box-sizing: border-box; margin: 0; padding: 0; }}
    body {{
      background: #fdfdfd;
      color: #111827;
      font-family: 'Inter', system-ui, -apple-system, sans-serif;
      padding: 3rem 2rem;
      line-height: 1.5;
    }}
    header {{
      max-width: 1200px;
      margin: 0 auto 3rem;
    }}
    .badge {{
      display: inline-flex;
      background: rgba(124, 58, 237, 0.1);
      color: #7c3aed;
      padding: 4px 12px;
      border-radius: 20px;
      font-size: 0.75rem;
      font-weight: 600;
      margin-bottom: 0.5rem;
    }}
    h1 {{ font-size: 2.25rem; font-weight: 800; letter-spacing: -0.025em; }}
    .count {{ color: #6b7280; font-size: 1rem; }}
    
    .masonry {{
      column-count: 4; column-gap: 20px;
      max-width: 1400px; margin: 0 auto;
    }}
    @media (max-width: 1200px) {{ .masonry {{ column-count: 3; }} }}
    @media (max-width: 800px)  {{ .masonry {{ column-count: 2; }} }}
    @media (max-width: 480px)  {{ .masonry {{ column-count: 1; }} }}
    
    .item {{
      break-inside: avoid; margin-bottom: 20px;
      border-radius: 16px; overflow: hidden;
      background: #fff; border: 1px solid #f1f1f1;
      transition: all 0.3s ease; cursor: zoom-in;
    }}
    .item:hover {{ transform: translateY(-4px); border-color: #7c3aed; }}
    .item img {{ width: 100%; display: block; }}
    .cap {{ padding: 12px 16px; font-size: 0.85rem; font-weight: 600; }}

    #lightbox {{
      display: none; position: fixed; inset: 0;
      background: rgba(255,255,255,0.98); backdrop-filter: blur(12px);
      z-index: 999; align-items: center; justify-content: center;
    }}
    #lightbox.active {{ display: flex; }}
    #lightbox img {{ max-width: 90vw; max-height: 80vh; border-radius: 20px; box-shadow: 0 40px 100px rgba(0,0,0,0.1); }}
    .close {{ position: fixed; top: 2rem; right: 2rem; font-size: 2rem; cursor: pointer; border: none; background: none; }}
  </style>
</head>
<body>
  <header>
    <div class="badge">Digital Portfolio</div>
    <h1>{title}</h1>
    <span class="count">{count} media files</span>
  </header>
  <div class="masonry" id="gallery"></div>
  <div id="lightbox" onclick="closeLightbox()">
    <button class="close">✕</button>
    <img id="lb-img" src="" />
  </div>
  <script>
    const images = {image_js};
    const gallery = document.getElementById('gallery');
    images.forEach((img, i) => {{
      const div = document.createElement('div');
      div.className = 'item';
      div.innerHTML = `<img src="${{img.src}}" /><div class="cap">${{img.stem}}</div>`;
      div.onclick = () => {{
        document.getElementById('lb-img').src = img.src;
        document.getElementById('lightbox').classList.add('active');
      }};
      gallery.appendChild(div);
    }});
    function closeLightbox() {{
      document.getElementById('lightbox').classList.remove('active');
    }}
  </script>
</body>
</html>"""
    return html
