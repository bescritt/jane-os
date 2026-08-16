#!/usr/bin/env python3
"""
Obsidian client adapter — Phase 1 scaffold.

Provides a minimal entry point for bidirectional sync between
Hermes Agent sessions and an Obsidian vault.

Full implementation deferred to a subsequent iteration.
"""
import sys
import os
import json
from datetime import datetime, timezone

VAULT_CONFIG = os.path.expanduser("~/.jane/obsidian-adapter.json")


def load_config():
    if os.path.isfile(VAULT_CONFIG):
        with open(VAULT_CONFIG) as f:
            return json.load(f)
    return {}


def sync_session_to_vault(session_id, session_title, content, vault_path):
    """
    Push a Hermes session to the Obsidian vault as a markdown note.

    Full implementation: reads session from state.db, converts to markdown,
    writes to vault_path with proper frontmatter.
    """
    if not vault_path or not os.path.isdir(vault_path):
        print(f"ERROR: vault path not found: {vault_path}", file=sys.stderr)
        return False

    slug = session_id.replace("_", "-")
    note_path = os.path.join(vault_path, f"hermes-session-{slug}.md")

    frontmatter = {
        "title": session_title or "(untitled)",
        "session_id": session_id,
        "created": datetime.now(timezone.utc).isoformat(),
        "type": "hermes-session",
    }

    with open(note_path, "w") as f:
        f.write("---\n")
        json.dump(frontmatter, f, indent=2)
        f.write("\n---\n\n")
        f.write(content or "(no content)\n")

    print(f"Synced session {session_id} -> {note_path}")
    return True


def main():
    import argparse
    parser = argparse.ArgumentParser(
        description="Obsidian adapter scaffold (Phase 1 — stub)"
    )
    parser.add_argument(
        "--sync",
        nargs=3,
        metavar=("SESSION_ID", "TITLE", "VAULT_PATH"),
        help="Sync a session to the vault (stub: writes placeholder)",
    )
    args = parser.parse_args()

    cfg = load_config()
    vault_path = cfg.get("vault_path", "")

    if args.sync:
        sid, title, vpath = args.sync
        sync_session_to_vault(sid, title, "", vpath or vault_path)
    else:
        print("Obsidian adapter — Phase 1 scaffold.")
        print("Install: python3 src/cli.py install obsidian-adapter")
        print("Usage:  python3 modules/obsidian-adapter/scripts/main.py --sync <session_id> <title> <vault_path>")
        print(f"Config: {VAULT_CONFIG} (create with vault_path + export_format)")
        print("Status: scaffold — full sync logic deferred to subsequent iteration.")


if __name__ == "__main__":
    main()
