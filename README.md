# Jane OS — Overlay for Hermes Agent

Jane OS is a lightweight, modular overlay for [Hermes Agent](https://hermes-agent.nousresearch.com/)
that provides a product layer addressing the capabilities Hermes lacks on its own. See
[`IDEA.md`](IDEA.md) for the full design document and roadmap.

## Features

- **Modular design** — each capability is an installable module
- **Hermes integration** — modules extend Hermes' agentic capabilities without forking
- **Cross-platform** — install/uninstall runs on Windows, macOS, and Linux
- **Smoke-tested** — every change validates via `tests/smoke_test.sh`

## Installation

```bash
./install.sh
```

This install places the Jane OS overlay scaffold at `~/.jane/`.

## Usage

List available modules:
```bash
python3 src/cli.py list
```

Install a module:
```bash
python3 src/cli.py install <module-name>
```

Uninstall a module:
```bash
python3 src/cli.py uninstall <module-name>
```

### Quick Start

1. Run the smoke test locally:
   ```bash
   bash tests/smoke_test.sh
   ```

2. List modules:
   ```bash
   python3 src/cli.py list
   ```

3. Install a module:
   ```bash
   python3 src/cli.py install sample_module
   ```

## Modules

| Module | Description | Phase |
|---|---|---|
| `sample_module` | Sample module demonstrating the manifest format | Phase 0 |
| `image-generation-core` | Diffusion-based image synthesis core | Phase 1 (scaffold) |
| `obsidian-adapter` | Obsidian client adapter for vault sync | Phase 1 (scaffold) |
| `json-chat-export` | Stable JSON chat export with pagination | Phase 2 (implemented) |
| `newsletter-scheduler` | Curated newsletter delivery with scheduling | Phase 3 (scaffold) |
| `module-marketplace` | Community marketplace, packaging, and publishing | Phase 4 (implemented) |
| `analytics-tracker` | Khoj-gap capability parity analytics from state.db | Phase 5 (implemented) |

## Roadmap

See [`IDEA.md`](IDEA.md) for the full roadmap. Current status:
- **Phase 0** — Foundation complete (CI, docs, templates, smoke tests)
|- **Phase 1** — Scaffolds in place (Obsidian adapter, image-gen core, TTS module)
|- **Phase 2** — Implemented (JSON export) + Planning (pgvector RAG, Exa reader — see [`docs/PHASE2_DESIGN.md`](docs/PHASE2_DESIGN.md))
- **Phase 3** — Planned (newsletter, phone app, enterprise deployment — see [`docs/PHASE3_DESIGN.md`](docs/PHASE3_DESIGN.md))
- **Phase 4** — Implemented (module marketplace — see [`docs/PHASE4_DESIGN.md`](docs/PHASE4_DESIGN.md))
- **Phase 5** — Implemented (analytics tracker — see [`docs/PHASE5_DESIGN.md`](docs/PHASE5_DESIGN.md))
- **Phase 6** — Planned (DX platform, benchmarking, docs automation, release automation — see [`docs/PHASE6_DESIGN.md`](docs/PHASE6_DESIGN.md))

## Contributing

See [`CONTRIBUTING.md`](CONTRIBUTING.md) for the development workflow.
All contributions must pass CI and the smoke test.

## License

MIT — see [`LICENSE`](LICENSE).
