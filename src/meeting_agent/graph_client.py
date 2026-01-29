"""Microsoft Graph client for meeting transcripts."""

import logging
from datetime import datetime
from typing import Any

import httpx

from meeting_agent.auth import GraphAuth
from meeting_agent.config import Config
from meeting_agent.transcript_parser import parse_vtt_to_text

logger = logging.getLogger(__name__)

GRAPH_BASE = "https://graph.microsoft.com/v1.0"


class GraphTranscriptClient:
    """Fetch meeting transcripts via Microsoft Graph getAllTranscripts and content URL."""

    def __init__(self, config: Config, auth: GraphAuth):
        self._config = config
        self._auth = auth

    def _headers(self) -> dict[str, str]:
        return {
            "Authorization": f"Bearer {self._auth.access_token}",
            "Content-Type": "application/json",
        }

    def get_all_transcripts(
        self,
        user_id: str,
        start_date_time: str,
        end_date_time: str,
    ) -> list[dict[str, Any]]:
        """
        GET /users/{userId}/onlineMeetings/getAllTranscripts(meetingOrganizerUserId=..., startDateTime=..., endDateTime=...)
        Returns list of callTranscript objects (id, meetingId, transcriptContentUrl, createdDateTime, etc.).
        """
        url = (
            f"{GRAPH_BASE}/users/{user_id}/onlineMeetings/getAllTranscripts"
            f"(meetingOrganizerUserId='{user_id}',startDateTime={start_date_time},endDateTime={end_date_time})"
        )
        all_transcripts: list[dict[str, Any]] = []
        with httpx.Client(timeout=60.0) as client:
            while url:
                resp = client.get(url, headers=self._headers())
                resp.raise_for_status()
                data = resp.json()
                value = data.get("value", [])
                all_transcripts.extend(value)
                url = data.get("@odata.nextLink")
        return all_transcripts

    def get_transcript_content(self, content_url: str) -> str:
        """
        GET transcript content (VTT). content_url is the transcriptContentUrl from callTranscript
        or the full URL to .../transcripts/{id}/content.
        """
        if not content_url.startswith("http"):
            content_url = GRAPH_BASE.rstrip("/") + ("/" + content_url.lstrip("/"))
        with httpx.Client(timeout=30.0) as client:
            resp = client.get(content_url, headers=self._headers())
            resp.raise_for_status()
            return resp.text

    def fetch_transcripts_for_user(
        self,
        user_id: str,
        start_date_time: str | None = None,
        end_date_time: str | None = None,
    ) -> list[dict[str, Any]]:
        """
        Fetch all transcript metadata for the organizer in the configured (or given) date range.
        Returns list of dicts with keys: transcript_id, meeting_id, created_date_time, content_text.
        """
        start, end = start_date_time, end_date_time
        if not start or not end:
            start, end = self._config.start_end_utc()
        transcripts_meta = self.get_all_transcripts(user_id, start, end)
        results: list[dict[str, Any]] = []
        for t in transcripts_meta:
            transcript_id = t.get("id")
            meeting_id = t.get("meetingId")
            created = t.get("createdDateTime", "")
            content_url = t.get("transcriptContentUrl")
            if not content_url:
                continue
            try:
                vtt = self.get_transcript_content(content_url)
                content_text = parse_vtt_to_text(vtt)
            except Exception as e:
                logger.warning("Failed to fetch transcript content %s: %s", transcript_id, e)
                content_text = ""
            results.append(
                {
                    "transcript_id": transcript_id,
                    "meeting_id": meeting_id,
                    "created_date_time": created,
                    "content_text": content_text,
                }
            )
        return results


def format_datetime_iso(dt: datetime) -> str:
    """Format datetime for Graph API (ISO 8601 UTC)."""
    return dt.strftime("%Y-%m-%dT%H:%M:%SZ")
