# Phase 5 Design Document — Jane OS

> **Status:** Planning (no implementation). Extrapolated from IDEA.md §39-48 success criteria,
> §81 Contributing section, and the natural evolution of the platform theme.
> **Scope:** What comes after Phase 4 — the product-completion layer.

## Overview

IDEA.md's roadmap ends at Phase 3 (§74). Phases 4 and 5 are extrapolations from the success
criteria (§39-48) and the Contributing section (§81):

- **Phase 4** = Product platform (community marketplace, as implemented)
- **Phase 5** = Product completion (analytics, monetization, open-source graduation, ecosystem
  governance)

Phase 5 completes the vision: a self-sustaining, community-driven, open-source platform that
competes with commercial alternatives (Khoj, Obsidian, etc.) through measurable parity (IDEA.md §41).

## Five Core Themes

1. **Analytics & Measurement** — Close the loop on IDEA.md §46 ("be testable against measured
   behavior"). Build telemetry that can *measure* the 9 Khoj-gap capabilities (§41-43).
2. **Open Source Graduation** — Move from single-author scaffold to community-owned project
   (license, docs, governance, contributor pipeline). Per IDEA.md §81 ("intentionally public and
   open to contributions").
3. **Monetization / Sustainability** — How maintainers and contributors sustain the project
   long-term (sponsorships, premium hosting, enterprise support).
4. **Cross-Platform Testing Matrix** — Satisfy IDEA.md §45 ("install and uninstall cleanly on
   Windows, macOS, and Linux"). Currently only tested on Linux.
5. **Ecosystem Governance** — Module approval process, security review, version compatibility
   matrix, deprecation policy.

---

## 1.0 Analytics & Measurement Layer

### 1.1 Overview
The success criteria require "measurable parity" with Khoj's 9 capabilities (§41). Phase 5
builds the instrumentation layer that *measures* this parity, closing the loop on
IDEA.md §46 ("be testable against the measured behavior of Khoj and Hermes").

### 1.2 Architecture
```
[Hermes Sessions (state.db)]
  ├── Extract usage metrics (tokens, cost, duration)
  ├── Extract capability invocation (which modules used)
  └── Extract user feedback (explicit ratings via CLI)
         │
         ▼
[Khoj Gap Metrics]
  ├── For each of 9 capabilities: pass/fail + quality score
  ├── Compare against Khoj behavior (from hermes-brain data)
  └── Produce parity dashboard
         │
         ▼
[Analytics Store]
  ├── Local SQLite: ~/.jane/analytics.db
  ├── Sync: optional (opt-in telemetry, Phase 4)
  └── Export: JSON for CI/CD integration
```

### 1.3 Integration Points
- **json-chat-export module** (Phase 2): provides the session export pipeline
- **state.db** (Hermes): source of all session metrics
- **hermes-subgoals-delegation skill**: tracks subagent task success (capability proxy)
- **frontend**: `hermes-features-reference` skill (§5: CLI commands + TUI)

### 1.4 Implementation Steps
| Step | Description | Est. Effort |
|---|---|---|
| P5-1.1 | Define 9 Khoj-gap capability metrics (from IDEA.md §22-35) | 2.0 |
| P5-1.2 | Build metrics collector (read state.db + module usage) | 2.5 |
| P5-1.3 | Build Khoj comparison engine (parity dashboard) | 3.0 |
| P5-1.4 | Build export (JSON + CI integration) | 1.5 |
| **Total** | | **9.0 units** |

### 1.5 Dependencies
- `hermes-features-reference` skill: for CLI metrics definitions
- IDEA.md §22-35: the 9 Khoj-gap capabilities (must re-read for exact definitions)

### 1.6 Risks
- R-P5-1: Metrics become vanity metrics → mitigation: tie to IDEA.md §41 success criteria
- R-P5-2: Telemetry privacy → mitigation: opt-in only, no session content

---

## 2.0 Open Source Graduation

### 2.1 Overview
IDEA.md §81 says the repo is "intentionally public and open to contributions." Phase 5
formalizes this: a real open-source project with governance, contributor pipeline, and
community health.

### 2.2 Architecture
```
[Project Governance]
  ├── LICENSE: MIT or Apache-2.0 (IDEA.md §93: "TBD")
  ├── CODE_OF_CONDUCT.md: Contributor Covenant
  ├── GOVERNANCE.md: RFC process, maintainer hierarchy, release cadence
  ├── SECURITY.md: vulnerability reporting + safe practices
  └── CONTRIBUTING.md: Good first issue, module template, test pipeline

[Documentation]
  ├── docs/ARCHITECTURE.md: 4-phase design + integration diagram
  ├── docs/COMPATIBILITY.md: module version matrix
  ├── docs/UPGRADING.md: migration guide
  └── Each module: README.md (already done for Phase 1-4 modules)

[CI/CD Enhancement]
  ├── test.yml: smoke_test.sh (already exists)
  ├── publish.yml: build + publish modules to registry on release
  ├── security.yml: secret-hygiene scan on PRs
  └── docs.yml: auto-deploy docs to GitHub Pages
```

### 2.3 Integration Points
- **`osint/secret-hygiene` skill**: PR security scan (secrets in code)
- **`codebase-inspection` skill**: code quality scan
- **`github-pr-workflow` skill**: PR automation
- **`github-repo-publish` skill**: release + Pages deployment

### 2.4 Implementation Steps
| Step | Description | Est. Effort |
|---|---|---|
| P5-2.1 | Finalize LICENSE (MIT per IDEA.md §93 "likely MIT") | 0.5 |
| P5-2.2 | Add CODE_OF_CONDUCT + SECURITY + GOVERNANCE | 1.5 |
| P5-2.3 | Expand CONTRIBUTING.md with module template | 1.0 |
| P5-2.4 | Enhance CI: security.yml + publish.yml workflows | 2.0 |
| P5-2.5 | docs/ARCHITECTURE.md (consolidate all design docs) | 1.5 |
| **Total** | | **6.5 units** |

### 2.5 Dependencies
- User's explicit decision on LICENSE (MIT vs Apache-2.0)
- GitHub for CI/CD workflows

### 2.6 Risks
- R-P5-3: Contributor pipeline doesn't activate → mitigation: "good first issue" labels + clear module template
- R-P5-4: Security vulnerabilities in published modules → mitigation: mandatory secret-hygiene scan on PR

---

## 3.0 Monetization / Sustainability

### 3.1 Overview
How the Jane OS project sustains long-term maintenance and development. Not a revenue engine
— a sustainability model for maintainers and contributors.

### 3.2 Models
| Model | Description | Implementation |
|---|---|---|
| **Sponsorships** | GitHub Sponsors + Open Collective for maintainers | Add `.github/FUNDING.yml` |
| **Premium Hosting** | Hosted Jane OS instances (managed registry, backup service) | Phase 3 enterprise infra reuse |
| **Enterprise Support** | Paid support contracts for enterprise deployments | Phase 3 enterprise customer base |
| **Training** | Workshop on building Jane OS modules | Content marketing |
| **Consulting** | Custom module development for enterprises | 1:1 service |

### 3.3 Implementation Steps
| Step | Description | Est. Effort |
|---|---|---|
| P5-3.1 | Add `.github/FUNDING.yml` (GitHub Sponsors + Open Collective) | 0.5 |
| P5-3.2 | Add "Sponsor" badge to README + CONTRIBUTING | 0.5 |
| P5-3.3 | Draft premium hosting offering (reuse Phase 3 infra) | 1.5 |
| P5-3.4 | Draft enterprise support SLA template | 1.0 |
| **Total** | | **3.5 units** |

### 3.6 Risks
- R-P5-5: Monetization alienates community → mitigation: clearly separate free (OSS) from paid (hosting/support) offerings

---

## 4.0 Cross-Platform Testing Matrix

### 4.1 Overview
IDEA.md §45: "Install and uninstall cleanly on Windows, macOS, and Linux."
Currently only Linux is tested. Phase 5 builds the CI matrix.

### 4.2 Architecture
```
[CI Matrix]
  ├── ubuntu-latest: tests/smoke_test.sh (Phase 5.2 already passing)
  ├── macos-latest:  tests/smoke_test.sh
  ├── windows-latest: tests/smoke_test.sh (requires .bat shim)
  └── Test: install.sh → smoke_test.sh → uninstall.sh → verify clean removal

[Install Script (install.sh)]
  ├── Already exists (Phase 0)
  ├── Extend: Windows .bat equivalent
  └── Extend: macOS .command equivalent
```

### 4.3 Integration Points
- `install.sh` + `uninstall.sh` (Phase 0) — tested on Linux, need macOS/Windows validation
- `tests/smoke_test.sh` — extend to verify install/uninstall clean

### 4.4 Implementation Steps
| Step | Description | Est. Effort |
|---|---|---|
| P5-4.1 | Add macos + windows CI matrix to ci.yml | 1.0 |
| P5-4.2 | Write Windows install.bat + uninstall.bat | 1.5 |
| P5-4.3 | Write macOS install.command + uninstall.command | 1.0 |
| P5-4.4 | Extend smoke_test to verify clean uninstall | 1.0 |
| **Total** | | **3.5 units** |

### 4.5 Dependencies
- macOS + Windows CI runners (GitHub Actions, no local testing possible)

### 4.6 Risks
- R-P5-6: Windows path issues → mitigation: use Pathlib + os.path.join throughout
- R-P5-7: macOS `.command` file permissions → mitigation: document `chmod +x` step

---

## 5.0 Ecosystem Governance

### 5.1 Overview
As the module marketplace grows (Phase 4), Jane OS needs governance for module quality,
security, and compatibility. This turns Jane OS from a personal scaffold into a platform.

### 5.2 Components
- **Module approval process:** community review + security scan + smoke_test gate
- **Version compatibility matrix:** module.json declares compatible Jane OS + Hermes versions
- **Deprecation policy:** 6-month notice + migration guide for deprecated modules
- **Security advisory system:** CVE-like process for module vulnerabilities

### 5.3 Integration Points
- **module-marketplace** (Phase 4): publish command adds `--review` flag for core modules
- **`osint/secret-hygiene` skill**: mandatory scan before publish
- **`codebase-inspection` skill**: quality gate
- **CI smoke_test.sh**: mandatory pass

### 5.4 Implementation Steps
| Step | Description | Est. Effort |
|---|---|---|
| P5-5.1 | Define module.version + jane_os_compat fields in manifest | 1.0 |
| P5-5.2 | Add review workflow to marketplace publish | 1.5 |
| P5-5.3 | Add deprecation notice system to marketplace search | 1.0 |
| P5-5.4 | Document governance policy (GOVERNANCE.md) | 1.0 |
| **Total** | | **3.5 units** |

### 5.5 Risks
- R-P5-8: Governance overhead blocks small contributions → mitigation: tiered review (core vs community modules)

---

## Phase 5 Dependency Graph

```
Phase 4 complete ──FS──> P5-1 (Analytics) ──FS──> P5-5 (Governance)
                   ├─FS─> P5-2 (OSS Graduation)
                   ├─FS─> P5-3 (Monetization)
                   └─FS─> P5-4 (Cross-Platform)
```

## Phase 5 Resource Requirements

| Resource | P5-1 | P5-2 | P5-3 | P5-4 | P5-5 |
|---|---|---|---|---|---|
| GitHub Actions (macOS/Windows runners) | No | Yes | No | Yes | No |
| himalaya CLI | No | No | No | No | No |
| state.db | Yes | No | No | No | No |
| Open Collective account | No | Yes | Yes | No | Yes |
| sudo | No | No | No | No | No |

## Total Phase 5 Effort: 25.5 units across 5 themes

## Sequencing Recommendation

Phase 5 is best executed as **5 parallel tracks** (each themed), coordinated by the
marketplace publish/review workflow (P5-5). P5-1 (Analytics) and P5-2 (OSS Graduation)
can run entirely in parallel. P5-3 (Monetization) depends on P5-2 (needs community).
P5-4 (Cross-Platform) is independent and can be done anytime.
