"""ProfileState — manages user onboarding, own-profile data, and public profile viewing."""

import re
import os
import uuid
import reflex as rx
import sqlmodel
from datetime import datetime
from pydantic import BaseModel

from TurkeyApp.models import UserProfile, ImageRecord, Follow

AVATAR_DIR = os.path.join("uploaded_files", "avatars")
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
    avatar_url: str = ""    # full upload path e.g. "avatars/abc123.jpg"
    member_since: str = ""
    image_count: int = 0
    image_count_str: str = "0"


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
    viewer_is_following: bool = False   # does the logged-in user follow this profile?

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

    # ── Avatar upload ─────────────────────────
    avatar_uploading: bool = False
    avatar_error: str = ""

    # ── Search / discovery ───────────────────
    search_query: str = ""
    search_results: list[SearchResult] = []
    search_loading: bool = False
    search_done: bool = False

    # ── Computed ──────────────────────────────
    @rx.var
    def own_initials(self) -> str:
        name = self.own_display_name or self.own_username
        parts = name.split()
        if len(parts) >= 2:
            return (parts[0][0] + parts[-1][0]).upper()
        return name[:2].upper() if name else "??"

    @rx.var
    def viewed_initials(self) -> str:
        name = self.viewed_display_name or self.viewed_username
        parts = name.split()
        if len(parts) >= 2:
            return (parts[0][0] + parts[-1][0]).upper()
        return name[:2].upper() if name else "??"

    @rx.var
    def username_ok(self) -> bool:
        return bool(_USERNAME_RE.match(self.username_input))

    @rx.var
    def step_title(self) -> str:
        if self.onboarding_step == 1:
            return "Create your identity"
        if self.onboarding_step == 2:
            return "Tell us about yourself"
        return "Privacy & finish"

    @rx.var
    def step_subtitle(self) -> str:
        if self.onboarding_step == 1:
            return "Choose a unique username and how your name appears to others."
        if self.onboarding_step == 2:
            return "Add a bio, your location, and a website (all optional)."
        return "Control who can see your library, then launch your profile."

    @rx.var
    def own_avatar_url(self) -> str:
        if self.own_avatar:
            return rx.get_upload_url("avatars/" + self.own_avatar)
        return ""

    @rx.var
    def viewed_avatar_url(self) -> str:
        if self.viewed_avatar:
            return rx.get_upload_url("avatars/" + self.viewed_avatar)
        return ""

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
        """Follow the currently viewed profile."""
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
                session.add(Follow(
                    follower_email=viewer,
                    following_email=self.viewed_email,
                    created_at=datetime.utcnow().strftime("%Y-%m-%d"),
                ))
                session.commit()
        self._reload_follow_state()

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

    def _reload_follow_state(self):
        """Refresh follower/following counts and viewer_is_following."""
        viewer = self._get_viewer_email()
        with rx.session() as session:
            self.viewed_follower_count = session.exec(
                sqlmodel.select(sqlmodel.func.count(Follow.id)).where(
                    Follow.following_email == self.viewed_email
                )
            ).one()
            self.viewed_following_count = session.exec(
                sqlmodel.select(sqlmodel.func.count(Follow.id)).where(
                    Follow.follower_email == self.viewed_email
                )
            ).one()
            if viewer and viewer != self.viewed_email:
                link = session.exec(
                    sqlmodel.select(Follow).where(
                        Follow.follower_email == viewer,
                        Follow.following_email == self.viewed_email,
                    )
                ).first()
                self.viewer_is_following = link is not None
            else:
                self.viewer_is_following = False

    # ── Lifecycle ─────────────────────────────

    def init_profile(self, email: str, google_name: str = ""):
        """Called right after Google OAuth success. Loads or queues onboarding."""
        self.own_email = email
        with rx.session() as session:
            profile = session.exec(
                sqlmodel.select(UserProfile).where(UserProfile.email == email)
            ).first()

        if profile and profile.onboarding_complete:
            self._load_from_profile(profile)
            self.onboarding_complete = True
            self.show_onboarding = False
        else:
            # New user — prefill display name from Google
            self.display_name_input = google_name
            self.onboarding_complete = False
            self.show_onboarding = True
            self.onboarding_step = 1

        self.profile_loaded = True

    def _load_from_profile(self, profile: UserProfile):
        self.own_username = profile.username
        self.own_display_name = profile.display_name
        self.own_bio = profile.bio
        self.own_dob = profile.date_of_birth
        self.own_location = profile.location
        self.own_website = profile.website
        self.own_is_public = profile.is_public
        self.own_avatar = profile.avatar_filename
        self.own_member_since = profile.created_at[:7] if profile.created_at else ""

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

    # ── Search / discovery ────────────────────

    def set_search_query(self, q: str):
        self.search_query = q

    def run_search(self):
        """Search public profiles by username or display name."""
        q = self.search_query.strip().lower()
        if not q:
            self.search_results = []
            self.search_done = False
            return
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
                    with rx.session() as session:
                        img_count = len(session.exec(
                            sqlmodel.select(ImageRecord).where(ImageRecord.owner_email == p.email)
                        ).all())
                    results.append(SearchResult(
                        username=p.username,
                        display_name=p.display_name or p.username,
                        bio=p.bio or "",
                        location=p.location or "",
                        avatar_url=("avatars/" + p.avatar_filename) if p.avatar_filename else "",
                        member_since=p.created_at[:7] if p.created_at else "",
                        image_count=img_count,
                        image_count_str=str(img_count),
                    ))
            self.search_results = results
            self.search_done = True
        except Exception:
            self.search_results = []
            self.search_done = True
        finally:
            self.search_loading = False

    def clear_profile(self):
        """Called on logout."""
        self.own_email = ""
        self.own_username = ""
        self.own_display_name = ""
        self.own_bio = ""
        self.profile_loaded = False
        self.onboarding_complete = False
        self.show_onboarding = False

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
            self.viewed_member_since = profile.created_at[:7] if profile.created_at else ""

            # Load public images only
            images = session.exec(
                sqlmodel.select(ImageRecord)
                .where(
                    ImageRecord.owner_email == profile.email,
                    ImageRecord.is_public == True,
                )
                .order_by(ImageRecord.created_at.desc())
                .limit(60)
            ).all()
            self.viewed_images = [
                {
                    "filename": img.filename,
                    "original_filename": img.original_filename,
                    "folder_name": img.folder_name,
                    "caption": img.caption,
                }
                for img in images
            ]
            self.viewed_image_count = len(self.viewed_images)

        self.viewed_is_loading = False
        self._reload_follow_state()
