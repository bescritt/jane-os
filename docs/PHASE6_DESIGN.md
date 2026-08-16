# Phase 6 Design Document — Jane OS

> **Status:** Planning (no implementation). Extrapolated from IDEA.md §39-48 success criteria
> and §81 Contributing. Written as the second Wallace's Wheel iteration output.
> **Scope:** Beyond the platform layer — maturity and scale.

## Overview

IDEA.md's roadmap ends at Phase 3 (§74). The extrapolation chain:
- **Phase 4:** Product platform (community marketplace — implemented in Wheel iteration 1)
- **Phase 5:** Measurement layer (analytics, OSS graduation, monetization, cross-platform, governance)
- **Phase 6:** Platform maturity — the layer that makes Jane OS sustainable at scale

Phase 6 focuses on **operational excellence**: making the project production-ready, maintainable,
and scalable. Where Phases 0-5 built features and infrastructure, Phase 6 hardens the
platform for long-term community use.

## Four Core Themes

1. **Developer Experience (DX) Platform** — tooling, scaffolding, and workflows that make
   contributing to Jane OS frictionless
2. **Performance & Reliability** — profiling, benchmarking, and resilience testing
3. **Documentation Modernization** — automated docs, searchable architecture reference,
   interactive examples
4. **Release Automation** — versioned releases, changelog generation, module version pinning

---

## 1.0 Developer Experience (DX) Platform

### 1.1 Overview
Per IDEA.md §81 ("intentionally public and open to contributions"), Jane OS needs first-class
developer tooling. Phase 5.2 (OSS Graduation) adds the process documents; Phase 6 adds the
tools that make contributing effortless.

### 1.2 Architecture
```
[DX Toolkit]
  ├── module-init: scaffold a new module with template structure
  │     Generates: manifest.json, README.md (with extends declaration), scripts/
  ├── module-test: run module-specific tests + smoke test
  │     Validates: manifest.json schema, README has extends declaration, smoke test passes
  ├── module-lint: lint module code + check for anti-patterns
  │     Checks: snakeoil secrets (osint/secret-hygiene), unused deps, path traversal safety
  └── module-submit: package + prepare PR for review
          Validates: all gates pass → open PR with auto-generated description
```

### 1.3 Integration Points
- **`module-marketplace`** (Phase 4): reuse manifest validation for module-init template
- **`osint/secret-hygiene` skill**: module-lint secret scanning
- **`codebase-inspection` skill**: code quality metrics (pygount LOC, language detection)
- **`frontmatter_health_check.py`** (from projects-manage): YAML/JSON validation
- **`github-pr-workflow` skill**: PR automation for module-submit

### 1.4 Implementation
| Step | Description | Est. Effort |
|---|---|---|
| P6-1.1 | module-init: scaffold new module from template | 2.0 |
| P6-1.2 | module-test: validate manifest + README + smoke | 2.5 |
| P6-1.3 | module-lint: secret scan + quality check | 2.0 |
| P6-1.4 | module-submit: auto-PR with template description | 1.5 |
| **Total** | | **8.0 units** |

### 1.5 Risks
- R-P6-1: Tooling becomes its own maintenance burden → mitigation: keep scripts stdlib-only, test in CI
- R-P6-2: Template drift from actual module structure → mitigation: smoke_test validates all modules against template

### 1.6 Dependencies
- None new (all reuse existing Phase 0-5 modules)

### 1.7 Procurement Note (PMP Procurement KA)
All four commands represent build-vs-buy decisions: building in Python (stdlib) ensures zero
external dependencies. The make/buy call: building costs less than integrating an external
scaffolding tool (e.g., cookiecutter) because the module structure runs simpler than a
generic project template.

---

## 2.0 Performance & Reliability

### 2.1 Overview
Per IDEA.md §46 ("be testable against the measured behavior of Khoj and Hermes"), Phase 6
adds formal performance profiling and reliability testing. This productizes the Phase 5
analytics layer into actionable performance insights.

### 2.2 Architecture
```
[Profile Harness]
  ├── time-module: timed execution of each module command
  │     Measures: wall-clock time, exit code, output size
  ├── memory-module: peak memory usage per command
  │     Uses: /proc/self/status (Linux), resource module (stdlib)
  ├── cost-tracking: estimate cost per operation
  │     Uses: analytics-tracker cost metrics from state.db
  └── stress-module: repeated execution under load
          Tests: module marketplace publish/search under 100 concurrent operations

[Benchmark Suite]
  ├── search-speed-test: publish 5 modules + search 100 queries < 2s
  ├── export-size-test: export 100 sessions + validate JSON < 10s
  ├── analytics-collect-test: full analytics run < 5s
  └── newsletter-generate-test: generate newsletter from 50 sessions < 3s
```

### 2.3 Integration Points
- **`analytics-tracker`** (Phase 5): cost metrics + session data source
- **`profiling-and-benchmarking` skill**: existing profiling patterns
- **`evaluating-llms-harness` skill**: benchmark harness patterns
- **CI pipeline (Phase 0)**: benchmarks run in CI, alerts on regression

### 2.4 Implementation
| Step | Description | Est. Effort |
|---|---|---|
| P6-2.1 | Profile harness: time + memory + cost tracking | 3.0 |
| P6-2.2 | Benchmark suite: 4 benchmark tests (search, export, analytics, newsletter) | 2.5 |
| P6-2.3 | CI integration: benchmark regression alerts | 1.5 |
| P6-2.4 | Stress testing: marketplace under load | 2.0 |
| **Total** | | **9.0 units** |

### 2.5 Risks
- R-P6-3: Benchmarks become stale → mitigation: version + date on all baselines, fail CI on 10% regression
- R-P6-4: Memory profiling platform-specific → mitigation: Linux-only first, macOS/Windows secondary

