"""Parse VTT transcript content from Microsoft Graph."""

import re
from dataclasses import dataclass


@dataclass
class TranscriptSegment:
    """A single segment (speaker + text) from a transcript."""

    speaker: str
    text: str


def parse_vtt_to_text(vtt_content: str) -> str:
    """
    Parse VTT content (from Graph transcript content URL) into plain text.
    Strips WEBVTT headers and extracts text from <v Speaker>...</v> cues.
    """
    if not vtt_content or not vtt_content.strip():
        return ""

    lines = vtt_content.strip().splitlines()
    text_parts: list[str] = []
    in_cue = False

    for line in lines:
        line = line.strip()
        if not line:
            continue
        if line.upper().startswith("WEBVTT"):
            continue
        if re.match(r"^\d{2}:\d{2}:\d{2}", line) or " --> " in line:
            in_cue = True
            continue
        # Cue text: may be <v Speaker>text</v> or plain
        if in_cue or "<v " in line:
            match = re.search(r"<v\s+([^>]+)>\s*([^<]*)\s*</v>", line, re.IGNORECASE)
            if match:
                speaker, text = match.group(1).strip(), match.group(2).strip()
                if text:
                    text_parts.append(f"{speaker}: {text}")
            else:
                # Plain line (no voice tag)
                if line and not line.startswith("NOTE"):
                    text_parts.append(line)
        in_cue = False

    return "\n".join(text_parts).strip()


def parse_vtt_to_segments(vtt_content: str) -> list[TranscriptSegment]:
    """Parse VTT into list of segments (speaker, text)."""
    if not vtt_content or not vtt_content.strip():
        return []

    segments: list[TranscriptSegment] = []
    for line in vtt_content.strip().splitlines():
        line = line.strip()
        match = re.search(r"<v\s+([^>]+)>\s*([^<]*)\s*</v>", line, re.IGNORECASE)
        if match:
            segments.append(
                TranscriptSegment(speaker=match.group(1).strip(), text=match.group(2).strip())
            )
    return segments
