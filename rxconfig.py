import reflex as rx

# Tells the server what the app is called and what plugins to use. 
# The plugins are used to add functionality to the app, such as generating a sitemap or using Tailwind CSS for styling.
config = rx.Config(
    app_name="TurkeyApp",
    plugins=[
        rx.plugins.SitemapPlugin(),
        rx.plugins.TailwindV4Plugin(),
    ],
    google_client_id="1094236817168-v8jhd5m0nke2dn68tjdjag9t0nto1pep.apps.googleusercontent.com",
    upload_dir="assets/uploaded_files",
    upload_url="/uploaded_files",
    # Uncomment api_url only when deploying to Lightning.ai CloudSpaces:
    # api_url="https://8000-sorry-ivory-n6ug.cloudspaces.litng.ai",
)
