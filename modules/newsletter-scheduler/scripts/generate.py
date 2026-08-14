#!/usr/bin/env python3
"""
Newsletter generator for Jane OS Phase 3 (newsletter-scheduler module).

Aggregates content from:
  1. Hermes sessions (via state.db, using json-chat-export logic)
  2. Jane OS module updates (git log)
  3. External sources (placeholder — Phase 2 Exa reader integration)

Produces a formatted newsletter as Markdown. Can be sent via himalaya CLI
or Hermes gateway (requires external config).

Usage:
  python3 scripts/generate.py [--dry-run] [--send] [--limit N]

Integration:
  - json-chat-export module: reuses state.db session-reading logic
  - himalaya skill: email delivery via 'himalaya template send'
  - Hermes cronjob: scheduling (see README.md)
  - llama-cpp skill: optional summarization (not implemented)
"""
import sys
import os
import json
import sqlite3
import hashlib
import subprocess
from datetime import datetime, timezone
from pathlib import Path

# ── Config ────────────────────────────────────────────────────────────────

JANE_ROOT = Path(__file__).resolve().parents[2]  # repo root
STATE_DB = os.path.expanduser("~/.hermes/state.db")
CONFIG_PATH = os.path.expanduser("~/.jane/newsletter-scheduler.json")
DEFAULT_CONFIG = {
    "delivery": "stdout",
    "sources": {
        "hermes_sessions": True,
        "module_updates": True,
        "external_sources": []
    },
    "frequency": "weekly",
    "max_items": 10,
}


# ── Content Sources ───────────────────────────────────────────────────────

def read_sessions(limit=10):
    """Read recent Hermes sessions from state.db (reuses json-chat-export logic)."""
    if not os.path.isfile(STATE_DB):
        print(f"[WARN] state.db not found at {STATE_DB}", file=sys.stderr)
        return []

    conn = sqlite3.connect(STATE_DB)
    conn.row_factory = sqlite3.Row
    c = conn.cursor()

    c.execute("""
        SELECT id, title, model, message_count, started_at, estimated_cost_usd
        FROM sessions
        WHERE archived = 0
        ORDER BY last_activity_at DESC
        LIMIT ?
    """, (limit,))

    sessions = []
    for r in c.fetchall():
        sessions.append({
            "session_id": r["id"],
            "title": r["title"] or "(untitled)",
            "model": r["model"] or "unknown",
            "message_count": r["message_count"] or 0,
            "started_at": datetime.fromtimestamp(
                r["started_at"], tz=timezone.utc
            ).isoformat() if r["started_at"] else None,
            "estimated_cost_usd": r["estimated_cost_usd"],
        })

    conn.close()
    return sessions


def read_module_updates(limit=5):
    """Read recent Jane OS module git log entries."""
    try:
        result = subprocess.run(
            ["git", "log", "--oneline", f"--since='1 week ago'", "--", "modules/"],
            capture_output=True, text=True, cwd=JANE_ROOT, timeout=10
        )
        lines = result.stdout.strip().split("\n") if result.stdout.strip() else []
        return [{"commit": line.split()[0], "message": " ".join(line.split()[1:])} for line in lines[:limit]]
    except Exception as e:
        return [{"error": str(e)}]


def read_external_content(sources, limit=5):
    """Placeholder for Exa/web-reader integration (Phase 2 dependency)."""
    results = []
    for src in sources[:limit]:
        results.append({
            "source": "placeholder",
            "url": src,
            "title": "Not yet implemented",
            "excerpt": "External content integration requires the Phase 2 Exa reader module."
        })
    return results


# ── Content Processing ─────────────────────────────────────────────────────

def deduplicate(items, key_field="url"):
    """Deduplicate by content hash (Tenet 9: content-hash cache)."""
    seen = set()
    unique = []
    for item in items:
        val = item.get(key_field, "")
        h = hashlib.sha256(val.encode()).hexdigest()
        if h not in seen:
            seen.add(h)
            unique.append(item)
    return unique


