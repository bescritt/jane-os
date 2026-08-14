# Obsidian Client Adapter Module

**Extends:** Hermes: Obsidian client adapter (Phase 1)
**Dependencies:** python3, hermes-agent
**Permissions:** filesystem, network


Phase 1 module for Jane OS. Bridges Jane OS with
[Obsidian](https://obsidian.md/) — the local-first Markdown knowledge base.

## Current Status
This module serves as a **scaffold** — the manifest and directory structure serve in place.
The actual API client and sync logic implement in subsequent iterations.

## Manifest Fields
- **name**: `obsidian-adapter`
- **extends**: Hermes: Obsidian client adapter (Phase 1)
- **dependencies**: `python3`, `hermes-agent`
- **permissions**: `filesystem`, `network`
- **description**: Bidirectional Obsidian vault bridge

## Planned Capabilities (Phase 1 full implementation)

### Sync
- Push Hermes session notes to an Obsidian vault (Markdown format)
- Pull Obsidian notes as context for Hermes queries

### Query
- Search Obsidian vault by tag, title, or content
- Resolve Obsidian URI links (`obsidian://`) from Hermes context

### Integration Points
- Reads from Hermes `state.db` session store for note export
- Writes to user's Obsidian vault directory (requires vault path config)
- Leverages existing Hermes CLI (`src/cli.py`) for module management

## Usage
```bash
python3 src/cli.py install obsidian-adapter
python3 src/cli.py uninstall obsidian-adapter
python3 src/cli.py list
```

## Configuration
Phase 2 adds a config file at `~/.jane/obsidian-adapter.json`:
```json
{
  "vault_path": "/path/to/obsidian/vault",
  "export_format": "markdown"
}
```
