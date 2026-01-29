"""Entrypoint: run the agent as an aiohttp server (POST /api/messages)."""

import asyncio
import logging
import os

from aiohttp import web

from meeting_agent.app import get_app_and_adapter
from meeting_agent.config import load_config
from microsoft_agents.hosting.aiohttp import start_agent_process

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(name)s: %(message)s",
)
logger = logging.getLogger(__name__)


async def handle_messages(request: web.Request) -> web.Response:
    """Handle POST /api/messages: run the agent with CloudAdapter."""
    app, adapter = get_app_and_adapter()
    response = await start_agent_process(request, app, adapter)
    if response is None:
        return web.Response(status=500, text="Agent process returned None")
    return response


def create_app() -> web.Application:
    """Create aiohttp Application with /api/messages route."""
    app = web.Application()
    app.router.add_post("/api/messages", handle_messages)
    return app


def main() -> None:
    """Run the aiohttp server."""
    config = load_config(os.environ)
    port = config.port
    app = create_app()
    logger.info("Starting agent server on port %s (POST /api/messages)", port)
    web.run_app(app, host="0.0.0.0", port=port)


if __name__ == "__main__":
    main()
