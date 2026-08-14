#!/usr/bin/env bash
set -euo pipefail
cd "$(dirname "$0")/.."
python3 src/cli.py list > /tmp/jane_list.txt
python3 src/cli.py install sample_module
[ -d .jane_installed/sample_module ] && echo "install OK"
python3 src/cli.py uninstall sample_module
[ ! -d .jane_installed/sample_module ] && echo "uninstall OK"