def generate_newsletter(config):
    """Generate the newsletter content."""
    max_items = config.get("max_items", 10)

    # Collect content from all sources
    sessions = read_sessions(limit=max_items)
    updates = read_module_updates(limit=max_items)
    external = read_external_content(
        config.get("sources", {}).get("external_sources", []),
        limit=max_items
    )

    # Deduplicate
    sessions = deduplicate(sessions, "session_id")
    updates = deduplicate(updates, "commit")

    # Build newsletter
    now = datetime.now(timezone.utc).strftime("%Y-%m-%d %H:%M UTC")
    lines = [
        f"# Jane OS Newsletter — {now}",
        "",
        f"> Automated digest of Hermes sessions and Jane OS module updates.",
        "",
        "## Recent Sessions",
        "",
    ]

    if sessions:
        for s in sessions[:max_items]:
            cost = f"${s['estimated_cost_usd']:.4f}" if s.get('estimated_cost_usd') else "N/A"
            lines.append(f"### {s['title']}")
            lines.append(f"- **Session:** `{s['session_id']}`")
            lines.append(f"- **Model:** {s['model']}")
            lines.append(f"- **Messages:** {s['message_count']}")
            lines.append(f"- **Cost:** {cost}")
            lines.append(f"- **Started:** {s['started_at']}")
            lines.append("")
    else:
        lines.append("_No recent sessions._")
        lines.append("")

    lines.append("## Module Updates (past week)")
    lines.append("")

    if updates:
        for u in updates[:max_items]:
            if "error" in u:
                lines.append(f"- _Error: {u['error']}_")
            else:
                lines.append(f"- `{u['commit'][:8]}` — {u['message']}")
        lines.append("")
    else:
        lines.append("_No module updates this week._")
        lines.append("")

    lines.append("## External Content")
    lines.append("")

    if external:
        for e in external[:max_items]:
            lines.append(f"### {e.get('title', 'Unknown')}")
            lines.append(f"- **URL:** {e.get('url', '')}")
            lines.append(f"- **Excerpt:** {e.get('excerpt', '')}")
            lines.append("")
    else:
        lines.append("_No external sources configured._")
        lines.append("")

    lines.append("---")
    lines.append(f"_Generated by Jane OS newsletter-scheduler module. "
                 f"Sources: {len(sessions)} sessions, {len(updates)} updates, {len(external)} external._")

    return "\n".join(lines)


# ── Delivery ──────────────────────────────────────────────────────────────

def send_via_himalaya(content, config):
    """Send newsletter via himalaya CLI (per email/himalaya skill)."""
    email_cfg = config.get("email", {})
    to = email_cfg.get("to", [])
    from_addr = email_cfg.get("from", "")
    account = email_cfg.get("account", "personal")

    if not to or not from_addr:
        print("[ERROR] Email config incomplete (email.to, email.from required)", file=sys.stderr)
        return False

    to_str = ", ".join(to) if isinstance(to, list) else str(to)

    # Non-interactive send via piped stdin (per himalaya skill guidance)
    message = f"From: {from_addr}\nTo: {to_str}\nSubject: Jane OS Newsletter — {datetime.now(timezone.utc).strftime('%Y-%m-%d')}\n\n{content}\n"

    try:
        result = subprocess.run(
            ["himalaya", "--account", account, "template", "send"],
            input=message, capture_output=True, text=True, timeout=30
        )
        if result.returncode == 0:
            print("[OK] Newsletter sent via himalaya.")
            return True
        else:
            print(f"[ERROR] himalaya failed (exit {result.returncode}): {result.stderr}", file=sys.stderr)
            return False
    except FileNotFoundError:
        print("[ERROR] himalaya CLI not installed. Install from https://github.com/pimalaya/himalaya", file=sys.stderr)
        return False
    except subprocess.TimeoutExpired:
        print("[ERROR] himalaya send timed out", file=sys.stderr)
        return False


def send_via_gateway(content, config):
    """Fallback: send via Hermes gateway (Discord/Telegram)."""
    print("[INFO] Gateway delivery not yet implemented. Newsletter content:")
    print(content)
    return True


def deliver(content, config):
    """Deliver newsletter per config."""
    delivery = config.get("delivery", "stdout")

    if delivery == "stdout":
        print(content)
        return True
    elif delivery == "email":
        return send_via_himalaya(content, config)
    elif delivery == "gateway":
        return send_via_gateway(content, config)
    else:
        print(f"[ERROR] Unknown delivery method: {delivery}", file=sys.stderr)
        return False


# ── Main ─────────────────────────────────────────────────────────────────

def load_config():
    """Load config from ~/.jane/newsletter-scheduler.json or use defaults."""
    config = DEFAULT_CONFIG.copy()
    if os.path.isfile(CONFIG_PATH):
        with open(CONFIG_PATH) as f:
            config.update(json.load(f))
    return config


def main():
    import argparse
    parser = argparse.ArgumentParser(description="Jane OS newsletter generator")
    parser.add_argument("--dry-run", action="store_true", help="Print to stdout without sending")
    parser.add_argument("--send", action="store_true", help="Generate and send")
    parser.add_argument("--limit", type=int, default=10, help="Max items per section")
    args = parser.parse_args()

    config = load_config()
    config["max_items"] = args.limit

    content = generate_newsletter(config)

    if args.dry_run:
        print(content)
        print(f"\n[DRY RUN] Newsletter would be delivered via: {config.get('delivery', 'stdout')}")
    elif args.send:
        success = deliver(content, config)
        sys.exit(0 if success else 1)
    else:
        print(content)


if __name__ == "__main__":
    main()
