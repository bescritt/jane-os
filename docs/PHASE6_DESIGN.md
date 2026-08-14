# Phase 6 Design Document — Jane OS

> **Status:** Planning (no implementation). Extrapolated from IDEA.md §39-48 success criteria,
> §81 Contributing, and the natural evolution beyond the platform layer.
> **Scope:** What comes after Phase 5 — the maturity and scale layer.

## Overview

IDEA.md's roadmap ends at Phase 3 (§74). The extrapolation chain:
- **Phase 4:** Product platform (community marketplace)
- **Phase 5:** Measurement layer (analytics, OSS graduation, monetization, cross-platform, governance)
- **Phase 6:** Maturity + scale — the layer that turns Jane OS from a project into a sustainable
  ecosystem

Phase 6 is the "beyond the scaffold" layer: how Jane OS operates at scale with community
contribution, distributed intelligence, and long-term sustainability.

## Five Core Themes

1. **Distributed Intelligence Network** — multi-user, cross-machine intelligence sharing
2. **Plugin Architecture 2.0** — dynamic module loading without restart
3. **Long-Form Session Persistence** — sessions longer than single agent lifecycle
4. **Performance Benchmarking Suite** — measurable parity against commercial alternatives
5. **Community Infrastructure** — forums, documentation portal, contributor onboarding pipeline

---

## 1.0 Distributed Intelligence Network

### 1.1 Overview
Phase 4's marketplace enables module sharing. Phase 5's analytics tracks local metrics.
Phase 6 extends this to a **distributed intelligence network** — users can optionally share
anonymized insights across the network, and agents can collaborate across machines beyond
the LAN mesh (Phase 4.3).

