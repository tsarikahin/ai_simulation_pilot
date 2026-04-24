"""Entry point for the SimCopilot API server."""

import uvicorn

from src.api.main import create_app, settings

app = create_app()

if __name__ == "__main__":
    uvicorn.run(
        "src.main:app",
        host=settings.api_settings.api_host,
        port=settings.api_settings.api_port,
        reload=settings.api_settings.api_debug
    )

