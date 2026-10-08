"""Configuration loaded from environment variables (.env supported)."""
import os

from dotenv import load_dotenv

load_dotenv()


def _bool(name: str, default: bool) -> bool:
    return os.getenv(name, str(default)).strip().lower() in {"1", "true", "yes", "on"}


def _list(name: str) -> list[str]:
    return [x.strip() for x in os.getenv(name, "").split(",") if x.strip()]


GMAIL_SCOPES = ["https://www.googleapis.com/auth/gmail.modify"]
CREDENTIALS_PATH = os.getenv("GMAIL_CREDENTIALS_PATH", "credentials.json")
TOKEN_PATH = os.getenv("GMAIL_TOKEN_PATH", "token.json")

ANTHROPIC_API_KEY = os.getenv("ANTHROPIC_API_KEY", "")
CLAUDE_MODEL = os.getenv("CLAUDE_MODEL", "claude-sonnet-4-6")

# "draft_only" | "whitelist" | "all"
AUTO_SEND_MODE = os.getenv("AUTO_SEND_MODE", "draft_only").strip().lower()
AUTO_SEND_WHITELIST = _list("AUTO_SEND_WHITELIST")

IGNORE_SENDERS = ["noreply@", "no-reply@", "notifications@", "mailer-daemon@"]

ONLY_PROCESS_NEW_MAIL = _bool("ONLY_PROCESS_NEW_MAIL", True)
MAX_EMAILS_PER_CYCLE = int(os.getenv("MAX_EMAILS_PER_CYCLE", "10"))
POLL_INTERVAL_SECONDS = int(os.getenv("POLL_INTERVAL_SECONDS", "60"))

USER_NAME = os.getenv("USER_NAME", "Kunal")
USER_BIO = os.getenv(
    "USER_BIO",
    "a B.Tech AI & Data Science Engineering student at K.K. Wagh Institute of Engineering, Nashik",
)

SYSTEM_PROMPT = f"""You are drafting email replies on behalf of {USER_NAME}, {USER_BIO}.

Guidelines:
- Keep replies concise, polite, and professional (or casual if the incoming email is casual).
- Match the tone and formality of the sender's email.
- Do not invent facts, commitments, dates, or promises not present in the thread.
- If the email requires information you don't have (e.g. specific data, decisions,
  approvals), draft a reply that asks a clarifying question instead of guessing.
- Sign off as "{USER_NAME}".
- Output ONLY the email body text. No subject line, no explanation, no markdown.
"""
