# 🦃 turkey.app
### Your Intelligent Media Library & Social Gallery

**turkey.app** is a premium, self-hosted media library solution inspired by modern social gallery aesthetics. It transforms your raw image collection into a stunning, Pinterest-style experience with powerful organization tools and a robust social discovery layer.

![License](https://img.shields.io/badge/license-MIT-blue.svg)
![Reflex](https://img.shields.io/badge/Reflex-Framework-purple.svg)
![UI](https://img.shields.io/badge/UI-Pinterest--Light-violet.svg)

---

## ✨ Features

- **🎨 Pinterest-Inspired UI**: A high-performance, responsive masonry gallery with a elegant light theme and violet accents.
- **🔐 Secure Authentication**: Integrated Google OAuth 2.0 for seamless and secure sign-in.
- **📁 Advanced Organization**: Drag-and-drop uploads, folder management, and a dynamic tagging system.
- **🚀 Social Discovery**: Follow creators, like public photos, and explore the community feed.
- **⚡ Static Gallery Generator**: A standalone Python CLI to build self-contained, beautiful HTML archives from any local folder.
- **📦 Smart Storage**: Automatic compression for large images and quota management.

---

## 🛠️ Getting Started

### Prerequisites

- **Python 3.10+**
- **uv** (Recommended) or **pip**
- **Google Cloud Console Credentials** (for OAuth)

### Installation

1. **Clone the repository:**
   ```bash
   git clone https://gitlab.com/jdecossard01-group/post.project.git
   cd post.project
   ```

2. **Install dependencies:**
   Using `uv` (fastest):
   ```bash
   uv sync
   ```
   Or using `pip`:
   ```bash
   pip install -r requirements.txt
   ```

3. **Configure Environment:**
   Update your `rxconfig.py` with your **Google Client ID**.

4. **Run the application:**
   ```bash
   uv reflex run
   ```

---

## 📁 Project Structure

- `/TurkeyApp`: Core application logic and Reflex pages.
- `/uploaded_files`: Local storage for images and avatars.
- `TurkeyApp/folder.name.py`: The static gallery generator CLI.
- `rxconfig.py`: Central configuration for the app and database.

---

## 🖼️ Static Gallery Generator

You can generate a self-contained HTML gallery from any folder on your machine:

```bash
python -m TurkeyApp.folder.name /path/to/my/photos -o gallery.html
```

---

## 🤝 Contributing

We welcome contributions! Please feel free to submit a Pull Request or open an issue for feature requests.

## 📄 License

Distributed under the MIT License. See `LICENSE` for more information.

---

*Built with ❤️ using Reflex.*

