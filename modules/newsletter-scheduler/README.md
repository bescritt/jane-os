# Newsletter Scheduler Module

Phase 3 module for Jane OS. Aggregates content from Hermes sessions, Jane OS
modules, and external sources into curated newsletters delivered via email or
messaging.

## Current Status
This module is a **scaffold** — the manifest and core script are in place.
Email delivery requires the `himalaya` CLI (see prerequisites).

## Manifest Fields
- **name**: `newsletter-scheduler`
- **extends**: Hermes: newsletter + smart notification scheduling (Phase 3)
- **dependencies**: `python3`, `hermes-agent`, `json-chat-export`
- **permissions**: `filesystem`, `network`, `schedule_emails`
- **description**: Curated newsletter delivery with scheduling

## Integration
- **json-chat-export (Phase 2):** Source content — exported Hermes sessions
  (per `docs/PHASE2_DESIGN.md` §2.2: `~/.hermes/state.db` → JSON)
- **himalaya skill** (`email/himalaya`): Email delivery via `himalaya template send`
  (non-interactive piped input — see himalaya skill §"Write a New Email")
- **Hermes cronjob system:** Scheduling engine (per `competitor-news-monitor` skill:
  `cronjob(action="create", schedule="every monday 9am", prompt="...")`)
- **llama-cpp skill:** Content summarization (per `llm/inference/llama-cpp`: `Llama(embedding=True)`)

## Prerequisites
1. Himalaya CLI installed and configured (`~/.config/himalaya/config.toml`)
   ```bash
   curl -sSL https://raw.githubusercontent.com/pimalaya/himalaya/master/install.sh | PREFIX=~/.local sh
   himalaya account configure
   ```
2. `json-chat-export` module installed (`python3 src/cli.py install json-chat-export`)

## Architecture

```
[Content Sources]
  ├── Hermes sessions (via json-chat-export → state.db)
  ├── Jane OS module updates (git log of bescritt/jane-os)
  └── External sources (via Exa reader or web_search)
         │
         ▼
[Content Aggregator] (aggregate.py)
  ├── Extract key insights (summary via llama-cpp if available)
  ├── Tag + categorize
  ├── Deduplicate (content-hash cache per Tenet 9)
  └── Score relevance
         │
         ▼
[Delivery] (send_newsletter.py)
  ├── Format as Markdown/HTML email
  ├── Pipe via himalaya: cat << EOF | himalaya template send
  └── Fallback to Hermes gateway (Discord/Telegram) if email fails
         │
         ▼
[Scheduling] (via Hermes cronjob)
  cronjob(action="create",
          schedule="every monday 9am",
          prompt="Load newsletter-scheduler skill and run send_newsletter.py")
```

## Usage
```bash
# Install the module
python3 src/cli.py install newsletter-scheduler

# Generate a newsletter (dry run to stdout)
python3 modules/newsletter-scheduler/scripts/generate.py --dry-run

# Generate + send
python3 modules/newsletter-scheduler/scripts/generate.py --send

# List recent sessions for curation
python3 src/cli.py sessions

# Export sessions as source content
python3 src/cli.py export --format json --limit 10 --output /tmp/recent_sessions.json

# Schedule (via Hermes cronjob system — see himalaya skill for SMTP config)
```

## Configuration
Create `~/.jane/newsletter-scheduler.json`:
```json
{
  "delivery": "email",
  "email": {
    "from": "jane@newsletter.example.com",
    "to": ["user@example.com"],
    "account": "personal"
  },
  "sources": {
    "hermes_sessions": true,
    "module_updates": true,
    "external_sources": []
  },
  "frequency": "weekly",
  "max_items": 10
}
```

## Dependencies
- Python 3.11+ (stdlib: json, sqlite3, subprocess, datetime, hashlib, pathlib)
- `himalaya` CLI (external — for email delivery)
- `json-chat-export` module (for Hermes session content)
- Optional: llama-cpp (for AI-generated summaries)

## Current Limitations
- Email delivery requires himalaya CLI (not installed in this environment)
- External source integration (Exa/web_search) is a Phase 2 dependency
- This is a scaffold — the generator script provides structure only