---

## 3.0 Documentation Modernization

### 3.1 Overview
Per IDEA.md §48 ("be testable"), Phase 6 ensures documentation stays in sync with code.
This goes beyond Phase 3-5 design docs — it automates documentation so the docs never
drift.

### 3.2 Architecture
```
[Docs Pipeline]
  ├── auto-README: generate README.md from manifest.json + scripts/
  │     Extracts: extends, dependencies, permissions, usage examples
  ├── auto-API: generate CLI reference from --help output
  │     Runs: all CLI commands with --help, captures output → docs/cli_reference.md
  ├── auto-ARCHITECTURE: generate architecture diagram from module graph
  │     Parses: manifest.json dependencies → Mermaid diagram → docs/ARCHITECTURE.md
  └── auto-TUTORIALS: generate usage examples from smoke_test.sh
          Walks: each smoke test step → tutorial section in docs/
```

### 3.3 Integration Points
- **`module-marketplace`** (Phase 4): manifest.json is the source of truth
- **`architecture-diagram` skill**: Mermaid diagram generation
- **`documentation` skill**: existing docs quality patterns
- **`hermes-agent-skill-authoring` skill**: SKILL.md template patterns

### 3.4 Implementation
| Step | Description | Est. Effort |
|---|---|---|
| P6-3.1 | auto-README: README.md generation from manifest.json | 2.0 |
| P6-3.2 | auto-API: CLI reference from --help output | 1.5 |
| P6-3.3 | auto-ARCHITECTURE: Mermaid diagram from dependency graph | 2.5 |
| P6-3.4 | auto-TUTORIALS: usage examples from smoke_test.sh | 2.0 |
| **Total** | | **8.0 units** |

### 3.5 Risks
- R-P6-5: Generated docs less useful than hand-written → mitigation: generated docs serve as baseline, manual edits enhance (not replace)

---

## 4.0 Release Automation

### 4.1 Overview
Per IDEA.md §45 ("install and uninstall cleanly"), Phase 6 adds formal release management:
versioned releases with changelogs, module version pinning, and upgrade paths.

### 4.2 Architecture
```
[Release Pipeline]
  ├── version-bump: bump all module versions + core version
  │     Format: semver (MAJOR.MINOR.PATCH), tag in git
  ├── changelog-gen: auto-generate CHANGELOG.md from git log
  │     Parses: commit messages (conventional commits), groups by module
  ├── module-compat: verify module compatibility matrix
  │     Checks: manifest.json jane_os_compat field → current version
  └── publish-release: tag + GitHub release + module-marketplace registry update
          Actions: git tag, GitHub release API, registry-index.json update

[Version Pinning]
  ├── manifest.json: jane_os_compat: ">=1.0.0,<2.0.0"
  ├── install: check compatibility before install
  └── upgrade: notify on version mismatch, offer upgrade path
```

### 4.3 Integration Points
- **`module-marketplace`** (Phase 4): registry-index.json format extension for versions
- **`github-repo-publish` skill**: release + Pages deployment
- **`github-pr-workflow` skill**: release branch + PR
- **`CHANGELOG.md`** (Phase 0): existing changelog format

### 4.4 Implementation
| Step | Description | Est. Effort |
|---|---|---|
| P6-4.1 | version-bump + changelog-gen (conventional commits) | 2.5 |
| P6-4.2 | module-compat: version matrix + install-time check | 2.0 |
| P6-4.3 | publish-release: GitHub release + registry update | 2.0 |
| P6-4.4 | Upgrade system: detect + notify + migrate | 2.0 |
| **Total** | | **8.5 units** |

### 4.5 Risks
- R-P6-6: Breaking changes in semver → mitigation: MAJOR version bump + migration guide
- R-P6-7: Changelog drift from commit messages → mitigation: enforce conventional commits in CI

---

## Phase 6 Dependency Graph

```
Phase 5 complete ──FS──> P6-1 (DX Platform) ──FS──> P6-4 (Release Automation)
                      ├─FS─> P6-2 (Performance) ──> CI integration
                      ├─FS─> P6-3 (Docs Modernization)
                      └─FS─> P6-4 (Release Automation)
```

P6-1 (DX) and P6-3 (Docs) run in parallel. P6-2 (Performance) depends on P6-1 (profiling
tools enable benchmarks). P6-4 (Release) depends on P6-1 (DX platform defines the release
tooling template).

## Phase 6 Resource Requirements

| Resource | P6-1 | P6-2 | P6-3 | P6-4 |
|---|---|---|---|---|
| Python stdlib | Yes | Yes | Yes | Yes |
| osint/secret-hygiene CLI | Yes | — | — | — |
| GitHub Actions (macOS/Windows) | — | Yes | — | Yes |
| GitHub release API | — | — | — | Yes |
| /proc/self/status (Linux) | — | Yes | — | — |

## Total Phase 6 Effort: 33.5 units across 4 themes

## Sequencing Recommendation

Phase 6 is **maturity engineering** — it transforms Jane OS from a working prototype into a
production-ready open source project. Recommended execution order:

1. **P6-1 (DX Platform)** — 8.0 units: makes ALL other work easier, reduces friction
2. **P6-2 (Performance)** — 9.0 units: provides measurement baseline before docs/release
3. **P6-3 (Docs)** + **P6-4 (Release)** in parallel — 8.0 + 8.5 = 16.5 units

Phase 6 items execute as separate PROJECT-mode invocations (3-4 sessions), each
gated by judge_gate + smoke_test. This is the natural conclusion of the Wheel iteration:
the experiment revealed concrete improvements, and Phase 6 plans the systematic follow-up.
