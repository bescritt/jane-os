# Jane OS — Overlay for Hermes

Lightweight repo scaffold following IDEA.md. Purpose: provide an overlay foundation (installer, module manifest format, smoke tests) so Jane OS modules can be developed and published.

Upstream references: https://github.com/NousResearch/hermes-agent and https://github.com/bescritt/hermes-brain. This repository intentionally contains a focused overlay; upstream contains the full Hermes implementation.

Quickstart

1. Run the smoke test locally:

   ./tests/smoke_test.sh

2. To publish to GitHub (requires gh CLI & auth):

   gh repo create --public --source=. --push

Module manifest format: see modules/sample_module/manifest.json

License: MIT (see LICENSE)

Contribution

See CONTRIBUTING.md and docs/manifest.md for how to contribute modules, tests, and manifests. For upstream ownership or project policy questions, open an issue or contact the upstream maintainers listed in IDEA.md.
