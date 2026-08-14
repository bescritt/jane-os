Each module should declare:

- What Hermes capability it extends
- What external services or dependencies it requires
- What permissions or consent it needs
- How to install/uninstall it cleanly

---

## Non-Goals

- **Not a fork of Hermes**
- **Not a clone of Khoj**
- **Not a replacement for Hermes core tools, judge, memory, or E-Prime enforcement**
- **Not a generic agent framework**
- **Not a duplicate of features Hermes already has**, unless they need to be productized
- **Not a SaaS product in its own right** — enterprise tier is an overlay deployment layer for Hermes+Jane, not a separate hosted service

---

## Why Not Just Use Khoj?

Because Khoj does not ship the deep agentic capabilities that Hermes does:

- OSINT tooling
- Reverse engineering tools
- GPU/CUDA setup tooling
- Desktop GUI control
- Local fail-closed LLM judge
- Tiered persistent memory
- E-Prime self-enforcement
- Subagent orchestration
- Procedural skills

Users who need those capabilities are running Hermes. Jane OS gives them the missing product layer without abandoning Hermes.

---

## Success Criteria

A stock Hermes installation plus Jane OS should:

1. Provide all nine Khoj-gap capabilities listed above with measurable parity
2. Preserve existing Hermes agentic behavior unchanged
3. Install and uninstall cleanly on Windows, macOS, and Linux
4. Be modular: users can enable only the modules they need
5. Respect Hermes’s offline-first, fail-closed, and consent-oriented design
6. Be testable against the measured behavior of Khoj and Hermes

---

## Roadmap

### Phase 0 — Overlay foundation
- Installer/uninstaller scripts
- Module manifest format
- Cross-platform smoke tests
- Documentation

### Phase 1 — High-impact product features
- Obsidian client adapter
- Emacs client adapter
- Image generation core module
- TTS playback module

### Phase 2 — Knowledge and data products
- pgvector semantic search / RAG
- Stable JSON chat export with pagination
- Exa web-page reader

### Phase 3 — Productivity and access
- Newsletter + smart notification scheduling
- Phone app companion client
- Enterprise cloud / on-prem / hybrid deployment layer

---

## Contributing

This repository is intentionally public and open to contributions.

Good first steps:

- Review the measured Khoj/Hermes gap list above
- Propose a module design for one of the nine core deliverables
- Add tests that compare behavior against Khoj or Hermes
- Help define the overlay manifest format

---

## License

TBD — likely MIT or Apache-2.0.

---

## Upstream Projects

- **Nous Research Hermes Agent OS** — the agentic core this overlay extends
- **Khoj** — the product-layer capabilities Jane OS measures itself against
- **bescritt/hermes-brain** — source of the measured Hermes advantages and overlap data
