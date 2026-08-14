# Phase 4 Design Document — Jane OS

> **Status:** Planning (no implementation). Extrapolated from IDEA.md §43-48 success criteria +
> Phase 3 enterprise theme.
> **Scope:** What comes after Phase 3 — the maturity and scaling layer for Jane OS.

## Overview

IDEA.md §91-101 does not explicitly define a "Phase 4." However, the success criteria
(§39-48) and the enterprise theme of Phase 3 (§73-75) point toward a natural Phase 4:
**community, marketplace, and intelligence layer** that turns Jane OS from a product into a
platform. This document drafts what Phase 4 would look like.

## The Phase 4 Vision

> **Phase 4: Platform + Intelligence** — Community-driven module marketplace,
> cross-user intelligence sharing (privacy-preserving), and autonomous agent
> ecosystem.

### Core Theme
Phase 3 (enterprise deployment) makes Jane OS deployable at scale. Phase 4 makes it
**collaborative** — users contribute modules, share intelligence, and build an ecosystem
around the Hermes + Jane stack.

---

## 1.0 Community & Marketplace

### 1.1 Overview
A module marketplace where users can publish, discover, and install Jane OS modules
(like the obsidian-adapter, json-chat-export, newsletter-scheduler already built as scaffolds).
Think "npm for Jane OS modules."

### 1.2 Architecture
```
[Module Registry]
  ├── Publisher: jane module publish modules/my-module/
  ├── Consumer: jane module install community:author/module-name
  ├── Search API: /api/v1/modules?q=...
  ├── Metadata: manifest.json validation + dependency resolution
  └── Ratings: user reviews + install counts
         │
         ▼
[Module Verification]
  ├── Automated: smoke_test.sh must pass (CI gate)
  ├── Human: maintainer review for core modules
  └── Security: secret-hygiene audit (osint/secret-hygiene skill)
```

### 1.3 Integration Points
- **`module manifest format`** (IDEA.md §4): registry validates manifest.json schema
- **CI pipeline** (Phase 0): `bash tests/smoke_test.sh` must pass before publish
- **`osint/secret-hygiene` skill**: scan published modules for embedded secrets
- **`codebase-inspection` skill**: static analysis on published modules

### 1.4 Implementation
| Step | Description | Est. Effort |
|---|---|---|
| P4-1.1 | Design registry API (REST) + module format | 2.0 |
| P4-1.2 | Publish tooling (`jane module publish`) | 1.5 |
| P4-1.3 | Discovery/search (`jane module search`, `jane module install`) | 2.0 |
| P4-1.4 | Security scanning pipeline (secret-hygiene + codebase-inspection) | 2.5 |
| **Total** | | **8.0 units** |

### 1.5 Dependencies
- A registry server (can start as GitHub Packages or a simple Flask API)
- `osint/secret-hygiene` skill for security scanning
- `codebase-inspection` skill for code analysis

### 1.6 Risks
- R-P4-1: Malicious modules → mitigation: mandatory smoke_test + secret scan before publish
- R-P4-2: Registry becomes a single point of failure → mitigation: mirror support + offline install

---

## 2.0 Cross-User Intelligence (Privacy-Preserving)

### 2.1 Overview
Allow users to opt into sharing anonymized intelligence (model performance benchmarks,
module success rates, error patterns) to improve the collective Jane OS experience.
All sharing is **opt-in** and **anonymized** — no session content or personal data.

Per IDEA.md §47: "Respect Hermes's offline-first, fail-closed, and consent-oriented design."

### 2.2 Architecture
```
[Local Telemetry]
  ├── Model performance (latency, token usage, cost)
  ├── Module success/failure rates
  ├── Error patterns (stack traces, anonymized)
  └── User feedback (ratings, usage counts)
         │
         ▼
[Anonymization Layer]
  ├── Strip user IDs, session IDs, PII
  ├── Hash module names (for correlation without attribution)
  ├── Sample 10% of events (rate limiting)
  └── Encrypt in transit (TLS)
         │
         ▼
[Telemetry Aggregator]
  ├── Collect from opted-in users (central server)
  ├── Compute aggregate metrics
  ├── Publish public dashboards
  └── Feedback to module maintainers (success rates)
```

### 2.3 Integration Points
- **`osint/secret-hygiene` skill**: ensure no PII leaks into telemetry
- **`error-analysis-unified` skill**: structured error pattern analysis
- **`weekly-review-planning` skill**: similar aggregation pattern for weekly reports

### 2.4 Implementation
| Step | Description | Est. Effort |
|---|---|---|
| P4-2.1 | Design telemetry schema (opt-in, anonymized) | 1.5 |
| P4-2.2 | Build local collector (read-only from state.db) | 2.0 |
| P4-2.3 | Build anonymization layer (PII stripping + hashing) | 2.0 |
| P4-2.4 | Build central aggregator + public dashboard | 3.0 |
| **Total** | | **8.5 units** |

