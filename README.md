# Jane OS — Overlay for Hermes Agent

Jane OS is a lightweight, modular overlay for [Hermes Agent](https://hermes-agent.nousresearch.com/)
that provides a product layer addressing the capabilities Hermes lacks on its own. See
[`IDEA.md`](IDEA.md) for the full design document and roadmap.

## Features

- **Modular design** — each capability is an installable module
- **Hermes integration** — modules extend Hermes' agentic capabilities without forking
- **Cross-platform** — install/uninstall works on Windows, macOS, and Linux
- **Smoke-tested** — every change validated by `tests/smoke_test.sh`

## Installation

```bash
./install.sh
```

This installs the Jane OS overlay scaffold to `~/.jane/`.

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

## Roadmap

See [`IDEA.md`](IDEA.md) for the full roadmap. Current status:
- **Phase 0** — Foundation complete (CI, docs, templates, smoke tests)
- **Phase 1** — In progress (Obsidian adapter, image-gen core, TTS module)
- **Phase 2** — Planned (pgvector RAG, JSON export, Exa reader) — see [`docs/PHASE2_DESIGN.md`](docs/PHASE2_DESIGN.md)

## Contributing

See [`CONTRIBUTING.md`](CONTRIBUTING.md) for the development workflow.
All contributions must pass CI and the smoke test.

## License

MIT — see [`LICENSE`](LICENSE).
