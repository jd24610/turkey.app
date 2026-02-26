"""Wrappers for @react-oauth/google components."""

import reflex as rx
from typing import Any


class GoogleOAuthProvider(rx.Component):
    """Provides the Google OAuth context to child components."""

    library = "@react-oauth/google"
    tag = "GoogleOAuthProvider"

    client_id: rx.Var[str]
    


class GoogleLogin(rx.Component):
    """The Google Sign-In button component."""

    library = "@react-oauth/google"
    tag = "GoogleLogin"

    on_success: rx.EventHandler[lambda credential_response: [credential_response]]
    on_error: rx.EventHandler[lambda: []]


google_oauth_provider = GoogleOAuthProvider.create
google_login = GoogleLogin.create



