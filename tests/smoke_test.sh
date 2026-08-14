#!/usr/bin/env bash
set -euo pipefail
cd "$(dirname "$0")/.."

# Phase 0: module install/uninstall lifecycle
python3 src/cli.py list | grep -q "sample_module" && echo "sample_module recognized"
python3 src/cli.py install sample_module
[ -d .jane_installed/sample_module ] && echo "install OK"
python3 src/cli.py uninstall sample_module
[ ! -d .jane_installed/sample_module ] && echo "uninstall OK"

# Phase 1: obsidian-adapter module lifecycle
python3 src/cli.py list | grep -q "obsidian-adapter" && echo "obsidian-adapter recognized"
python3 src/cli.py install obsidian-adapter
[ -d .jane_installed/obsidian-adapter ] && echo "obsidian-install OK"
python3 src/cli.py uninstall obsidian-adapter
[ ! -d .jane_installed/obsidian-adapter ] && echo "obsidian-uninstall OK"

# Phase 2: JSON chat export (from Hermes state.db)
python3 src/cli.py list | grep -q "json-chat-export" && echo "json-chat-export recognized"
python3 src/cli.py sessions > /tmp/jane_sessions.txt
[ -s /tmp/jane_sessions.txt ] && echo "sessions-list OK"
python3 src/cli.py export --format json --limit 1 --output /tmp/jane_export.json
python3 -c "import json; d=json.load(open('/tmp/jane_export.json')); assert 'version' in d and 'sessions' in d and 'pagination' in d" && echo "export-schema OK"

echo "ALL SMOKE TESTS PASSED"
