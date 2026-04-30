"""ProfileState — manages user onboarding, own-profile data, and public profile viewing."""

import re
import os
import uuid
import reflex as rx
import sqlmodel
from datetime import datetime
from pydantic import BaseModel
from typing import Union, List, Optional

from TurkeyApp.models import UserProfile, ImageRecord, Follow, Like, Notification, Comment

AVATAR_DIR = os.path.join("assets", "uploaded_files", "avatars")
os.makedirs(AVATAR_DIR, exist_ok=True)


# ───────────────────────────────────────────────
#  Helpers / data models
# ───────────────────────────────────────────────

class SearchResult(BaseModel):
    """Typed search result for the discovery page."""
    username: str = ""
    display_name: str = ""
    bio: str = ""
    location: str = ""
    avatar_url: str = ""    # "avatars/abc123.jpg"
    full_avatar_url: str = ""
    member_since: str = ""
    image_count: int = 0
    image_count_str: str = "0"
    follower_count: int = 0


class SemanticImageResult(BaseModel):
    """Result for AI-driven image search."""
    id: int = 0
    filename: str = ""
    full_url: str = ""
    caption: str = ""
    owner_username: str = ""


# ─────────────────────────────────────────────
#  Helpers
# ─────────────────────────────────────────────

_USERNAME_RE = re.compile(r"^[a-z0-9_]{3,20}$")