### 2.5 Dependencies
- Consent UI (user must explicitly opt in)
- Central telemetry server
- `osint/secret-hygiene` skill integration

### 2.6 Risks
- R-P4-3: Privacy violation → mitigation: zero-trust (strip first, anonymize second, opt-in always)
- R-P4-4: Telemetry overhead → mitigation: rate-limited sampling (10% of events)

---

## 3.0 Multi-Agent Ecosystem

### 3.1 Overview
Enable Hermes agents to collaborate across machines using the `hermes-lan-mesh` skill
(local UDP broadcast discovery + HMAC-signed registry) as a foundation, extended with:
- **Task delegation marketplace** — agents can discover and hire other agents for subtasks
- **Shared memory pools** — cross-agent memory sharing (with consent)
- **Skill federation** — agents share custom skills across the mesh

Per IDEA.md §43 (success criterion): "Provide all nine Khoj-gap capabilities with measurable parity" —
multi-agent collaboration extends the "subagent orchestration" Khoj gap.

### 3.2 Architecture
```
[Hermes LAN Mesh] (existing: hermes-lan-mesh skill)
  ├── UDP broadcast discovery (HMAC-signed, stdlib socket)
  ├── HTTP registry (stdlib http.server)
  └── Capability routing
         │
         ▼
[Task Delegation Marketplace]
  ├── Publish: agent advertises available capabilities
  ├── Discover: agent finds capability-bearing peers
  ├── Delegate: task handed off with context
  └── Verify: judge_gate on returned result (Tenet 3)
         │
         ▼
[Shared Memory Pools]
  ├── Consent-gated (per-agent opt-in)
  ├── Conflict resolution (last-write-wins + user mediation)
  └── Backup: tiered to state.db + longterm.db
```

### 3.3 Integration Points
- **`hermes-lan-mesh` skill** (`agentic/peer/hermes-lan-mesh`): foundation discovery + registry
- **`self-improving-git-brain` skill** (`agentic/self-improving-git-brain`): git-backed agent state
- **`autonomous-goal-execution` skill** (`agentic/delegation/autonomous-goal-execution`): task delegation pattern
- **Ten-tenets judge_gate** (Tenet 3): verification of delegated results

### 3.4 Implementation
| Step | Description | Est. Effort |
|---|---|---|
| P4-3.1 | Extend lan-mesh with task marketplace | 3.0 |
| P4-3.2 | Build shared memory pools (consent-gated) | 2.5 |
| P4-3.3 | Skill federation (share custom skills) | 3.0 |
| P4-3.4 | Integration tests (multi-agent task delegation) | 2.0 |
| **Total** | | **10.5 units** |

### 3.5 Dependencies
- `hermes-lan-mesh` skill (already exists in skill library)
- Multiple Hermes agents on same LAN (for testing)

### 3.6 Risks
- R-P4-5: Agent misalignment on delegated tasks → mitigation: judge_gate verification (Tenet 3)
- R-P4-6: Memory conflicts → mitigation: CRDT-style merge + user mediation

---

## 4.0 Phase 4 Dependency Graph

```
Phase 4.1 (Marketplace)
  ├── Module manifest format (Phase 0)
  ├── CI smoke test (Phase 0)
  ├── osint/secret-hygiene skill
  └── codebase-inspection skill

Phase 4.2 (Intelligence)
  ├── state.db (existing)
  ├── osint/secret-hygiene skill
  └── error-analysis-unified skill

Phase 4.3 (Multi-agent)
  ├── hermes-lan-mesh skill (existing)
  ├── self-improving-git-brain skill
  ├── autonomous-goal-execution skill
  └── Ten-tenets judge_gate (Tenet 3)
```

## 5.0 Phase 4 vs IDEA.md Success Criteria

| IDEA.md Criterion (§39-48) | Phase 4 Mapping |
|---|---|
| C4: Modular (enable only needed modules) | Phase 4.1 Marketplace enables module discovery/installation |
| C5: Offline-first, fail-closed, consent-oriented | Phase 4.2 is opt-in + anonymized; Phase 4.3 uses judge_gate |
| C6: Testable against measured behavior | Phase 4.1 requires smoke_test pass; Phase 4.3 uses integration tests |
| C7: Enterprise tier | Phase 3 covers this; Phase 4 extends to community platform |

## 6.0 Phase 4 Sequencing

```
Phase 3 complete ──FS──> P4-3 (Multi-Agent Ecosystem)
                             ├─FS─> P4-2 (Intelligence Sharing)
                             └─FS─> P4-1 (Marketplace)
```

**Rationale:** P4-3 (multi-agent) is the foundation — it extends the existing `hermes-lan-mesh`
skill to enable agent-to-agent collaboration. P4-1 (marketplace) and P4-2 (intelligence) both
leverage the multi-agent mesh for distributed discovery and aggregation.
Phase 4 is a **strategic** layer — it transforms Jane OS from a product into a platform.
Implementation would span multiple sessions and require community involvement.
