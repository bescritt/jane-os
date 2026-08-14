#!/usr/bin/env python3
"""
Jane OS CLI — module management + Phase 2 export + Phase 3 newsletter + Phase 4 marketplace + Phase 5 analytics.

Module commands: list / install / uninstall (Phase 0).
Export commands: export / sessions (Phase 2 — json-chat-export module).
Newsletter: generate (Phase 3 — newsletter-scheduler module).
Marketplace: publish / search (Phase 4 — module-marketplace module).
Analytics: analytics (Phase 5 — analytics-tracker module).
"""
import sys
import json
import shutil
import os
import sqlite3
import subprocess
from datetime import datetime, timezone

# Paths
_JANE_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
STATE_DB = os.path.expanduser("~/.hermes/state.db")
_MODULES = os.path.join(_JANE_ROOT, "modules")
SCRIPTS = {
    "marketplace": os.path.join(_JANE_ROOT, "modules", "module-marketplace", "scripts", "package.py"),
    "analytics": os.path.join(_JANE_ROOT, "modules", "analytics-tracker", "scripts", "collect.py"),
}


def _run_script(script_key, args):
    """Delegate to a module script (keeps CLI thin, modules self-contained)."""
    script = SCRIPTS.get(script_key)
    if not script or not os.path.isfile(script):
        print(f"ERROR: {script_key} script not found at {script}", file=sys.stderr)
        return False
    result = subprocess.run([sys.executable, script] + args, capture_output=False, timeout=60)
    return result.returncode == 0


# ── Module management (Phase 0) ─────────────────────────────────────────────

def list_mods():
    for p in sorted(os.listdir("modules")):
        m = f"modules/{p}/manifest.json"
        if os.path.isfile(m):
            d = json.load(open(m))
            print(f"{p}: extends {d.get('extends')}")


def install(name):
    src = f"modules/{name}"
    dst = f".jane_installed/{name}"
    shutil.rmtree(dst, ignore_errors=True)
    shutil.copytree(src, dst)
    print("installed", name)


def uninstall(name):
    shutil.rmtree(f".jane_installed/{name}", ignore_errors=True)
    print("removed", name)


# ── Phase 2: JSON chat export (json-chat-export module) ──────────────────────


def list_sessions():
    """List Hermes sessions from state.db (Phase 2 helper)."""
    if not os.path.isfile(STATE_DB):
        print(f"ERROR: state.db not found at {STATE_DB}")
        sys.exit(1)

    conn = sqlite3.connect(STATE_DB)
    conn.row_factory = sqlite3.Row
    c = conn.cursor()

    c.execute("""
        SELECT id, title, model, profile_name, message_count,
               started_at, ended_at
        FROM sessions
        WHERE archived = 0
        ORDER BY started_at DESC
    """)

    rows = c.fetchall()
    if not rows:
        print("No sessions found.")
        conn.close()
        return

    for r in rows:
        sid = r["id"]
        title = r["title"] or "(untitled)"
        model = r["model"] or "unknown"
        msgs = r["message_count"] or 0
        started = datetime.fromtimestamp(r["started_at"], tz=timezone.utc).isoformat() if r["started_at"] else "unknown"
        print(f"  {sid} | {title} | model={model} | msgs={msgs} | started={started}")

    conn.close()


def _session_to_dict(conn, session_id):
    """Convert a single session + its messages to a dict."""
    c = conn.cursor()
    c.execute("""
        SELECT id, title, model, profile_name, message_count,
               started_at, ended_at, cwd, estimated_cost_usd
        FROM sessions WHERE id = ?
    """, (session_id,))
    s = c.fetchone()
    if not s:
        return None

    c.execute("""
        SELECT role, content, timestamp, token_count
        FROM messages WHERE session_id = ? ORDER BY id ASC
    """, (session_id,))
    msgs = c.fetchall()

    messages = []
    for m in msgs:
        messages.append({
            "role": m["role"],
            "content": m["content"] or "",
            "timestamp": datetime.fromtimestamp(m["timestamp"], tz=timezone.utc).isoformat()
            if m["timestamp"] else None,
            "token_count": m["token_count"] or 0,
        })

    return {
        "session_id": s["id"],
        "title": s["title"] or "(untitled)",
        "model": s["model"] or "unknown",
        "profile_name": s["profile_name"],
        "message_count": s["message_count"] or 0,
        "started_at": datetime.fromtimestamp(s["started_at"], tz=timezone.utc).isoformat()
        if s["started_at"] else None,
        "ended_at": datetime.fromtimestamp(s["ended_at"], tz=timezone.utc).isoformat()
        if s["ended_at"] else None,
        "cwd": s["cwd"],
        "estimated_cost_usd": s["estimated_cost_usd"],
        "messages": messages,
    }


