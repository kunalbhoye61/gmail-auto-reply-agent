"""Gmail authentication and message helpers."""
import base64
import os
import re
from email.mime.text import MIMEText
from email.utils import parseaddr

from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build

from . import config


def authenticate():
    """Return an authenticated Gmail service. Caches the token in token.json."""
    creds = None
    if os.path.exists(config.TOKEN_PATH):
        creds = Credentials.from_authorized_user_file(config.TOKEN_PATH, config.GMAIL_SCOPES)

    if not creds or not creds.valid:
        if creds and creds.expired and creds.refresh_token:
            creds.refresh(Request())
        else:
            if not os.path.exists(config.CREDENTIALS_PATH):
                raise FileNotFoundError(
                    f"{config.CREDENTIALS_PATH} not found. Download your OAuth client "
                    "credentials from Google Cloud Console (see README)."
                )
            flow = InstalledAppFlow.from_client_secrets_file(
                config.CREDENTIALS_PATH, config.GMAIL_SCOPES
            )
            creds = flow.run_local_server(port=0)
        with open(config.TOKEN_PATH, "w") as f:
            f.write(creds.to_json())

    return build("gmail", "v1", credentials=creds)


def get_my_email(service) -> str:
    return service.users().getProfile(userId="me").execute()["emailAddress"]


def list_unread_messages(service):
    results = (
        service.users()
        .messages()
        .list(userId="me", labelIds=["UNREAD", "INBOX"], maxResults=config.MAX_EMAILS_PER_CYCLE)
        .execute()
    )
    return results.get("messages", [])


def get_message(service, msg_id):
    return service.users().messages().get(userId="me", id=msg_id, format="full").execute()


def _get_header(message, name):
    for h in message["payload"].get("headers", []):
        if h["name"].lower() == name.lower():
            return h["value"]
    return ""


def _extract_body(payload):
    if payload.get("mimeType") == "text/plain" and "data" in payload.get("body", {}):
        return base64.urlsafe_b64decode(payload["body"]["data"]).decode("utf-8", errors="ignore")
    for part in payload.get("parts", []):
        text = _extract_body(part)
        if text:
            return text
    if payload.get("mimeType") == "text/html" and "data" in payload.get("body", {}):
        html = base64.urlsafe_b64decode(payload["body"]["data"]).decode("utf-8", errors="ignore")
        return re.sub("<[^<]+?>", "", html)
    return ""


def parse_message(message):
    return {
        "id": message["id"],
        "thread_id": message["threadId"],
        "from": _get_header(message, "From"),
        "subject": _get_header(message, "Subject"),
        "message_id_header": _get_header(message, "Message-ID"),
        "body": _extract_body(message["payload"]).strip(),
    }


def _build_reply(parsed, reply_body, my_email):
    _, sender_email = parseaddr(parsed["from"])
    subject = parsed["subject"]
    if not subject.lower().startswith("re:"):
        subject = f"Re: {subject}"
    mime_msg = MIMEText(reply_body)
    mime_msg["to"] = sender_email
    mime_msg["from"] = my_email
    mime_msg["subject"] = subject
    if parsed["message_id_header"]:
        mime_msg["In-Reply-To"] = parsed["message_id_header"]
        mime_msg["References"] = parsed["message_id_header"]
    raw = base64.urlsafe_b64encode(mime_msg.as_bytes()).decode()
    return {"raw": raw, "threadId": parsed["thread_id"]}


def create_draft_reply(service, parsed, reply_body, my_email):
    body = _build_reply(parsed, reply_body, my_email)
    return service.users().drafts().create(userId="me", body={"message": body}).execute()


def send_reply(service, parsed, reply_body, my_email):
    body = _build_reply(parsed, reply_body, my_email)
    return service.users().messages().send(userId="me", body=body).execute()


def mark_as_read(service, msg_id):
    service.users().messages().modify(
        userId="me", id=msg_id, body={"removeLabelIds": ["UNREAD"]}
    ).execute()
