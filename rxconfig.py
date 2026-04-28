import reflex as rx
import os

config = rx.Config(
    app_name="TurkeyApp",
    plugins=[
        rx.plugins.SitemapPlugin(),
        rx.plugins.TailwindV4Plugin(),
    ],
    google_client_id="1094236817168-v8jhd5m0nke2dn68tjdjag9t0nto1pep.apps.googleusercontent.com",
    upload_dir="assets/uploaded_files",
    upload_url="/uploaded_files",
    # Only override API URL for self-hosted deployments (e.g. Render).
    # On Reflex Cloud, leave unset so it auto-configures.
    **({"api_url": os.environ["API_URL"]} if "API_URL" in os.environ else {}),
)