def export_json(session_id=None, offset=0, limit=None, output_path=None):
    """Export Hermes sessions to stable paginated JSON."""
    if not os.path.isfile(STATE_DB):
        print(f"ERROR: state.db not found at {STATE_DB}")
        sys.exit(1)

    conn = sqlite3.connect(STATE_DB)
    conn.row_factory = sqlite3.Row

    if session_id:
        session = _session_to_dict(conn, session_id)
        if session is None:
            print(f"ERROR: session '{session_id}' not found in state.db")
            conn.close()
            sys.exit(1)
        result = {
            "version": "1.0",
            "exported_at": datetime.now(timezone.utc).isoformat(),
            "sessions": [session],
            "pagination": {"offset": 0, "limit": 1, "total_sessions": 1, "has_more": False},
        }
    else:
        c = conn.cursor()
        total = c.execute("SELECT COUNT(*) FROM sessions WHERE archived = 0").fetchone()[0]
        if limit is None:
            limit = 50
        limit = min(limit, 500)
        c.execute("""
            SELECT id FROM sessions WHERE archived = 0
            ORDER BY started_at DESC LIMIT ? OFFSET ?
        """, (limit, offset))
        session_ids = [r["id"] for r in c.fetchall()]
        sessions = [_session_to_dict(conn, sid) for sid in session_ids]
        sessions = [s for s in sessions if s is not None]
        result = {
            "version": "1.0",
            "exported_at": datetime.now(timezone.utc).isoformat(),
            "sessions": sessions,
            "pagination": {"offset": offset, "limit": limit, "total_sessions": total,
                           "has_more": (offset + limit) < total},
        }

    conn.close()
    if output_path:
        with open(output_path, "w") as f:
            json.dump(result, f, indent=2, ensure_ascii=False)
        print(f"Exported {len(result['sessions'])} session(s) to {output_path}")
    else:
        print(json.dumps(result, indent=2, ensure_ascii=False))
    return result


# ── Phase 3: Newsletter generation (newsletter-scheduler module) ────────────


def generate_newsletter(dry_run=False, limit=10):
    """Generate a newsletter from recent sessions + git log."""
    sessions = []
    if os.path.isfile(STATE_DB):
        conn = sqlite3.connect(STATE_DB)
        conn.row_factory = sqlite3.Row
        c = conn.cursor()
        c.execute("""
            SELECT id, title, model, message_count, started_at
            FROM sessions WHERE archived = 0
            ORDER BY last_activity_at DESC LIMIT ?
        """, (limit,))
        for r in c.fetchall():
            sessions.append({
                "session_id": r["id"],
                "title": r["title"] or "(untitled)",
                "model": r["model"] or "unknown",
                "message_count": r["message_count"] or 0,
                "started_at": datetime.fromtimestamp(r["started_at"], tz=timezone.utc).isoformat()
                if r["started_at"] else None,
            })
        conn.close()

    updates = []
    try:
        result = subprocess.run(
            ["git", "log", "--oneline", "-5", "--", "modules/"],
            capture_output=True, text=True, timeout=10
        )
        if result.stdout.strip():
            for line in result.stdout.strip().split("\n")[:5]:
                parts = line.split(None, 1)
                updates.append({"commit": parts[0], "message": parts[1] if len(parts) > 1 else ""})
    except Exception:
        pass

    now = datetime.now(timezone.utc).strftime("%Y-%m-%d %H:%M UTC")
    lines = [f"# Jane OS Newsletter — {now}", "", "## Recent Sessions", ""]
    if sessions:
        for s in sessions[:limit]:
            lines.append(f"### {s['title']}")
            lines.append(f"- **Session:** `{s['session_id']}`")
            lines.append(f"- **Model:** {s['model']}")
            lines.append(f"- **Messages:** {s['message_count']}")
            lines.append(f"- **Started:** {s['started_at']}")
            lines.append("")
    else:
        lines.append("_No recent sessions._")
        lines.append("")
    lines.append("## Module Updates (recent commits)")
    lines.append("")
    if updates:
        for u in updates[:5]:
            lines.append(f"- `{u['commit'][:8]}` — {u['message']}")
        lines.append("")
    else:
        lines.append("_No module updates._")
        lines.append("")
    content = "\n".join(lines)
    if dry_run:
        print(content)
        print(f"\n[DRY RUN] Newsletter preview generated from {len(sessions)} sessions, {len(updates)} updates.")
    else:
        print(content)
    return len(sessions) + len(updates) > 0


