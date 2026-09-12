import reflex as rx

config = rx.Config(
    app_name="app",
    plugins=[
        rx.plugins.TailwindV3Plugin(
            config={
                "theme": {
                    "extend": {
                        "colors": {
                            "cream": {
                                "50": "#fdfcfb",
                                "100": "#faf8f5",
                                "200": "#f5f0eb",
                            }
                        }
                    }
                }
            }
        )
    ],
    # Hide the sticky "Built with Reflex" badge from every page.
    show_built_with_reflex=False,
    # Opt out of Reflex usage telemetry.
    telemetry_enabled=False,
    # Silence the sitemap plugin warning (not used by this app).
    disable_plugins=["reflex.plugins.sitemap.SitemapPlugin"],
    # The FastAPI layer (app.api) is mounted INSIDE the Reflex server via
    # api_transformer (see app.py), so the UI and API share one origin/port.
    # Same-origin UI needs no extra CORS origins; list API origins only when
    # consuming the REST API cross-origin (comma-separated in CORS_ORIGINS).
    cors_allowed_origins=[
        origin.strip()
        for origin in __import__("os").getenv(
            "CORS_ORIGINS", "http://localhost:3000"
        ).split(",")
        if origin.strip()
    ],
)
