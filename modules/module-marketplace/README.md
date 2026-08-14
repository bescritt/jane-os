# Module Marketplace

**Extends:** Hermes: community marketplace for module discovery, packaging, and publishing (Phase 4)
**Dependencies:** python3, hermes-agent, tar, sha256sum
**Permissions:** filesystem, network, package_modules


Phase 4 module for Jane OS. Enables community sharing of Jane OS modules via a
local registry with manifest validation, content-hashed packaging, and search.

## Current Status
This module is **implemented** — the `package.py` script provides manifest validation,
`.tar.gz` packaging with SHA256 content hash, and a local registry with search.

## Manifest Fields
- **name**: `module-marketplace`
- **extends**: Hermes: community marketplace for module discovery, packaging, and publishing (Phase 4)
- **dependencies**: `python3`, `hermes-agent`, `tar`, `sha256sum`
- **permissions**: `filesystem`, `network`, `package_modules`

## Integration
- **`json-chat-export` module** (Phase 2): marketplace packages list this as a dependency
- **`osint/secret-hygiene` skill**: manifest validation checks for embedded secrets (future)
- **`codebase-inspection` skill**: package quality analysis (future)
- **CLI**: `publish` and `search` subcommands (see `src/cli.py`)

## Architecture

```
[CLI: publish <module-name>]
  ├── Validate manifest.json (required fields: name, extends, dependencies, permissions)
  ├── Compute SHA256 content hash (Tenet 9: content-hash cache)
  └── Package into .tar.gz (module-name-version-hash.tar.gz)
         │
         ▼
[Local Registry: ~/.jane/registry/]
  ├── index.json — searchable catalog of published modules
  ├── Each entry: name, version, sha256, tags, description, path
  └── Searchable by name / tag / description

[CLI: search <query>]
  ├── Query local registry index
  ├── Match by name, tag, or description (case-insensitive)
  └── Return matching modules with sha256 + metadata
```

## Usage

```bash
# Publish a module to the local registry
python3 src/cli.py publish obsidian-adapter

# Search the registry
python3 src/cli.py search obsidian
python3 src/cli.py search "Phase 1"
python3 src/cli.py search json

# List all published modules
python3 modules/module-marketplace/scripts/package.py list

# Registry location
ls ~/.jane/registry/
```

## Registry Format

`~/.jane/registry/index.json`:
```json
{
  "modules": [
    {
      "name": "obsidian-adapter",
      "version": "1.0.0",
      "sha256": "<content hash>",
      "tags": ["phase1", "obsidian", "adapter"],
      "description": "Obsidian client adapter",
      "published_at": "2026-08-14T...",
      "manifest": { ...full manifest... }
    }
  ]
}
```

## Dependencies
- Python 3.11+ (stdlib: json, hashlib, subprocess, tarfile, datetime, pathlib)
- `tar` command (for packaging)
- No external packages required

## Current Limitations
- Local registry only (single user). Distributed registry (Phase 4.1.4) is planned.
- Secret scanning via `osint/secret-hygiene` skill is documented but not yet integrated.