# ── CLI dispatch ─────────────────────────────────────────────────────────────

USAGE = """usage: cli.py <command> [args]

Module management (Phase 0):
  list                                  List available modules
  install <module-name>                 Install a module
  uninstall <module-name>               Uninstall a module

Chat export (Phase 2 — json-chat-export):
  sessions                              List Hermes sessions from state.db
  export --format json [--session-id ID] Export sessions to JSON
         [--offset N] [--limit N] [--output FILE]

Newsletter (Phase 3 — newsletter-scheduler):
  generate [--dry-run] [--limit N]      Generate newsletter from sessions + git log

Marketplace (Phase 4 — module-marketplace):
  publish <module-name>                 Validate + package + register a module
  search <query>                        Search the local module registry

Analytics (Phase 5 — analytics-tracker):
  analytics [--output FILE]             Collect Khoj-gap parity metrics from state.db"""


def main():
    cmd = sys.argv[1] if len(sys.argv) > 1 else "list"

    if cmd == "list":
        list_mods()
    elif cmd == "install" and len(sys.argv) > 2:
        install(sys.argv[2])
    elif cmd == "uninstall" and len(sys.argv) > 2:
        uninstall(sys.argv[2])
    elif cmd == "sessions":
        list_sessions()
    elif cmd == "export":
        session_id = None; offset = 0; limit = None; output_path = None; fmt = "json"
        args = sys.argv[2:]; i = 0
        while i < len(args):
            if args[i] == "--session-id" and i + 1 < len(args): session_id = args[i + 1]; i += 2
            elif args[i] == "--offset" and i + 1 < len(args): offset = int(args[i + 1]); i += 2
            elif args[i] == "--limit" and i + 1 < len(args): limit = int(args[i + 1]); i += 2
            elif args[i] == "--output" and i + 1 < len(args): output_path = args[i + 1]; i += 2
            elif args[i] == "--format" and i + 1 < len(args): fmt = args[i + 1]; i += 2
            else:
                print(f"ERROR: unknown argument '{args[i]}'"); print(USAGE); sys.exit(1)
        if fmt != "json": print(f"ERROR: unsupported format '{fmt}'"); sys.exit(1)
        export_json(session_id=session_id, offset=offset, limit=limit, output_path=output_path)
    elif cmd == "generate":
        dry_run = "--dry-run" in sys.argv; limit = 10
        args = sys.argv[2:]; i = 0
        while i < len(args):
            if args[i] == "--dry-run": i += 1
            elif args[i] == "--limit" and i + 1 < len(args): limit = int(args[i + 1]); i += 2
            else:
                print(f"ERROR: unknown argument '{args[i]}'"); print(USAGE); sys.exit(1)
        generate_newsletter(dry_run=dry_run, limit=limit)
    elif cmd == "publish":
        if len(sys.argv) < 3:
            print("ERROR: publish requires a module name\nUsage: cli.py publish <module-name>"); sys.exit(1)
        ok = _run_script("marketplace", ["publish", sys.argv[2]])
        sys.exit(0 if ok else 1)
    elif cmd == "search":
        if len(sys.argv) < 3:
            print("ERROR: search requires a query\nUsage: cli.py search <query>"); sys.exit(1)
        ok = _run_script("marketplace", ["search", sys.argv[2]])
        sys.exit(0 if ok else 1)
    elif cmd == "analytics":
        args = sys.argv[2:]
        ok = _run_script("analytics", args)
        sys.exit(0 if ok else 1)
    else:
        print(USAGE)
        sys.exit(1 if cmd not in ("list",) else 0)


if __name__ == "__main__":
    main()
