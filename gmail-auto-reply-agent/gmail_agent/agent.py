"""Core poll-and-reply logic."""
import time
from email.utils import parseaddr

from . import config, drafter, gmail_client


def should_ignore(sender_email: str) -> bool:
    sender_email = sender_email.lower()
    return any(p in sender_email for p in config.IGNORE_SENDERS)


def is_whitelisted(sender_email: str) -> bool:
    sender_email = sender_email.lower()
    return any(e.lower() in sender_email for e in config.AUTO_SEND_WHITELIST)


def decide_action(sender_email: str) -> str:
    if config.AUTO_SEND_MODE == "all":
        return "send"
    if config.AUTO_SEND_MODE == "whitelist":
        return "send" if is_whitelisted(sender_email) else "draft"
    return "draft"


def process_once(service, my_email: str, session_start_ms: int) -> None:
    messages = gmail_client.list_unread_messages(service)
    if not messages:
        print("No new unread messages.")
        return

    for m in messages:
        full = gmail_client.get_message(service, m["id"])
        parsed = gmail_client.parse_message(full)
        _, sender_email = parseaddr(parsed["from"])

        if not sender_email or sender_email.lower() == my_email.lower():
            continue
        if should_ignore(sender_email):
            print(f"Skipping ignored sender: {sender_email}")
            continue
        if config.ONLY_PROCESS_NEW_MAIL and int(full.get("internalDate", 0)) < session_start_ms:
            continue

        print(f"\nNew mail from {sender_email} - Subject: {parsed['subject']}")

        try:
            reply_body = drafter.draft_reply(parsed)
        except Exception as e:
            print(f"  Failed to draft reply: {e}")
            continue

        action = decide_action(sender_email)
        try:
            if action == "send":
                gmail_client.send_reply(service, parsed, reply_body, my_email)
                print(f"  -> Auto-sent reply to {sender_email}")
            else:
                gmail_client.create_draft_reply(service, parsed, reply_body, my_email)
                print("  -> Saved as draft for review")
            gmail_client.mark_as_read(service, m["id"])
        except Exception as e:
            print(f"  Failed to {action} reply: {e}")


def run_loop(service, my_email: str, session_start_ms: int) -> None:
    try:
        while True:
            process_once(service, my_email, session_start_ms)
            time.sleep(config.POLL_INTERVAL_SECONDS)
    except KeyboardInterrupt:
        print("Stopped.")
