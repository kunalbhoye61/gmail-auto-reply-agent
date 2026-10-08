"""Draft reply text with Claude."""
import anthropic

from . import config

_client = None


def _get_client():
    global _client
    if _client is None:
        if not config.ANTHROPIC_API_KEY:
            raise RuntimeError("ANTHROPIC_API_KEY is not set. Add it to your .env file.")
        _client = anthropic.Anthropic(api_key=config.ANTHROPIC_API_KEY)
    return _client


def draft_reply(parsed_email: dict) -> str:
    user_prompt = (
        f"From: {parsed_email['from']}\n"
        f"Subject: {parsed_email['subject']}\n\n"
        f"Email body:\n{parsed_email['body']}\n\n"
        "Write the reply body."
    )
    response = _get_client().messages.create(
        model=config.CLAUDE_MODEL,
        max_tokens=600,
        system=config.SYSTEM_PROMPT,
        messages=[{"role": "user", "content": user_prompt}],
    )
    return "".join(b.text for b in response.content if b.type == "text").strip()
