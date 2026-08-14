# Jane OS — Overlay for Hermes

Lightweight repo scaffold following IDEA.md. Purpose: provide an overlay foundation (installer, module manifest format, smoke tests) so Jane OS modules can be developed and published.

Quickstart

1. Run the smoke test locally:

   ./tests/smoke_test.sh

2. To publish to GitHub (requires gh CLI & auth):

   gh repo create --public --source=. --push

Module manifest format: see modules/sample_module/manifest.json

License: MIT (see LICENSE)