class ProfileState(rx.State):
    """Manages the full user-profile lifecycle."""

    # ── Own profile ───────────────────────────
    own_email: str = ""
    own_username: str = ""
    own_display_name: str = ""
    own_bio: str = ""
    own_dob: str = ""
    own_location: str = ""
    own_website: str = ""
    own_is_public: bool = True
    own_avatar: str = ""
    own_initials: str = ""
    own_member_since: str = ""
    own_image_count: int = 0

    profile_loaded: bool = False
    onboarding_complete: bool = False

    # ── Onboarding wizard ─────────────────────
    show_onboarding: bool = False
    onboarding_step: int = 1  # 1 | 2 | 3

    # Step form inputs
    username_input: str = ""
    display_name_input: str = ""
    bio_input: str = ""
    dob_input: str = ""
    location_input: str = ""
    website_input: str = ""
    is_public_input: bool = True

    # Validation / loading
    username_error: str = ""
    onboarding_saving: bool = False
    save_error: str = ""

    # ── Viewed public profile ─────────────────
    viewed_username: str = ""
    viewed_display_name: str = ""
    viewed_bio: str = ""
    viewed_location: str = ""
    viewed_website: str = ""
    viewed_avatar: str = ""
    viewed_member_since: str = ""
    viewed_image_count: int = 0
    viewed_images: list[dict] = []
    viewed_not_found: bool = False
    viewed_is_loading: bool = False
    viewed_email: str = ""        # needed for follow operations
    viewed_follower_count: int = 0
    viewed_following_count: int = 0
    
    # ── Viewed Collections ────────────────────
    active_profile_tab: str = "all"   # "all" | "collections"
    viewed_collections: list[dict] = []
    viewed_active_folder: str = ""

    # ── Edit profile modal ───────────────────
    show_edit_profile: bool = False
    edit_username: str = ""
    edit_display_name: str = ""
    edit_bio: str = ""
    edit_location: str = ""
    edit_website: str = ""
    edit_is_public: bool = True
    edit_username_error: str = ""
    edit_saving: bool = False
    edit_save_error: str = ""
    edit_save_success: bool = False

    # ── Viewed Stats ──────────────────────────
    viewed_total_likes: int = 0
    viewed_banner: str = ""

    # ── Avatar/Banner upload ──────────────────
    avatar_uploading: bool = False
    avatar_error: str = ""
    banner_uploading: bool = False
    banner_error: str = ""

    # ── Own data expansion ────────────────────
    own_banner: str = ""

    # ── Search / discovery ───────────────────
    search_query: str = ""
    search_results: list[SearchResult] = []
    image_search_results: list[SemanticImageResult] = []
    search_mode: str = "profiles"  # "profiles" or "images"
    search_loading: bool = False
    search_done: bool = False

    # ── Public profile image lightbox ─────────
    show_viewed_lightbox: bool = False
    viewed_lightbox_filename: str = ""
    viewed_lightbox_caption: str = ""
    viewed_lightbox_index: int = -1
    viewed_lightbox_image_id: int = 0
    viewed_lightbox_like_count: int = 0
    viewed_lightbox_viewer_has_liked: bool = False
    viewed_lightbox_comments: list[dict] = []
    comment_input: str = ""
    comment_loading: bool = False

    # ── Notifications ────────────────────────
    notifications: list[Notification] = []
    unread_notifications_count: int = 0
    show_notifications_dropdown: bool = False

    # ── Suggested Creators ──────────────────
    suggested_creators: list[SearchResult] = []
    suggested_loading: bool = False

    # ── Profile toast ────────────────────────
    profile_toast_visible: bool = False
    profile_toast_message: str = ""

    # ── Computed ──────────────────────────────
    @rx.var
    def viewed_initials(self) -> str:
        name = self.viewed_display_name or self.viewed_username
        parts = name.split()
        if len(parts) >= 2:
            return (parts[0][0] + parts[-1][0]).upper()
        return name[:2].upper() if name else "??"

    @rx.var
    def viewer_is_following(self) -> bool:
        """True if the viewer follows the viewed profile (Accepted)."""
        if not self.own_email or not self.viewed_email: return False
        if self.own_email == self.viewed_email: return False
        with rx.session() as session:
            f = session.exec(
                sqlmodel.select(Follow).where(
                    Follow.follower_email == self.own_email,
                    Follow.following_email == self.viewed_email,
                    Follow.status == "accepted"
                )
            ).first()
            return f is not None

    @rx.var
    def viewer_follow_pending(self) -> bool:
        """True if there is a pending follow request."""
        if not self.own_email or not self.viewed_email: return False
        if self.own_email == self.viewed_email: return False
        with rx.session() as session:
            f = session.exec(
                sqlmodel.select(Follow).where(
                    Follow.follower_email == self.own_email,
                    Follow.following_email == self.viewed_email,
                    Follow.status == "pending"
                )
            ).first()
            return f is not None

    @rx.var
    def username_ok(self) -> bool:
        return bool(_USERNAME_RE.match(self.username_input))

    @rx.var
    def step_title(self) -> str:
        if self.onboarding_step == 1:
            return "Create your identity"
        if self.onboarding_step == 2:
            return "Tell us about yourself"
        if self.onboarding_step == 3:
            return "Personalize your profile"
        return "Privacy & finish"

    @rx.var
    def step_subtitle(self) -> str:
        if self.onboarding_step == 1:
            return "Choose a unique username and how your name appears to others."
        if self.onboarding_step == 2:
            return "Add a bio, your location, and a website (all optional)."
        if self.onboarding_step == 3:
            return "Upload an avatar and a profile banner to stand out."
        return "Control who can see your library, then launch your profile."

    @rx.var
    def own_avatar_url(self) -> str:
        if self.own_avatar:
            return self.backend_url + "/uploaded_files/avatars/" + self.own_avatar
        return ""

    @rx.var
    def viewed_banner_url(self) -> str:
        if self.viewed_banner:
            return self.backend_url + "/uploaded_files/banners/" + self.viewed_banner
        return ""

    @rx.var
    def viewed_avatar_url(self) -> str:
        if self.viewed_avatar:
            return self.backend_url + "/uploaded_files/avatars/" + self.viewed_avatar
        return ""

    @rx.var
    def own_banner_url(self) -> str:
        if self.own_banner:
            return self.backend_url + "/uploaded_files/banners/" + self.own_banner
        return ""

    @rx.var
    def viewed_lightbox_url(self) -> str:
        if self.viewed_lightbox_filename:
            return self.backend_url + "/uploaded_files/" + self.viewed_lightbox_filename
        return ""

    @rx.var
    def viewed_member_since_text(self) -> str:
        if self.viewed_member_since:
            return f"Joined {self.viewed_member_since}"
        return ""

    @rx.var
    def is_guest(self) -> bool:
        """True when the active session is a read-only guest account."""
        return self.own_email == "guest@turkey.app"

    @rx.var
    def is_own_profile(self) -> bool:
        """True when viewing your own public profile."""
        return (
            self.own_email != ""
            and self.viewed_email != ""
            and self.own_email == self.viewed_email
        )

    # ── Follow helpers ────────────────────────

    def _get_viewer_email(self) -> str:
        """Best-effort current user email from own_email or cookie."""
        return self.own_email

    def follow_user(self):
        """Request to follow the currently viewed profile."""
        viewer = self._get_viewer_email()
        if not viewer or not self.viewed_email or viewer == self.viewed_email:
            return
        with rx.session() as session:
            existing = session.exec(
                sqlmodel.select(Follow).where(
                    Follow.follower_email == viewer,
                    Follow.following_email == self.viewed_email,
                )
            ).first()
            if not existing:
                # Create pending follow
                session.add(Follow(
                    follower_email=viewer,
                    following_email=self.viewed_email,
                    status="pending",
                    created_at=datetime.utcnow().strftime("%Y-%m-%d %H:%M:%S"),
                ))
                # Create notification for the recipient
                session.add(Notification(
                    to_email=self.viewed_email,
                    from_email=viewer,
                    from_username=self.own_username,
                    type="follow_request",
                    status="unread",
                    message=f"@{self.own_username} wants to follow you",
                    created_at=datetime.utcnow().strftime("%Y-%m-%d %H:%M:%S"),
                ))
                session.commit()
        self._reload_follow_state()
        self.profile_toast_message = "Follow request sent to @" + self.viewed_username
        self.profile_toast_visible = True


    def unfollow_user(self):
        """Unfollow the currently viewed profile."""
        viewer = self._get_viewer_email()
        if not viewer or not self.viewed_email:
            return
        with rx.session() as session:
            existing = session.exec(
                sqlmodel.select(Follow).where(
                    Follow.follower_email == viewer,
                    Follow.following_email == self.viewed_email,
                )
            ).first()
            if existing:
                session.delete(existing)
                session.commit()
        self._reload_follow_state()
        self.profile_toast_message = "Unfollowed @" + self.viewed_username
        self.profile_toast_visible = True

    def _reload_follow_state(self):
        """Refresh follower/following counts and viewer_is_following."""
        viewer = self._get_viewer_email()
        with rx.session() as session:
            self.viewed_follower_count = session.exec(
                sqlmodel.select(sqlmodel.func.count(Follow.id)).where(
                    Follow.following_email == self.viewed_email,
                    Follow.status == "accepted",
                )
            ).one()
            self.viewed_following_count = session.exec(
                sqlmodel.select(sqlmodel.func.count(Follow.id)).where(
                    Follow.follower_email == self.viewed_email,
                    Follow.status == "accepted",
                )
            ).one()
            # These are now computed rx.vars
            pass

    def dismiss_profile_toast(self):
        self.profile_toast_visible = False

    def set_profile_tab(self, tab: str):
        self.active_profile_tab = tab

    def copy_profile_link(self):
        """Copies the profile URL and shows a toast."""
        url = "https://turkey.app/u/" + self.viewed_username
        self.profile_toast_message = "Profile link copied to clipboard!"
        self.profile_toast_visible = True
        return rx.set_clipboard(url)

    # ── Lifecycle ─────────────────────────────

    def init_profile(self, email: str, google_name: str = ""):
        """Called right after Google OAuth success. Loads or queues onboarding."""
        self.own_email = email
        profile = None
        with rx.session() as session:
            profile = session.exec(
                sqlmodel.select(UserProfile).where(UserProfile.email == email)
            ).first()
            if profile and profile.onboarding_complete:
                # Load everything inside the session so no detached-instance errors
                self._load_from_profile(profile)
                self.onboarding_complete = True
                self.show_onboarding = False
            elif profile:
                # Partial onboarding — prefill what we have
                self.display_name_input = profile.display_name or google_name
                self.username_input = profile.username or ""
                self.onboarding_complete = False
                self.show_onboarding = True
                self.onboarding_step = 1
            else:
                # Brand new user
                self.display_name_input = google_name
                self.onboarding_complete = False
                self.show_onboarding = True
                self.onboarding_step = 1

        self.profile_loaded = True

    def _load_from_profile(self, profile: UserProfile):
        self.own_username = profile.username or ""
        self.own_display_name = profile.display_name or ""
        self.own_bio = profile.bio or ""
        self.own_dob = profile.date_of_birth or ""
        self.own_location = profile.location or ""
        self.own_website = profile.website or ""
        self.own_is_public = profile.is_public
        self.own_avatar = profile.avatar_filename or ""
        self.own_banner = profile.banner_filename or ""
        self.own_member_since = profile.created_at[:7] if profile.created_at else ""
        # Compute initials from display name
        name = profile.display_name or profile.username or ""
        parts = name.split()
        if len(parts) >= 2:
            self.own_initials = (parts[0][0] + parts[-1][0]).upper()
        elif name:
            self.own_initials = name[:2].upper()
        else:
            self.own_initials = "??"

    # ── Edit profile ──────────────────────────

    def open_edit_profile(self):
        """Pre-fill edit form from current own_* state and open the modal."""
        self.edit_username = self.own_username
        self.edit_display_name = self.own_display_name
        self.edit_bio = self.own_bio
        self.edit_location = self.own_location
        self.edit_website = self.own_website
        self.edit_is_public = self.own_is_public
        self.edit_username_error = ""
        self.edit_save_error = ""
        self.edit_save_success = False
        self.show_edit_profile = True

    def close_edit_profile(self):
        self.show_edit_profile = False

    def toggle_edit_profile(self):
        if self.show_edit_profile:
            self.show_edit_profile = False
        else:
            self.open_edit_profile()

    def set_edit_username(self, v: str):
        self.edit_username = v.lower().strip()
        self.edit_username_error = ""

    def set_edit_display_name(self, v: str):
        self.edit_display_name = v

    def set_edit_bio(self, v: str):
        self.edit_bio = v

    def set_edit_location(self, v: str):
        self.edit_location = v

    def set_edit_website(self, v: str):
        self.edit_website = v

    def toggle_edit_is_public(self, v: bool):
        self.edit_is_public = v

    def save_profile_edits(self):
        """Persist the updated profile to DB."""
        username = self.edit_username.strip()
        if not _USERNAME_RE.match(username):
            self.edit_username_error = "3–20 chars, lowercase letters, numbers, underscores only."
            return

        # Uniqueness check (skip if same as current own username)
        if username != self.own_username:
            with rx.session() as session:
                clash = session.exec(
                    sqlmodel.select(UserProfile).where(UserProfile.username == username)
                ).first()
            if clash and clash.email != self.own_email:
                self.edit_username_error = f"@{username} is already taken."
                return

        self.edit_saving = True
        self.edit_save_error = ""
        self.edit_save_success = False
        try:
            with rx.session() as session:
                profile = session.exec(
                    sqlmodel.select(UserProfile).where(UserProfile.email == self.own_email)
                ).first()
                if profile:
                    profile.username = username
                    profile.display_name = self.edit_display_name.strip() or username
                    profile.bio = self.edit_bio.strip()
                    profile.location = self.edit_location.strip()
                    profile.website = self.edit_website.strip()
                    profile.is_public = self.edit_is_public
                    session.add(profile)
                    session.commit()
            # Sync local state
            self.own_username = username
            self.own_display_name = self.edit_display_name.strip() or username
            self.own_bio = self.edit_bio.strip()
            self.own_location = self.edit_location.strip()
            self.own_website = self.edit_website.strip()
            self.own_is_public = self.edit_is_public
            self.edit_save_success = True
        except Exception as exc:
            self.edit_save_error = f"Save failed: {exc}"
        finally:
            self.edit_saving = False

    # ── Avatar upload ─────────────────────────

    async def handle_avatar_upload(self, files: list[rx.UploadFile]):
        """Upload a profile picture and persist the filename."""
        if not files:
            return
        self.avatar_uploading = True
        self.avatar_error = ""
        file = files[0]
        ext = os.path.splitext(file.filename)[1].lower()
        if ext not in (".jpg", ".jpeg", ".png", ".gif", ".webp"):
            self.avatar_error = "Only JPG, PNG, GIF, or WEBP allowed."
            self.avatar_uploading = False
            return
        data = await file.read()
        if len(data) > 5 * 1024 * 1024:
            self.avatar_error = "Avatar must be under 5 MB."
            self.avatar_uploading = False
            return
        filename = f"{uuid.uuid4().hex}{ext}"
        save_path = os.path.join(AVATAR_DIR, filename)
        with open(save_path, "wb") as f:
            f.write(data)
        # Persist to DB
        try:
            with rx.session() as session:
                profile = session.exec(
                    sqlmodel.select(UserProfile).where(UserProfile.email == self.own_email)
                ).first()
                if profile:
                    # Delete old avatar file
                    if profile.avatar_filename:
                        old_path = os.path.join(AVATAR_DIR, profile.avatar_filename)
                        if os.path.exists(old_path):
                            os.remove(old_path)
                    profile.avatar_filename = filename
                    session.add(profile)
                    session.commit()
            self.own_avatar = filename
        except Exception as exc:
            self.avatar_error = f"Upload failed: {exc}"
        finally:
            self.avatar_uploading = False

    async def handle_banner_upload(self, files: list[rx.UploadFile]):
        """Upload a profile banner (wide aspect ratio recommended)."""
        if not files:
            return
        self.banner_uploading = True
        self.banner_error = ""
        file = files[0]
        ext = os.path.splitext(file.filename)[1].lower()
        if ext not in (".jpg", ".jpeg", ".png", ".webp"):
            self.banner_error = "Only JPG, PNG, or WEBP allowed."
            self.banner_uploading = False
            return
        
        # Ensure banners dir exists
        banner_dir = os.path.join("uploaded_files", "banners")
        os.makedirs(banner_dir, exist_ok=True)
        
        data = await file.read()
        if len(data) > 8 * 1024 * 1024:
            self.banner_error = "Banner must be under 8 MB."
            self.banner_uploading = False
            return
        
        filename = f"banner_{uuid.uuid4().hex}{ext}"
        save_path = os.path.join(banner_dir, filename)
        with open(save_path, "wb") as f:
            f.write(data)
            
        try:
            with rx.session() as session:
                profile = session.exec(
                    sqlmodel.select(UserProfile).where(UserProfile.email == self.own_email)
                ).first()
                if profile:
                    # Delete old
                    if profile.banner_filename:
                        old_p = os.path.join(banner_dir, profile.banner_filename)
                        if os.path.exists(old_p):
                            os.remove(old_p)
                    profile.banner_filename = filename
                    session.add(profile)
                    session.commit()
            self.own_banner = filename
            self.profile_toast_message = "Profile banner updated!"
            self.profile_toast_visible = True
        except Exception as e:
            self.banner_error = f"Banner upload failed: {e}"
        finally:
            self.banner_uploading = False

    # ── Search / discovery ────────────────────

    def set_search_query(self, q: str):
        self.search_query = q

    def set_search_mode(self, mode: Union[str, List[str]]):
        # Even if it's a list (unlikely here), we take the first or cast to str
        if isinstance(mode, list):
            self.search_mode = str(mode[0]) if mode else "profiles"
        else:
            self.search_mode = mode
        self.search_done = False
        self.search_results = []
        self.image_search_results = []

    async def run_search(self):
        """Dispatches search based on current mode."""
        if self.search_mode == "images":
            return await self.run_image_search()
        return self.run_profile_search()

    def run_profile_search(self):
        """Search public profiles by username or display name."""
        # Handle query from URL parameters if present
        q_param = self.router.page.params.get("q")
        if q_param:
            self.search_query = q_param

        q = self.search_query.strip().lower()
        if not q:
            self.search_results = []
            self.search_done = False
            return self.load_suggested_creators()
        
        self.search_loading = True
        self.search_results = []
        try:
            with rx.session() as session:
                profiles = session.exec(
                    sqlmodel.select(UserProfile).where(
                        UserProfile.is_public == True,
                        UserProfile.onboarding_complete == True,
                    )
                ).all()
            results = []
            for p in profiles:
                if q in p.username.lower() or q in (p.display_name or "").lower():
                    # Count their images
                    img_count = session.exec(
                        sqlmodel.select(sqlmodel.func.count(ImageRecord.id))
                        .where(ImageRecord.owner_email == p.email)
                    ).one()
                    results.append(SearchResult(
                        username=p.username,
                        display_name=p.display_name or p.username,
                        bio=p.bio or "",
                        location=p.location or "",
                        avatar_url=("avatars/" + p.avatar_filename) if p.avatar_filename else "",
                        full_avatar_url=("/uploaded_files/avatars/" + p.avatar_filename) if p.avatar_filename else "",
                        member_since=p.created_at[:7] if p.created_at else "",
                        image_count=img_count,
                        image_count_str=str(img_count),
                        follower_count=session.exec(
                            sqlmodel.select(sqlmodel.func.count(Follow.id))
                            .where(Follow.following_email == p.email)
                        ).one(),
                    ))
            self.search_results = results
            self.search_done = True
        except Exception:
            self.search_results = []
            self.search_done = True
        finally:
            self.search_loading = False
    async def run_image_search(self):
        """Search public images by caption, filename, or tag — no AI keys needed."""
        import os
        q = self.search_query.strip().lower()
        if not q:
            self.image_search_results = []
            self.search_done = False
            return

        self.search_loading = True
        self.image_search_results = []
        try:
            backend = os.getenv("API_URL", "http://localhost:8000").rstrip("/")
            with rx.session() as session:
                images = session.exec(
                    sqlmodel.select(ImageRecord, UserProfile)
                    .join(UserProfile, ImageRecord.owner_email == UserProfile.email)
                    .where(ImageRecord.is_public == True)
                    .where(UserProfile.onboarding_complete == True)
                    .order_by(ImageRecord.created_at.desc())
                    .limit(200)
                ).all()

                results = []
                for img, user in images:
                    # Match against caption, filename, or username
                    searchable = " ".join([
                        (img.caption or ""),
                        (img.original_filename or ""),
                        (img.filename or ""),
                        (user.username or ""),
                        (user.display_name or ""),
                    ]).lower()

                    if q in searchable:
                        results.append(SemanticImageResult(
                            id=img.id,
                            filename=img.filename,
                            full_url=f"{backend}/uploaded_files/{img.filename}",
                            caption=img.caption or img.original_filename or "",
                            owner_username=user.username,
                        ))

            self.image_search_results = results[:48]  # Cap at 48
            self.search_done = True
        except Exception as e:
            print(f"Image Search Error: {e}")
            self.image_search_results = []
            self.search_done = True
        finally:
            self.search_loading = False

    def load_suggested_creators(self):
        """Load a few active public profiles to show as suggestions."""
        self.suggested_loading = True
        try:
            with rx.session() as session:
                # Get up to 5 random/recent public profiles
                profiles = session.exec(
                    sqlmodel.select(UserProfile).where(
                        UserProfile.is_public == True,
                        UserProfile.onboarding_complete == True,
                        UserProfile.email != self.own_email,
                    ).order_by(UserProfile.created_at.desc()).limit(5)
                ).all()
                results = []
                for p in profiles:
                    img_count = session.exec(
                        sqlmodel.select(sqlmodel.func.count(ImageRecord.id))
                        .where(ImageRecord.owner_email == p.email)
                    ).one()
                    results.append(SearchResult(
                        username=p.username,
                        display_name=p.display_name or p.username,
                        bio=p.bio or "",
                        location=p.location or "",
                        avatar_url=("avatars/" + p.avatar_filename) if p.avatar_filename else "",
                        full_avatar_url=("/uploaded_files/avatars/" + p.avatar_filename) if p.avatar_filename else "",
                        member_since=p.created_at[:7] if p.created_at else "",
                        image_count=img_count,
                        image_count_str=str(img_count),
                        follower_count=session.exec(
                            sqlmodel.select(sqlmodel.func.count(Follow.id))
                            .where(Follow.following_email == p.email)
                        ).one(),
                    ))
                self.suggested_creators = results
        except Exception:
            self.suggested_creators = []
        finally:
            self.suggested_loading = False

    def global_search_submit(self):
        """Called on Enter in the navbar search input."""
        q = self.search_query.strip()
        if not q:
            return
        # If we are already on the search page, just run_search
        if self.router.page.path == "/search":
            return self.run_search()
        # Otherwise, redirect to search page with query param
        return rx.redirect(f"/search?q={q}")

    def clear_profile(self):
        """Called on logout."""
        self.own_email = ""
        self.own_username = ""
        self.own_display_name = ""
        self.own_bio = ""
        self.profile_loaded = False
        self.onboarding_complete = False
        self.show_onboarding = False

    def init_guest(self):
        """Set a minimal guest profile so is_guest == True in the UI."""
        self.own_email = "guest@turkey.app"
        self.own_username = "guest"
        self.own_display_name = "Guest"
        self.profile_loaded = True
        self.onboarding_complete = False

    # ── Notification Actions ──────────────────
    def load_notifications(self):
        """Fetch unread/pending notifications for the current user."""
        if not self.own_email:
            return
        with rx.session() as session:
            self.notifications = session.exec(
                sqlmodel.select(Notification)
                .where(Notification.to_email == self.own_email)
                .order_by(Notification.created_at.desc())
                .limit(20)
            ).all()
            self.unread_notifications_count = sum(1 for n in self.notifications if n.status == "unread")

    def toggle_notifications(self):
        self.show_notifications_dropdown = not self.show_notifications_dropdown
        if self.show_notifications_dropdown:
            self.load_notifications()

    def accept_follow_request(self, notification_id: int):
        """Accept a follow request."""
        with rx.session() as session:
            notif = session.get(Notification, notification_id)
            if notif and notif.to_email == self.own_email:
                # Update follow record
                follow = session.exec(
                    sqlmodel.select(Follow).where(
                        Follow.follower_email == notif.from_email,
                        Follow.following_email == notif.to_email,
                        Follow.status == "pending"
                    )
                ).first()
                if follow:
                    follow.status = "accepted"
                    session.add(follow)
                
                # Mark notification as accepted
                notif.status = "accepted"
                session.add(notif)
                session.commit()
        self.load_notifications()
        self._reload_follow_state()

    def decline_follow_request(self, notification_id: int):
        """Decline a follow request."""
        with rx.session() as session:
            notif = session.get(Notification, notification_id)
            if notif and notif.to_email == self.own_email:
                # Delete follow record
                follow = session.exec(
                    sqlmodel.select(Follow).where(
                        Follow.follower_email == notif.from_email,
                        Follow.following_email == notif.to_email,
                        Follow.status == "pending"
                    )
                ).first()
                if follow:
                    session.delete(follow)
                
                # Mark notification as declined
                notif.status = "declined"
                session.add(notif)
                session.commit()
        self.load_notifications()
        self._reload_follow_state()

    # ── Onboarding setters ────────────────────

    def set_username_input(self, val: str):
        self.username_input = val.lower().strip()
        self.username_error = ""

    def set_display_name_input(self, val: str):
        self.display_name_input = val

    def set_bio_input(self, val: str):
        self.bio_input = val

    def set_dob_input(self, val: str):
        self.dob_input = val

    def set_location_input(self, val: str):
        self.location_input = val

    def set_website_input(self, val: str):
        self.website_input = val

    def toggle_is_public(self, val: bool):
        self.is_public_input = val

    # ── Onboarding navigation ─────────────────

    def next_step(self):
        if self.onboarding_step == 1:
            username = self.username_input.strip()
            if not _USERNAME_RE.match(username):
                self.username_error = (
                    "3–20 chars, lowercase letters, numbers, and underscores only."
                )
                return
            # Check uniqueness
            with rx.session() as session:
                clash = session.exec(
                    sqlmodel.select(UserProfile).where(
                        UserProfile.username == username
                    )
                ).first()
            if clash and clash.email != self.own_email:
                self.username_error = f"@{username} is already taken — try another."
                return
            self.onboarding_step = 2
        elif self.onboarding_step == 2:
            self.onboarding_step = 3
        elif self.onboarding_step == 3:
            self.onboarding_step = 4

    def prev_step(self):
        if self.onboarding_step > 1:
            self.onboarding_step -= 1

    def complete_onboarding(self):
        """Persist profile and mark setup as done."""
        self.onboarding_saving = True
        self.save_error = ""
        now = datetime.utcnow().strftime("%Y-%m-%d %H:%M:%S")

        try:
            with rx.session() as session:
                existing = session.exec(
                    sqlmodel.select(UserProfile).where(
                        UserProfile.email == self.own_email
                    )
                ).first()

                display = self.display_name_input.strip() or self.username_input

                if existing:
                    existing.username = self.username_input.strip()
                    existing.display_name = display
                    existing.bio = self.bio_input.strip()
                    existing.date_of_birth = self.dob_input
                    existing.location = self.location_input.strip()
                    existing.website = self.website_input.strip()
                    existing.is_public = self.is_public_input
                    existing.onboarding_complete = True
                    existing.avatar_filename = self.own_avatar
                    existing.banner_filename = self.own_banner
                    session.add(existing)
                else:
                    session.add(UserProfile(
                        email=self.own_email,
                        username=self.username_input.strip(),
                        display_name=display,
                        bio=self.bio_input.strip(),
                        date_of_birth=self.dob_input,
                        location=self.location_input.strip(),
                        website=self.website_input.strip(),
                        is_public=self.is_public_input,
                        created_at=now,
                        onboarding_complete=True,
                        avatar_filename=self.own_avatar,
                        banner_filename=self.own_banner,
                    ))
                session.commit()

            # Update own-profile vars
            self.own_username = self.username_input.strip()
            self.own_display_name = display
            self.own_bio = self.bio_input.strip()
            self.own_dob = self.dob_input
            self.own_location = self.location_input.strip()
            self.own_website = self.website_input.strip()
            self.own_is_public = self.is_public_input
            self.own_member_since = now[:7]
            self.onboarding_complete = True
            self.show_onboarding = False
        except Exception as exc:
            self.save_error = f"Save failed: {exc}"
        finally:
            self.onboarding_saving = False

    # ── Public profile viewer ─────────────────

    def load_public_profile(self):
        """Called on_load of the /u/[username] page — reads route param."""
        username = self.router.page.params.get("username", "")
        self.viewed_username = username
        self.viewed_not_found = False
        self.viewed_is_loading = True
        self.viewed_images = []
        self.viewed_email = ""
        self.viewed_active_folder = self.router.page.params.get("folder", "")
        self.viewed_follower_count = 0
        self.viewed_following_count = 0
        self.viewer_is_following = False

        with rx.session() as session:
            profile = session.exec(
                sqlmodel.select(UserProfile).where(
                    UserProfile.username == username
                )
            ).first()

            if not profile or not profile.onboarding_complete:
                self.viewed_not_found = True
                self.viewed_is_loading = False
                return

            if not profile.is_public:
                self.viewed_not_found = True
                self.viewed_is_loading = False
                return

            self.viewed_email = profile.email
            self.viewed_display_name = profile.display_name
            self.viewed_bio = profile.bio
            self.viewed_location = profile.location
            self.viewed_website = profile.website
            self.viewed_avatar = profile.avatar_filename
            self.viewed_banner = profile.banner_filename
            self.viewed_member_since = profile.created_at[:7] if profile.created_at else ""

            query = sqlmodel.select(ImageRecord).where(
                ImageRecord.owner_email == profile.email,
                ImageRecord.is_public == True,
            )
            if self.viewed_active_folder:
                query = query.where(ImageRecord.folder_name == self.viewed_active_folder)
            
            images = session.exec(
                query.order_by(ImageRecord.created_at.desc()).limit(60)
            ).all()
            import os, urllib.parse as _up
            _backend = os.getenv("API_URL", "http://localhost:8000").rstrip("/")
            self.viewed_images = [
                {
                    "filename": img.filename,
                    "url": img.cdn_url if img.cdn_url else f"{_backend}/uploaded_files/{_up.quote(img.filename or '', safe='')}",
                    "original_filename": img.original_filename,
                    "folder_name": img.folder_name,
                    "caption": img.caption,
                    "image_id": img.id or 0,
                }
                for img in images
            ]
            self.viewed_image_count = len(self.viewed_images)

            # Calculate total likes across all their images
            image_ids = [img["image_id"] for img in self.viewed_images]
            if image_ids:
                self.viewed_total_likes = session.exec(
                    sqlmodel.select(sqlmodel.func.count(Like.id))
                    .where(Like.image_id.in_(image_ids))
                ).one()
            else:
                self.viewed_total_likes = 0

            # Load public collections
            from TurkeyApp.models import Folder
            colls = session.exec(
                sqlmodel.select(Folder).where(
                    Folder.owner_email == self.viewed_email,
                    Folder.is_public == True,
                )
            ).all()
            self.viewed_collections = []
            for c in colls:
                # Get a cover image
                cover_img = session.exec(
                    sqlmodel.select(ImageRecord).where(
                        ImageRecord.owner_email == self.viewed_email,
                        ImageRecord.folder_name == c.name,
                        ImageRecord.is_public == True,
                    ).limit(1)
                ).first()
                count = session.exec(
                    sqlmodel.select(sqlmodel.func.count(ImageRecord.id)).where(
                        ImageRecord.owner_email == self.viewed_email,
                        ImageRecord.folder_name == c.name,
                        ImageRecord.is_public == True,
                    )
                ).one()
                cover_url = ""
                if cover_img:
                    cover_url = cover_img.cdn_url if cover_img.cdn_url else f"{_backend}/uploaded_files/{_up.quote(cover_img.filename or '', safe='')}"
                self.viewed_collections.append({
                    "name": c.name,
                    "description": c.description,
                    "cover": cover_img.filename if cover_img else "",
                    "cover_url": cover_url,
                    "count": count,
                    "count_text": f"{count} items",
                })

        self.viewed_is_loading = False
        self._reload_follow_state()

    def set_profile_tab(self, tab: str):
        self.active_profile_tab = tab

    # ── Public profile lightbox ───────────────

    def _load_lightbox_data(self, image_id: int):
        """Refresh like count, viewer_has_liked, and comments for lightbox."""
        viewer = self._get_viewer_email()
        with rx.session() as session:
            # Likes
            self.viewed_lightbox_like_count = session.exec(
                sqlmodel.select(sqlmodel.func.count(Like.id))
                .where(Like.image_id == image_id)
            ).one()
            if viewer:
                self.viewed_lightbox_viewer_has_liked = session.exec(
                    sqlmodel.select(Like).where(
                        Like.liker_email == viewer, Like.image_id == image_id
                    )
                ).first() is not None
            else:
                self.viewed_lightbox_viewer_has_liked = False

            # Comments
            comments = session.exec(
                sqlmodel.select(Comment).where(Comment.image_id == image_id)
                .order_by(Comment.created_at.desc())
            ).all()
            self.viewed_lightbox_comments = [
                {
                    "id": c.id,
                    "author_email": c.author_email,
                    "author_username": c.author_username,
                    "text": c.text,
                    "created_at": c.created_at,
                    "is_own": c.author_email == viewer
                }
                for c in comments
            ]

    def open_viewed_image(self, payload: dict):
        """Open a public-profile gallery image in a lightbox."""
        index = payload.get("index", 0)
        if 0 <= index < len(self.viewed_images):
            img = self.viewed_images[index]
            self.viewed_lightbox_filename = img.get("filename", "")
            self.viewed_lightbox_caption = img.get("caption", "") or ""
            self.viewed_lightbox_image_id = img.get("image_id", 0)
            self.viewed_lightbox_index = index
            self.show_viewed_lightbox = True
            self._load_lightbox_data(self.viewed_lightbox_image_id)

    def close_viewed_lightbox(self):
        self.show_viewed_lightbox = False
        self.viewed_lightbox_filename = ""
        self.viewed_lightbox_index = -1

    def prev_viewed_image(self):
        idx = self.viewed_lightbox_index - 1
        if idx >= 0:
            img = self.viewed_images[idx]
            self.viewed_lightbox_filename = img.get("filename", "")
            self.viewed_lightbox_caption = img.get("caption", "") or ""
            self.viewed_lightbox_image_id = img.get("image_id", 0)
            self.viewed_lightbox_index = idx
            self._load_lightbox_data(self.viewed_lightbox_image_id)

    def next_viewed_image(self):
        idx = self.viewed_lightbox_index + 1
        if idx < len(self.viewed_images):
            img = self.viewed_images[idx]
            self.viewed_lightbox_filename = img.get("filename", "")
            self.viewed_lightbox_caption = img.get("caption", "") or ""
            self.viewed_lightbox_image_id = img.get("image_id", 0)
            self.viewed_lightbox_index = idx
            self._load_lightbox_data(self.viewed_lightbox_image_id)

    def toggle_profile_like(self):
        """Like/unlike the image currently open in the profile lightbox."""
        viewer = self._get_viewer_email()
        image_id = self.viewed_lightbox_image_id
        if not viewer or image_id == 0:
            return
        with rx.session() as session:
            existing = session.exec(
                sqlmodel.select(Like).where(
                    Like.liker_email == viewer,
                    Like.image_id == image_id,
                )
            ).first()
            if existing:
                session.delete(existing)
                session.commit()
            else:
                session.add(Like(
                    liker_email=viewer,
                    image_id=image_id,
                    created_at=datetime.utcnow().strftime("%Y-%m-%d"),
                ))
                session.commit()
        self._load_lightbox_data(image_id)

    def add_comment(self):
        """Add a comment to the current photo."""
        viewer = self._get_viewer_email()
        image_id = self.viewed_lightbox_image_id
        text = self.comment_input.strip()
        if not viewer or not text or image_id == 0:
            return
        
        self.comment_loading = True
        try:
            with rx.session() as session:
                new_comment = Comment(
                    image_id=image_id,
                    author_email=viewer,
                    author_username=self.own_username,
                    text=text,
                    created_at=datetime.utcnow().strftime("%Y-%m-%d %H:%M"),
                )
                session.add(new_comment)
                
                # Notify owner if it's not them
                if self.viewed_email != viewer:
                    session.add(Notification(
                        to_email=self.viewed_email,
                        from_email=viewer,
                        from_username=self.own_username,
                        type="comment",
                        message=f"@{self.own_username} commented: {text[:20]}...",
                        created_at=datetime.utcnow().strftime("%Y-%m-%d %H:%M:%S"),
                    ))
                session.commit()
            self.comment_input = ""
            self._load_lightbox_data(image_id)
        finally:
            self.comment_loading = False

    def delete_comment(self, comment_id: int):
        """Delete a comment if you are the author or the photo owner."""
        viewer = self._get_viewer_email()
        if not viewer: return
        with rx.session() as session:
            comment = session.get(Comment, comment_id)
            if comment and (comment.author_email == viewer or self.viewed_email == viewer):
                session.delete(comment)
                session.commit()
        self._load_lightbox_data(self.viewed_lightbox_image_id)

    @rx.var
    def viewed_lightbox_has_prev(self) -> bool:
        return self.viewed_lightbox_index > 0

    @rx.var
    def viewed_lightbox_has_next(self) -> bool:
        return self.viewed_lightbox_index < len(self.viewed_images) - 1

    def copy_image_link(self):
        """Direct link to the currently viewed image in the lightbox."""
        if not self.viewed_lightbox_filename: return
        url = "/uploaded_files/" + self.viewed_lightbox_filename
        # Using a full site URL would be better but let's stick to the upload URL for now
        # especially since they don't have a permalink page yet.
        # Alternatively, we could link to the user's profile with an anchor or param.
        profile_url = f"https://turkey.app/u/{self.viewed_username}?img={self.viewed_lightbox_image_id}"
        self.profile_toast_message = "Direct image link copied!"
        self.profile_toast_visible = True
        return rx.set_clipboard(profile_url)

    # ── Notifications Management ────────────────
    def toggle_notifications(self):
        self.show_notifications_dropdown = not self.show_notifications_dropdown
        if self.show_notifications_dropdown:
            return self.load_notifications()

    def accept_follow_request(self, notification_id: int):
        with rx.session() as session:
            notif = session.get(Notification, notification_id)
            if notif and notif.type == "follow_request":
                # Update follow record
                follow = session.exec(
                    sqlmodel.select(Follow).where(
                        Follow.follower_email == notif.from_email,
                        Follow.following_email == self.own_email
                    )
                ).first()
                if follow:
                    follow.status = "accepted"
                    session.add(follow)
                
                # Mark notification as read or accepted
                notif.status = "accepted"
                session.add(notif)
                session.commit()
        return self.load_notifications()

    def decline_follow_request(self, notification_id: int):
        with rx.session() as session:
            notif = session.get(Notification, notification_id)
            if notif and notif.type == "follow_request":
                # Delete follow record
                follow = session.exec(
                    sqlmodel.select(Follow).where(
                        Follow.follower_email == notif.from_email,
                        Follow.following_email == self.own_email
                    )
                ).first()
                if follow:
                    session.delete(follow)
                
                # Mark notification as Declined
                notif.status = "declined"
                session.add(notif)
                session.commit()
        self.load_notifications()

    def goto_profile(self, username: str):
        """Server-side redirect to a user profile."""
        return rx.redirect(f"/u/{username}")

    def goto_collection(self, username: str, folder_name: str):
        """Redirect to a specific collection (folder) on a user's profile."""
        return rx.redirect(f"/u/{username}?folder={folder_name}")

    def clear_collection_filter(self):
        """Clear the folder filter and show all public photos."""
        return rx.redirect(f"/u/{self.viewed_username}")
