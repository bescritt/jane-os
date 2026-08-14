# JSON Chat Export Module

**Extends:** Hermes: stable JSON chat export with pagination (Phase 2)
**Dependencies:** python3, hermes-agent
**Permissions:** filesystem, read:state_db


Phase 2 module for Jane OS. Exports Hermes Agent conversation sessions to
stable, paginated JSON format for external consumption (analytics, backup,
integration with other tools).

## Current Status
This module is a **proof-of-concept implementation** — it reads from the Hermes
`~/.hermes/state.db` SQLite session store and produces paginated JSON export.

## Manifest Fields
- **name**: `json-chat-export`
- **extends**: Hermes: stable JSON chat export with pagination (Phase 2)
- **dependencies**: `python3`, `hermes-agent`
- **permissions**: `filesystem`, `read:state_db`
- **description**: Exports Hermes sessions to stable JSON with pagination

## Integration
Per `hermes-features-reference` skill (§6: Key Paths):
- **Data source:** `~/.hermes/state.db` — SQLite session store with `sessions` and
  `messages` tables
- **Session transcripts:** `~/.hermes/sessions/` (raw, supplementary)

## Usage
```bash
# Export all sessions (paginated internally)
python3 src/cli.py export --format json --output sessions.json

# Export with manual pagination
python3 src/cli.py export --format json --offset 0 --limit 50 --output page1.json

# Export a single session
python3 src/cli.py export --format json --session-id 20260813_153155_8a3425 --output session.json

# List available sessions (for finding IDs)
python3 src/cli.py sessions
```

## JSON Schema
```json
{
  "version": "1.0",
  "exported_at": "2026-08-14T12:00:00Z",
  "sessions": [...],
  "pagination": {
    "offset": 0,
    "limit": 50,
    "total_sessions": 24,
    "has_more": true
  }
}
```

## Dependencies
- Python 3.11+ (stdlib: sqlite3, json, datetime, argparse, pathlib)
- No external packages required (per Phase 2 design doc P2-2)
