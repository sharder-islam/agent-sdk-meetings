"""M365 Agents SDK application: AgentApplication, adapter, and message handler."""

import logging
import os
from pathlib import Path
from typing import Any

from microsoft_agents.hosting.core import (
    AgentApplication,
    ApplicationOptions,
    Authorization,
    MemoryStorage,
    RestChannelServiceClientFactory,
    TurnState,
)
from microsoft_agents.hosting.core.turn_context import TurnContext
from microsoft_agents.hosting.aiohttp import CloudAdapter, start_agent_process
from microsoft_agents.authentication.msal import MsalConnectionManager

from meeting_agent.config import load_config, Config
from meeting_agent.auth import GraphAuth
from meeting_agent.graph_client import GraphTranscriptClient
from meeting_agent.summarizer import TranscriptSummarizer

logger = logging.getLogger(__name__)

# Lazy-initialized services (Graph client, summarizer)
_graph_client: GraphTranscriptClient | None = None
_summarizer: TranscriptSummarizer | None = None


def _ensure_services(config: Config) -> tuple[GraphTranscriptClient, TranscriptSummarizer]:
    global _graph_client, _summarizer
    if _graph_client is None:
        auth = GraphAuth(config)
        _graph_client = GraphTranscriptClient(config, auth)
    if _summarizer is None:
        _summarizer = TranscriptSummarizer(config)
    return _graph_client, _summarizer


def _build_connections_config(config: Config) -> dict[str, Any]:
    """Build CONNECTIONS config for MsalConnectionManager (Bot Framework auth)."""
    return {
        "CONNECTIONS": {
            "SERVICE_CONNECTION": {
                "SETTINGS": {
                    "CLIENTID": config.microsoft_app_id,
                    "TENANTID": config.tenant_id,
                    "CLIENTSECRET": config.microsoft_app_password,
                    "AUTHORITY": config.authority,
                }
            }
        }
    }


def _create_app_and_adapter() -> tuple[AgentApplication[TurnState], CloudAdapter]:
    """Create AgentApplication and CloudAdapter for the aiohttp server."""
    config = load_config(os.environ)
    agents_config = _build_connections_config(config)
    connection_manager = MsalConnectionManager(**agents_config)
    channel_factory = RestChannelServiceClientFactory(connection_manager)
    adapter = CloudAdapter(
        connection_manager=connection_manager,
        channel_service_client_factory=channel_factory,
    )
    storage = MemoryStorage()
    authorization = Authorization(storage=storage, connection_manager=connection_manager)
    options = ApplicationOptions(
        bot_app_id=config.microsoft_app_id,
        storage=storage,
    )
    app = AgentApplication[TurnState](
        options=options,
        connection_manager=connection_manager,
        authorization=authorization,
        **agents_config.get("AGENTAPPLICATION", {}),
    )

    @app.activity("message")
    async def on_message(context: TurnContext, state: TurnState) -> bool:
        """Handle message: fetch transcripts and summarize, or echo help."""
        text = (context.activity.text or "").strip().lower()
        if not text:
            await context.send_activity(
                "Send 'summary' or 'summarize' to get meeting summaries for the last configured days."
            )
            return True
        if "summary" in text or "summarize" in text:
            user_id = config.meeting_organizer_user_id
            if not user_id:
                await context.send_activity(
                    "Meeting organizer user ID is not configured (MEETING_ORGANIZER_USER_ID). "
                    "Please set it in configuration to fetch your meeting transcripts."
                )
                return True
            try:
                await context.send_activity("Fetching meeting transcripts and generating summary...")
                graph_client, summarizer = _ensure_services(config)
                transcripts = graph_client.fetch_transcripts_for_user(user_id)
                try:
                    output_dir = str(Path(__file__).resolve().parents[2] / "output")
                except Exception:
                    output_dir = "output"
                summary = summarizer.summarize_transcripts(
                    transcripts, combined=True, output_dir=output_dir
                )
                reply = summary[:4000] + "..." if len(summary) > 4000 else summary
                await context.send_activity(reply)
            except Exception as e:
                logger.exception("Transcript/summary error: %s", e)
                await context.send_activity(f"Error: {e}")
            return True
        await context.send_activity("Send 'summary' or 'summarize' to get meeting summaries.")
        return True

    @app.error
    async def on_error(context: TurnContext, error: Exception) -> None:
        logger.exception("Agent error: %s", error)
        await context.send_activity("The bot encountered an error. Please try again.")

    return app, adapter


def get_app_and_adapter() -> tuple[AgentApplication[TurnState], CloudAdapter]:
    """Return (AgentApplication, CloudAdapter) for the aiohttp server."""
    return _create_app_and_adapter()
