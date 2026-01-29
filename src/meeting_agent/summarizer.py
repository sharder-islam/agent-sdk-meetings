"""Summarize meeting transcripts using Azure OpenAI."""

import logging
import os
from pathlib import Path
from typing import Any

from openai import AzureOpenAI

from meeting_agent.config import Config

logger = logging.getLogger(__name__)

SYSTEM_PROMPT = """You are a meeting summarizer. Given raw meeting transcript text (possibly from multiple meetings), produce a concise summary. Include: main topics, decisions, and action items when present. Keep the summary clear and scannable."""

USER_PROMPT_TEMPLATE = """Summarize the following meeting transcript(s):

---
{text}
---

Summary:"""


class TranscriptSummarizer:
    """Summarize transcripts using Azure OpenAI chat completions."""

    def __init__(self, config: Config):
        self._config = config
        self._client = AzureOpenAI(
            api_key=config.azure_openai_api_key,
            api_version=config.azure_openai_api_version,
            azure_endpoint=config.azure_openai_endpoint,
        )
        self._deployment = config.azure_openai_deployment

    def summarize_text(self, text: str, max_tokens: int = 1000) -> str:
        """Summarize a single block of transcript text."""
        if not text or not text.strip():
            return "(No transcript content to summarize.)"
        user_content = USER_PROMPT_TEMPLATE.format(text=text[:50000])
        try:
            resp = self._client.chat.completions.create(
                model=self._deployment,
                messages=[
                    {"role": "system", "content": SYSTEM_PROMPT},
                    {"role": "user", "content": user_content},
                ],
                max_tokens=max_tokens,
            )
            choice = resp.choices[0] if resp.choices else None
            if choice and choice.message and choice.message.content:
                return choice.message.content.strip()
        except Exception as e:
            logger.exception("Azure OpenAI summarization failed: %s", e)
            return f"(Summarization failed: {e})"
        return "(No summary generated.)"

    def summarize_transcripts(
        self,
        transcripts: list[dict[str, Any]],
        combined: bool = True,
        output_dir: str | None = None,
    ) -> str:
        """
        Summarize a list of transcript results (from GraphTranscriptClient).
        If combined=True, concatenate all content and produce one summary.
        If combined=False, summarize each and concatenate.
        Optionally write per-meeting summaries to output_dir.
        """
        if not transcripts:
            return "No transcripts found for the selected period."

        output_path = None
        if output_dir:
            Path(output_dir).mkdir(parents=True, exist_ok=True)
            output_path = Path(output_dir)

        if combined:
            combined_text = "\n\n---\n\n".join(
                f"Meeting {t.get('meeting_id', '')} ({t.get('created_date_time', '')}):\n{t.get('content_text', '')}"
                for t in transcripts
            )
            summary = self.summarize_text(combined_text)
            if output_path:
                (output_path / "combined_summary.md").write_text(summary, encoding="utf-8")
            return summary

        summaries: list[str] = []
        for t in transcripts:
            content = t.get("content_text", "")
            meeting_id = t.get("meeting_id", "") or "unknown"
            created = t.get("created_date_time", "")
            one = self.summarize_text(content)
            summaries.append(f"**Meeting {meeting_id}** ({created}):\n{one}")
            if output_path:
                safe_id = "".join(c if c.isalnum() or c in "-_" else "_" for c in meeting_id)[:50]
                (output_path / f"summary_{safe_id}.md").write_text(one, encoding="utf-8")
        return "\n\n".join(summaries)
