# Gmail Auto-Reply Agent

An AI agent that reads your unread Gmail, drafts replies with the **Claude API**, and either saves them as drafts for review or auto-sends them, depending on the safety mode you choose.

## Features

- Polls your Gmail inbox for new unread mail via the Gmail API (OAuth 2.0)
- Drafts context-aware replies with Claude, matching the sender's tone
- Three safety modes: `draft_only` (default), `whitelist`, `all`
- Ignores no-reply and automated senders
- Skips mail that arrived before the session started (optional)
- Replies stay in the same thread (`In-Reply-To` / `References` headers)
- Run once, or poll continuously

## Project structure

```
gmail-auto-reply-agent/
├── gmail_agent/
│   ├── config.py          # Settings loaded from .env
│   ├── gmail_client.py    # OAuth + Gmail read/draft/send helpers
│   ├── drafter.py         # Claude reply generation
│   └── agent.py           # Poll-and-reply logic, safety rules
├── notebooks/
│   └── gmail_auto_reply_agent.ipynb   # Original Colab version
├── tests/
│   └── test_logic.py
├── main.py                # CLI entry point
├── requirements.txt
├── .env.example
└── LICENSE
```

## Setup

### 1. Clone and install

```bash
git clone https://github.com/<your-username>/gmail-auto-reply-agent.git
cd gmail-auto-reply-agent
python -m venv .venv
source .venv/bin/activate        # Windows: .venv\Scripts\activate
pip install -r requirements.txt
```

### 2. Gmail OAuth credentials

1. Go to [Google Cloud Console](https://console.cloud.google.com/) and create a project.
2. Enable the **Gmail API**.
3. Configure the OAuth consent screen and add your Gmail address as a test user.
4. Create **OAuth client ID** credentials with type **Desktop app**.
5. Download the JSON and save it as `credentials.json` in the project root.

### 3. Anthropic API key

Get a key from the [Anthropic Console](https://console.anthropic.com/), then:

```bash
cp .env.example .env
# edit .env and set ANTHROPIC_API_KEY
```

## Usage

```bash
python main.py            # process unread mail once
python main.py --loop     # keep polling (Ctrl+C to stop)
```

The first run opens a browser for Gmail consent and saves `token.json` for later runs.

## Safety modes

Set `AUTO_SEND_MODE` in `.env`:

| Mode | Behavior |
|------|----------|
| `draft_only` | Never sends. Saves replies as Gmail drafts. **Start here.** |
| `whitelist` | Auto-sends only to addresses/domains in `AUTO_SEND_WHITELIST`; drafts for everyone else. |
| `all` | Auto-sends every reply. Use only once you trust the output. |

## Configuration

All options are in `.env.example`: model, mode, whitelist, polling interval, max emails per cycle, and the name/bio the agent writes as.

## Tests

```bash
pip install -r requirements-dev.txt
pytest
```

## Security

- `credentials.json`, `token.json` and `.env` are in `.gitignore`. **Never commit them.**
- The Gmail scope is `gmail.modify` (read, draft, send, mark as read).
- Review drafts before enabling auto-send, since the model can still misjudge a reply.

## Notebook version

`notebooks/gmail_auto_reply_agent.ipynb` is the original Google Colab version using a manual copy-paste OAuth flow.

## License

MIT
