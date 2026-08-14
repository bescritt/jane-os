# Analytics Tracker Module

**Extends:** Hermes: analytics metrics for Khoj-gap capability parity tracking (Phase 5)
**Dependencies:** python3, hermes-agent, json-chat-export
**Permissions:** filesystem, read:state_db


Phase 5 module for Jane OS. Collects metrics from Hermes's `state.db` to measure
parity with Khoj's 9 "gap" capabilities (IDEA.md §25-34), satisfying IDEA.md §43
("Provide all nine Khoj-gap capabilities listed above with measurable parity").

## Current Status
This module is a **scaffold with implementation** — the `collect.py` script computes
real metrics from `state.db` and the CLI `analytics` subcommand outputs them as JSON.

## Manifest Fields
- **name**: `analytics-tracker`
- **extends**: Hermes: analytics metrics for Khoj-gap capability parity tracking (Phase 5)
- **dependencies**: `python3`, `hermes-agent`, `json-chat-export`
- **permissions**: `filesystem`, `read:state_db`

## The 9 Khoj-Gap Capabilities (IDEA.md §25-34)

| # | Capability | Metric Tracked |
|---|---|---|
| 1 | OSINT tooling | sessions with OSINT skills used (tool_call_count) |
| 2 | Reverse engineering tools | sessions with RE tools |
| 3 | GPU/CUDA setup tooling | sessions with GPU/CUDA tools |
| 4 | Desktop GUI control | sessions with computer_use / desktop_ui |
| 5 | Local fail-closed LLM judge | usage of judge_gate / local model |
| 6 | Tiered persistent memory | usage of memory / tiered_memory |
| 7 | E-Prime self-enforcement | sessions with E-Prime |
| 8 | Subagent orchestration | sessions with delegate_task |
| 9 | Procedural skills | sessions with /skill commands |

## Architecture

```
[state.db (sessions + messages tables)]
  ├── Aggregate: session count, message count, token usage, cost
  ├── Per-capability: scan messages for tool/skill keywords
  └── Per-model: usage breakdown (latency, tokens, cost)
         │
         ▼
[collect.py]
  ├── Read-only SQLite queries
  ├── Output: versioned JSON {version, collected_at, metrics{}, capabilities{}}
  └── Exit code 0 on success
         │
         ▼
[CLI: analytics]
  ├── python3 src/cli.py analytics [show|export] [--output FILE]
  └── JSON output for CI/CD integration
```

## Integration
- **state.db** (Hermes): primary data source — `sessions` table (40 columns) + `messages` table
- **json-chat-export module** (Phase 2): reuses state.db reading pattern
- **`hermes-features-reference` skill**: maps CLI commands to capabilities
- **Ten-tenets judge_gate** (Tenet 3): quality gate for metrics claims
- **SMELOSS §46**: "testable against measured behavior" — analytics provides the measures

## Usage
```bash
# Show metrics (pretty JSON to stdout)
python3 src/cli.py analytics

# Export to file
python3 src/cli.py analytics --output ~/.jane/analytics/latest.json

# Direct module usage
python3 modules/analytics-tracker/scripts/collect.py
python3 modules/analytics-tracker/scripts/collect.py --output /tmp/metrics.json
```

## JSON Output Schema
```json
{
  "version": "1.0",
  "collected_at": "2026-08-14T21:30:00Z",
  "metrics": {
    "total_sessions": 24,
    "total_messages": 10494,
    "total_input_tokens": 14375257,
    "total_output_tokens": 253915,
    "total_cost_usd": 72.84,
    "models_used": {"hy3-free": 24, "qwen2.5-1.5b": 0}
  },
  "capabilities": {
    "osint_tooling": {"sessions": 5, "messages": 127},
    "reverse_engineering": {"sessions": 3, "messages": 42},
    "gpu_cuda": {"sessions": 2, "messages": 18},
    "desktop_gui": {"sessions": 1, "messages": 23},
    "local_judge": {"sessions": 8, "messages": 301},
    "tiered_memory": {"sessions": 3, "messages": 89},
    "eprime_enforcement": {"sessions": 0, "messages": 0},
    "subagent_orchestration": {"sessions": 7, "messages": 210},
    "procedural_skills": {"sessions": 12, "messages": 415}
  },
  "khoj_parity": {
    "capabilities_with_data": 7,
    "capabilities_without_data": 2,
    "total_capabilities": 9
  }
}
```

## Dependencies
- Python 3.11+ (stdlib: json, sqlite3, datetime, pathlib)
- Hermes state.db (read-only queries — no writes)
- No external packages required