Per IDEA.md §16 ("not a duplicate of features Hermes already has, unless they need to be
productized"), this productizes the existing `hermes-lan-mesh` skill's discovery pattern
into a broader network.

### 1.2 Architecture
```
[Local Agent (Jane OS)]
  ├── Analytics tracker (Phase 5) → emits anonymized metrics
  ├── Module marketplace (Phase 4) → shares module success rates
  ├── Shared memory (Phase 4.3) → peer-to-peer memory sharing
  └── Network sync → push anonymized insights to central aggregator
         │
         ▼
[Network Aggregator]
  ├── Collect anonymized module success rates (no session content)
  ├── Compute global model performance benchmarks
  ├── Distribute: best-practice configs + popular modules
  └── Publish: public dashboards (khoj-parity metrics)
```

### 1.3 Integration Points
- **`analytics-tracker`** (Phase 5): source of anonymized metrics
- **`module-marketplace`** (Phase 4): module success rates + download counts
- **`hermes-lan-mesh` skill**: existing peer discovery pattern
- **`osint/secret-hygiene` skill**: ensure no PII in shared data
- **`hermes-features-reference`** skill: network protocol patterns

### 1.4 Implementation
| Step | Description | Est. Effort |
|---|---|---|
| P6-1.1 | Design anonymized metrics schema (opt-in) | 1.5 |
| P6-1.2 | Build network sync client (push to aggregator) | 2.5 |
| P6-1.3 | Build central aggregator (central server) | 4.0 |
| P6-1.4 | Public dashboard (KPI visualization) | 2.5 |
| **Total** | | **10.5 units** |

### 1.5 Risks
- R-P6-1: Privacy violation → mitigation: zero-trust anonymization at source (Phase 5 analytics already strips session content)
- R-P6-2: Network dependency → mitigation: fully functional offline, sync is additive

---

## 2.0 Plugin Architecture 2.0

### 2.1 Overview
Currently, modules are installed by copying files (`cli.py install`). Phase 6 enables
**dynamic module loading** — modules can be loaded/unloaded without restarting the Hermes
agent, using Python's `importlib` + plugin discovery.

### 2.2 Architecture
```
[Plugin Manager]
  ├── Discovery: scan ~/.jane_installed/*/manifest.json
  ├── Loading: importlib.util.spec_from_file_location
  ├── Lifecycle: on_load() / on_unload() hooks
  ├── Isolation: each module in its own namespace
  └── Hot-reload: reload on file change (watchdog)
         │
         ▼
[Module Interface]
  ├── manifest.json: extends, permissions, hooks
  ├── hooks.py (optional): on_load, on_unload, on_message
  └── config.json (optional): module-specific settings
```

### 2.3 Integration Points
- **Hermes skill system**: existing skill discovery pattern (`skill_utils.iter_skill_index_files`)
- **`hermes-desktop-plugins` skill**: desktop plugin patterns
- **`tiered_memory` system** (Tenet 4): module state persistence

### 2.4 Implementation
| Step | Description | Est. Effort |
|---|---|---|
| P6-2.1 | Design plugin interface (hooks + manifest extensions) | 2.0 |
| P6-2.2 | Build plugin manager (importlib + lifecycle hooks) | 3.0 |
| P6-2.3 | Hot-reload support (file watching) | 1.5 |
| P6-2.4 | Migration: convert existing 7 modules to plugin format | 2.0 |
| **Total** | | **8.5 units** |

### 2.5 Risks
- R-P6-3: Module conflicts (namespace pollution) → mitigation: isolated namespaces + permission model
- R-P6-4: Hot-reload instability → mitigation: sandbox each module, restart on crash

---

## 3.0 Long-Form Session Persistence

### 3.1 Overview
Current Hermes sessions can be long but are single-agent-lifecycle. Phase 6 enables
**long-form sessions** that persist across agent restarts, with state checkpointing and
resume capability. This productizes the existing tiered memory system (Tenet 4) into a
user-facing capability.

### 3.2 Architecture
```
[Session State Manager]
  ├── Checkpoint: periodic snapshot of session state to ~/.jane/sessions/
  ├── Resume: restore session from checkpoint on agent restart
  ├── Migrate: handle schema changes between Hermes versions
  └── Archive: move old sessions to Tier 1 (longterm.db) per Tenet 4
         │
         ▼
[Checkpoint Format]
  ├── state.json: conversation + tool state + memory snapshots
  ├── messages.db: SQLite copy of messages table
  └── sha256: content hash for integrity verification
```

### 3.3 Integration Points
- **Ten-tenets Tiered Memory** (Tenet 4): Tier 1 (longterm.db) + Tier 2 (summarized) + Tier 3 (ephemeral)
- **`json-chat-export` module** (Phase 2): session serialization pattern
- **`self-improving-git-brain` skill**: git-backed state persistence pattern

### 3.4 Implementation
| Step | Description | Est. Effort |
|---|---|---|
| P6-3.1 | Design checkpoint format (versioned, content-hashed) | 2.0 |
| P6-3.2 | Build state saver (snapshot to ~/.jane/sessions/) | 2.5 |
| P6-3.3 | Build state restorer (resume from checkpoint) | 2.0 |
| P6-3.4 | Integrate with tiered memory (archive old sessions) | 1.5 |
| **Total** | | **8.0 units** |

### 3.5 Risks
- R-P6-5: State corruption on crash → mitigation: SHA256 content-hash checkpoint (Tenet 9)
- R-P6-6: Version migration failures → mitigation: schema-version-aware migration + rollback

---

## 4.0 Performance Benchmarking Suite

### 4.1 Overview
Per IDEA.md §46 ("be testable against the measured behavior of Khoj and Hermes"), Phase 6
builds a formal benchmarking suite that measures Jane OS modules against commercial
alternatives (Khoj, Obsidian, etc.) using standardized tests.

### 4.2 Architecture
```
[Benchmark Runner]
  ├── Test definitions: YAML files defining tasks + expected outputs
  ├── Execution: run module → capture output + timing + cost
  ├── Comparison: diff against baseline (Khoj/Hermes/Obsidian measured output)
  └── Report: HTML dashboard + JSON for CI
         │
         △
[Test Definitions]
  ├── search_speed.yaml: "Find 'quantum computing' in 50 notes < 2s"
  ├── export_format.yaml: "Export 1000 messages to JSON < 5s"
  ├── memory_recall.yaml: "Recall 'Debian 13' from state.db"
  ├── newsletter_quality.yaml: "Newsletter contains ≥3 sessions"
  └── marketplace_search.yaml: "Publish + search 5 modules < 1s"
```

### 4.3 Integration Points
- **`analytics-tracker`** (Phase 5): metric collection patterns
- **`evaluating-llms-harness` skill**: existing benchmark harness patterns
- **`profiling-and-benchmarking` skill**: profiling patterns
- **CI pipeline** (Phase 0): benchmark runs in CI, results published to dashboard

### 4.4 Implementation
| Step | Description | Est. Effort |
|---|---|---|
| P6-4.1 | Define 10 benchmark test cases (search, export, memory, etc.) | 2.0 |
| P6-4.2 | Build benchmark runner (YAML + execution + timing) | 2.5 |
| P6-4.3 | Build comparison engine (against Khoj/Hermes baselines) | 2.0 |
| P6-4.4 | Build HTML report generator + CI integration | 2.0 |
| **Total** | | **6.5 units** |

### 4.5 Risks
- R-P6-7: Benchmarks become stale → mitigation: version + timestamp on all baselines
- R-P6-8: False parity claims → mitigation: judge_gate verification on all benchmark results

---

## 5.0 Community Infrastructure

### 5.1 Overview
Phase 4's marketplace and Phase 5's OSS graduation need supporting infrastructure: forums,
documentation portal, and a contributor onboarding pipeline. This completes the "platform"
vision.

### 5.2 Components
| Component | Description | Implementation |
|---|---|---|
| **Documentation Portal** | All design docs + module docs in searchable format | MkDocs + GitHub Pages |
| **Community Forum** | Discussion + support (vs GitHub Issues) | Discourse or GitHub Discussions |
| **Contributor Pipeline** | Good-first-issue → mentor → merge | GitHub issue labeling + CODEOWNERS |
| **Monthly Reports** | Phase 1 retrospective + roadmap progress | Newsletter module integration |

### 5.3 Integration Points
- **`newsletter-scheduler`** (Phase 3): monthly report generation
- **`github-repo-publish` skill**: GitHub Pages deployment for docs
- **`github-issues` skill**: issue + label management
- **`weekly-review-planning` skill**: monthly report patterns

### 5.4 Implementation
| Step | Description | Est. Effort |
|---|---|---|
| P6-5.1 | MkDocs setup + docs deployment (GitHub Pages) | 2.0 |
| P6-5.2 | GitHub Discussions setup + templates | 1.0 |
| P6-5.3 | Contributor pipeline (CODEOWNERS + issue templates) | 1.5 |
| P6-5.4 | Newsletter-based monthly report template | 1.0 |
| **Total** | | **4.5 units** |

### 5.5 Risks
- R-P6-9: Community doesn't form → mitigation: proactive outreach via newsletter
- R-P6-10: Docs become stale → mitigation: docs build in CI (break on missing refs)

---

## Phase 6 Dependency Graph

```
Phase 5 complete ──FS──> P6-1 (Distributed Network) ──FS──> P6-2 (Plugin Arch)
                          │                    └─FS─> P6-4 (Benchmarks)
                          └─FS─> P6-3 (Session Persistence) ──FS─> P6-5 (Community)
```

## Phase 6 Resource Requirements

| Resource | P6-1 | P6-2 | P6-3 | P6-4 | P6-5 |
|---|---|---|---|---|---|
| Python importlib | Yes | — | — | — | — |
| Network server | Yes | — | — | — | — |
| GitHub Pages | — | — | — | — | Yes |
| Khoj/Hermes baselines | — | — | — | Yes | — |
| Discourse/GitHub Discussions | — | — | — | — | Yes |

## Total Phase 6 Effort: 38.0 units across 5 themes

## Sequencing Recommendation

Phase 6 is **strategic infrastructure** — it transforms Jane OS from a scaffold into a
real platform. Recommended execution order:
1. **P6-3 (Session Persistence)** first — foundational, low-risk, high-value
2. **P6-2 (Plugin Arch)** second — enables cleaner module management
3. **P6-4 (Benchmarks)** third — provides measurement for all other improvements
4. **P6-1 (Distributed Network)** and **P6-5 (Community)** in parallel — both platform-scale

Phase 6 items are substantial (38 units total) and would span multiple sessions. They
should be executed as separate PROJECT-mode invocations, each gated by judge_gate +
smoke_test.
