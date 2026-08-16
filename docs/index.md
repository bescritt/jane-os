---
layout: default
title: Jane OS — Overlay for Hermes
---

# Jane OS

**A lightweight overlay that productizes Hermes Agent capabilities — installer scripts, module manifests, and cross-platform smoke tests.**

## What is Jane OS?

Jane OS adds a layer of usability on top of Hermes Agent:

- **Installer/uninstaller scripts** — cross-platform deployment
- **Module manifest format** — structured packaging for Hermes skills
- **Cross-platform smoke tests** — automated verification
- **Documentation** — scope, non-goals, contribution guidelines

## Quick Start

```bash
# Clone
git clone https://github.com/bescritt/jane-os.git
cd jane-os

# Run smoke test
bash tests/smoke_test.sh
```

## Modules

Jane OS provides modules that extend Hermes Agent:

| Module | Description |
|---|---|
| sample_module | Minimal example following the manifest format |
| analytics-tracker | Phase 5 analytics tracker |
| module-marketplace | Phase 4 marketplace |
| obsidian-adapter | Obsidian integration |
| image-generation-core | Image generation core |
| json-chat-export | Chat export utilities |
| newsletter-scheduler | Newsletter automation |

## Manifest Format

Each module declares:

```json
{
  "name": "module-name",
  "version": "1.0.0",
  "description": "What this module does",
  "entry": "scripts/main.py",
  "tags": ["tag1", "tag2"]
}
```

See [`docs/manifest.md`](./docs/manifest.md) for details.

## Documentation

- [IDEA.md](./IDEA.md) — Project philosophy and phase design
- [docs/PHASE2_DESIGN.md](./docs/PHASE2_DESIGN.md) — Phase 2 design
- [docs/PHASE3_DESIGN.md](./docs/PHASE3_DESIGN.md) — Phase 3 design
- [docs/PHASE4_DESIGN.md](./docs/PHASE4_DESIGN.md) — Phase 4 design (marketplace)
- [docs/PHASE5_DESIGN.md](./docs/PHASE5_DESIGN.md) — Phase 5 design (analytics)
- [docs/PHASE6_DESIGN.md](./docs/PHASE6_DESIGN.md) — Phase 6 design (distributed)
- [docs/WHEEL_REVIEW.md](./docs/WHEEL_REVIEW.md) — Wallace's Wheel review

## License

MIT — see [LICENSE](./LICENSE).
