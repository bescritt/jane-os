#!/usr/bin/env bash
set -euo pipefail
cd "$(dirname "$0")/.."

# Phase 0: module lifecycle
python3 src/cli.py list | grep -q "sample_module"
python3 src/cli.py install sample_module
[ -d .jane_installed/sample_module ]
python3 src/cli.py uninstall sample_module
[ ! -d .jane_installed/sample_module ]

# Phase 1: obsidian-adapter
python3 src/cli.py list | grep -q "obsidian-adapter"
python3 src/cli.py install obsidian-adapter
[ -d .jane_installed/obsidian-adapter ]
python3 src/cli.py uninstall obsidian-adapter
[ ! -d .jane_installed/obsidian-adapter ]

# Phase 2: json-chat-export
python3 src/cli.py list | grep -q "json-chat-export"
python3 src/cli.py sessions > /tmp/jane_sessions.txt
[ -s /tmp/jane_sessions.txt ]
python3 src/cli.py export --format json --limit 1 --output /tmp/jane_export.json
python3 -c "import json; d=json.load(open('/tmp/jane_export.json')); assert 'version' in d and 'sessions' in d"

# Phase 3: newsletter
python3 src/cli.py list | grep -q "newsletter-scheduler"
python3 src/cli.py generate --dry-run --limit 1 > /tmp/jane_newsletter.txt
[ -s /tmp/jane_newsletter.txt ]

# Phase 4: marketplace — clean registry first, then publish + search
rm -rf ~/.jane/registry
python3 src/cli.py publish sample_module
python3 src/cli.py publish obsidian-adapter
python3 src/cli.py publish json-chat-export
python3 src/cli.py publish newsletter-scheduler
python3 src/cli.py publish module-marketplace
# Verify search works
python3 src/cli.py search obsidian > /tmp/jane_search.txt
[ -s /tmp/jane_search.txt ]
python3 src/cli.py search phase1 > /tmp/jane_search2.txt
[ -s /tmp/jane_search2.txt ]

echo "ALL SMOKE TESTS PASSED"
