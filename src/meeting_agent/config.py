"""Configuration from environment."""

import os
from dataclasses import dataclass
from datetime import datetime, timedelta, timezone


@dataclass
class Config:
    """Application configuration from env."""

    # Entra / Graph
    tenant_id: str
    client_id: str
    client_secret: str
    authority: str

    # Bot (same app)
    microsoft_app_id: str
    microsoft_app_password: str

    # Transcript window (days)
    transcript_days: int

    # Azure OpenAI
    azure_openai_endpoint: str
    azure_openai_api_key: str
    azure_openai_deployment: str
    azure_openai_api_version: str

    # Server
    port: int

    # Optional: default organizer user ID for transcript fetch
    meeting_organizer_user_id: str | None

    def graph_scope(self) -> str:
        return "https://graph.microsoft.com/.default"

    def start_end_utc(self) -> tuple[str, str]:
        """Return (startDateTime, endDateTime) in ISO 8601 UTC for getAllTranscripts."""
        end = datetime.now(timezone.utc)
        start = end - timedelta(days=self.transcript_days)
        return start.strftime("%Y-%m-%dT%H:%M:%SZ"), end.strftime("%Y-%m-%dT%H:%M:%SZ")


def load_config(environ: dict[str, str] | None = None) -> Config:
    """Load configuration from environment."""
    env = environ if environ is not None else os.environ

    def get(key: str, default: str = "") -> str:
        return env.get(key, default).strip()

    tenant_id = get("TENANT_ID")
    client_id = get("CLIENT_ID") or get("MicrosoftAppId")
    client_secret = get("CLIENT_SECRET") or get("MicrosoftAppPassword")
    authority = get("AUTHORITY") or f"https://login.microsoftonline.com/{tenant_id}"

    transcript_days_str = get("TRANSCRIPT_DAYS", "7")
    try:
        transcript_days = max(1, min(14, int(transcript_days_str)))
    except ValueError:
        transcript_days = 7

    api_version = get("AZURE_OPENAI_API_VERSION", "2024-02-15-preview")

    port_str = get("PORT", "3978")
    try:
        port = int(port_str)
    except ValueError:
        port = 3978

    return Config(
        tenant_id=tenant_id,
        client_id=client_id,
        client_secret=client_secret,
        authority=authority,
        microsoft_app_id=get("MicrosoftAppId") or client_id,
        microsoft_app_password=get("MicrosoftAppPassword") or client_secret,
        transcript_days=transcript_days,
        azure_openai_endpoint=get("AZURE_OPENAI_ENDPOINT").rstrip("/") + "/"
        if get("AZURE_OPENAI_ENDPOINT")
        else "",
        azure_openai_api_key=get("AZURE_OPENAI_API_KEY"),
        azure_openai_deployment=get("AZURE_OPENAI_DEPLOYMENT_NAME", "gpt-4o-mini"),
        azure_openai_api_version=api_version,
        port=port,
        meeting_organizer_user_id=get("MEETING_ORGANIZER_USER_ID") or None,
    )
