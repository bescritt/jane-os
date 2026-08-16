# Changelog

All notable changes to this project appear in this file.

The format draws from [Keep a Changelog](https://keepachangelog.com/en/1.1.0/"),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [Unreleased]

### Added
- Phase 1 scaffolds: obsidian-adapter, image-generation-core (manifest + directory structure)
- Phase 2: json-chat-export module (stable JSON chat export with pagination) — `src/cli.py export`, `src/cli.py sessions`
- Phase 3: newsletter-scheduler module (newsletter generation from sessions + git log) — `src/cli.py generate`
- Phase 4: module-marketplace module (local registry, manifest validation, SHA256 packaging, search) — `src/cli.py publish`, `src/cli.py search`
- Phase 5: analytics-tracker module (Khoj-gap capability parity metrics from state.db) — `src/cli.py analytics`
- E-Prime compliance: IDEA.md, README.md, CONTRIBUTING.md, GitHub templates converted to active voice
- Wallace's Wheel review (docs/WHEEL_REVIEW.md): confirmed 3 bugs, applied fixes
- GitHub Pages site (docs/index.md) + promotion topics

### Fixed
- Analytics tracker: removed `eprime_enforcement` (Hermes core feature, not Jane OS), switched to `tool_name` + `tool_calls` as primary signal (over-counting fix)
- All 7 module READMEs: added Extends/Dependencies/Permissions declaration block
- cli.py: fixed relative paths (now uses _JANE_ROOT/_MODULES), added --help/-h support, fixed error exit codes

## [0.1.0] - 2026-08-14

### Added
- Project scaffold: installer (`install.sh`), uninstaller (`uninstall.sh`)
- Module manifest format (`modules/sample_module/manifest.json`)
- CLI for module install/uninstall (`src/cli.py`)
- Cross-platform smoke test (`tests/smoke_test.sh`)
- `IDEA.md` design document outlining Phase 0-3 roadmap
- CI pipeline (`.github/workflows/ci.yml`)
- Contributing guidelines (`CONTRIBUTING.md`)
- Issue templates (bug report, feature request)
- Pull request template
