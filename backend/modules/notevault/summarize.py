"""
Summarization module for NoteVault
Uses the Anthropic Claude API to produce structured summaries.
"""

import json
import logging
import os
from typing import Optional

logger = logging.getLogger(__name__)

# Max characters of raw text sent to Claude (keeps latency + cost low)
_MAX_TEXT_CHARS = 12_000


def summarize(raw_text: str, file_name: str = "") -> dict:
    """
    Summarize extracted text using Claude.

    Returns a dict:
        {
            "title":   str,          # Suggested note title
            "summary": str,          # 100-150 word summary
            "tags":    list[str],    # 3-5 keyword tags
            "ocr_text": str          # The original raw text (passed through)
        }

    On failure, returns safe defaults so the upload never crashes.
    """
    if not raw_text or not raw_text.strip():
        return _empty_result(file_name)

    try:
        result = _call_claude(raw_text.strip(), file_name)
        result["ocr_text"] = raw_text
        return result
    except Exception as e:
        logger.error(f"Summarization failed: {e}")
        # Degrade gracefully — still save the file with raw text
        return {
            "title":    file_name or "Untitled note",
            "summary":  raw_text[:300] + ("…" if len(raw_text) > 300 else ""),
            "tags":     [],
            "ocr_text": raw_text,
        }


# ── Internal ──────────────────────────────────────────────────────────────────

def _call_claude(raw_text: str, file_name: str) -> dict:
    import anthropic

    client = anthropic.Anthropic(api_key=os.environ["ANTHROPIC_API_KEY"])

    truncated = raw_text[:_MAX_TEXT_CHARS]
    hint = f'The file is named "{file_name}".\n\n' if file_name else ""

    prompt = f"""{hint}You are a smart note-taking assistant. \
Analyse the text extracted from a document and return a JSON object with exactly these keys:

- "title"   : a short, descriptive title (≤8 words)
- "summary" : a clear summary in 100-150 words
- "tags"    : an array of 3-5 lowercase keyword tags

Return ONLY valid JSON — no markdown fences, no preamble, no explanation.

EXTRACTED TEXT:
{truncated}"""

    message = client.messages.create(
        model="claude-sonnet-4-20250514",
        max_tokens=512,
        messages=[{"role": "user", "content": prompt}],
    )

    raw_response = message.content[0].text.strip()
    # Strip accidental markdown fences
    clean = raw_response.replace("```json", "").replace("```", "").strip()
    parsed = json.loads(clean)

    # Validate expected keys and types
    title   = str(parsed.get("title", file_name or "Untitled note"))
    summary = str(parsed.get("summary", ""))
    tags    = parsed.get("tags", [])
    if not isinstance(tags, list):
        tags = []

    return {"title": title, "summary": summary, "tags": tags}


def _empty_result(file_name: str) -> dict:
    return {
        "title":    file_name or "Untitled note",
        "summary":  "No text could be extracted from this file.",
        "tags":     [],
        "ocr_text": "",
    }
