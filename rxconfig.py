import reflex as rx

# Tells the server what the app is called and what plugins to use. 
# The plugins are used to add functionality to the app, such as generating a sitemap or using Tailwind CSS for styling.
config = rx.Config(
    app_name="TurkeyApp",
    plugins=[
        rx.plugins.SitemapPlugin(),
        rx.plugins.TailwindV4Plugin(),
    ]
)