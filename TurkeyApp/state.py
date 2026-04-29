import reflex as rx
from TurkeyApp.upload_state import UploadState
from TurkeyApp.profile_state import ProfileState

class State(rx.State):
    """The app state - extracted to resolve circular imports."""
    
    @rx.var
    def backend_url(self) -> str:
        from rxconfig import config
        # Use the configured API URL, stripping any trailing /api
        url = config.api_url
        if url.endswith("/"):
            url = url[:-1]
        return url

    id_token_json: str = ""
    user_email: str = ""
    user_name: str = ""

    # ── Session persistence via cookie ────────
    session_email: str = rx.Cookie(name="turkey_email", max_age=604800)  # 7 days
    session_name: str = rx.Cookie(name="turkey_name", max_age=604800)

    GUEST_EMAIL: str = "guest@turkey.app"

    @rx.var
    def is_authenticated(self) -> bool:
        return bool(self.id_token_json) or bool(self.session_email)

    @rx.var
    def is_guest(self) -> bool:
        """True when the session is a temporary guest (not a real Google account)."""
        return self.session_email == "guest@turkey.app" or self.user_email == "guest@turkey.app"

    def on_app_load(self):
        """Called on every page load — restores session from cookie if present."""
        if self.session_email and not self.id_token_json:
            self.user_email = self.session_email
            self.user_name = self.session_name
            yield UploadState.set_user_email(self.session_email)
            yield UploadState.set_user_name(self.session_name)
            yield ProfileState.init_profile(self.session_email, self.session_name)
            yield UploadState.on_load  # Restore image library from DB

    def on_success(self, id_token: dict):
        self.id_token_json = str(id_token)
        cred = id_token.get("credential", "")

        # ── Step 1: Decode JWT payload ─────────────────────────────────────
        email = ""
        name = ""
        try:
            import base64, json as _json
            parts = cred.split(".")
            if len(parts) >= 2:
                payload = parts[1]
                payload += "=" * (4 - len(payload) % 4)
                data = _json.loads(base64.b64decode(payload).decode("utf-8"))
                email = data.get("email", "")
                name = data.get("name", "")
        except Exception as e:
            print(f"[turkey] JWT decode error: {e}")

        # ── Step 2: If we couldn't decode, bail out visibly ────────────────
        if not email:
            print("[turkey] on_success: no email found in token — aborting login")
            return

        # ── Step 3: Persist session state ──────────────────────────────────
        self.user_email = email
        self.user_name = name
        self.session_email = email
        self.session_name = name

        # ── Step 4: Propagate to sub-states ────────────────────────────────
        yield UploadState.set_user_email(email)
        yield UploadState.set_user_name(name)

        # ── Step 5: Profile init (non-blocking — redirect happens regardless)
        try:
            yield ProfileState.init_profile(email, name)
        except Exception as e:
            print(f"[turkey] ProfileState.init_profile error: {e}")

        # ── Step 6: Always redirect to the library ─────────────────────────
        yield rx.redirect("/library")

    def login_as_guest(self):
        """Set a read-only guest session and go to the feed."""
        guest_email = "guest@turkey.app"
        guest_name = "Guest"
        self.user_email = guest_email
        self.user_name = guest_name
        self.session_email = guest_email
        self.session_name = guest_name
        yield UploadState.set_user_email(guest_email)
        yield UploadState.set_user_name(guest_name)
        yield ProfileState.init_guest()
        yield rx.redirect("/feed")

    def logout(self):
        """Clear session and redirect to home."""
        self.id_token_json = ""
        self.session_email = ""
        self.session_name = ""
        self.user_email = ""
        self.user_name = ""
        yield UploadState.set_user_email("")
        yield UploadState.set_user_name("")
        yield ProfileState.clear_profile()
        yield rx.redirect("/")
