# Phase 3 Design Document — Jane OS

> **Status:** Planning (no implementation). Per IDEA.md §73-75.
> **Scope:** Detailed design for the three Phase 3 enterprise/deployment items.

## Overview

Per IDEA.md §75, Phase 3 delivers the **enterprise tier** — a deployment layer
for Hermes + Jane, deployable across cloud/on-prem/hybrid. This document plans
all three Phase 3 items in detail.

## IDEA.md Phase 3 Roadmap (§73-75)

| Item | Description |
|---|---|
| Newsletter + smart notification scheduling | Curated content delivery with scheduling |
| Phone app companion client | Mobile companion for Jane OS |
| Enterprise cloud / on-prem / hybrid deployment layer | Enterprise-grade deployment infrastructure |

---

## 1.0 Newsletter + Smart Notification Scheduling

### 1.1 Overview
A curated content delivery system that aggregates Hermes session insights,
Jane OS module updates, and external research (via Exa/Exa reader) into
scheduled newsletters and smart notifications. Uses the existing Phase 2
JSON export as its content source.

### 1.2 Architecture

```
[Content Sources]
  ├── Hermes sessions (state.db via json-chat-export module)
  ├── Jane OS module updates (git log of bescritt/jane-os)
  ├── Exa web reader results (Phase 2 P2-3 corpus/)
  └── Obsidian vault notes (Phase 1 obsidian-adapter)
         │
         ▼
[Content Aggregator]
  ├── Extract key insights (summary via local LLM — llama-cpp)
  ├── Tag + categorize (tech / research / updates)
  ├── Deduplicate (content-hash cache per Tenet 9)
  └── Score relevance (recency + user feedback)
         │
         ▼
[Scheduler]
  ├── Cron-based scheduling (leveraging Hermes cronjob system)
  ├── User-configurable frequency (daily / weekly / custom)
  └── Time-zone aware (per user profile)
         │
         ▼
[Delivery Adapters]
  ├── Email (via himalaya skill — IMAP/SMTP)
  ├── Discord webhook (via Hermes gateway)
  ├── Telegram (via Hermes gateway)
  └── Obsidian daily note (via obsidian-adapter)
```

### 1.3 Integration Points
- **json-chat-export module** (Phase 2): content source — exported sessions provide conversation summaries
- **hermes cronjob system**: scheduling engine (per hermes-features-reference §4.4: `/cron`)
- **llama-cpp skill**: content summarization and relevance scoring
- **himalaya skill** (`email/himalaya`): email delivery
- **Hermes gateway**: Discord/Telegram/Slack delivery (per hermes-features-reference §1.1: 20+ platforms)

### 1.4 Implementation Steps

| Step | Description | Est. Effort |
|---|---|---|
| P3-1.1 | Design newsletter JSON schema (versioned) | 0.5 |
| P3-1.2 | Build content aggregator (read from state.db + corpus/) | 1.5 |
| P3-1.3 | Build scheduler (cron integration) | 1.0 |
| P3-1.4 | Build delivery adapters (email + gateway) | 1.5 |
| P3-1.5 | Build unsubscribe/preferences UI | 1.0 |
| **Total** | | **4.5 units** |

### 1.5 Dependencies
- Exa API key (for external content, or use DuckDuckGo fallback via offline-first)
- Email SMTP credentials (via himalaya skill)
- Hermes gateway configured on target platform(s)

### 1.6 Risks
- R-P3-1: Content overload → mitigation: user-configurable limits + relevance scoring
- R-P3-2: Email delivery failures → mitigation: delivery logs + fallback to Discord

---

## 2.0 Phone App Companion Client

### 2.1 Overview
A mobile companion app (iOS + Android) that syncs with a user's Hermes + Jane
OS instance, enabling remote session management, notification delivery, and
lightweight querying. Built as a progressive web app (PWA) for cross-platform
deployment, or native via React Native/Flutter for app-store distribution.

Per IDEA.md §74, this is Phase 3 — not a core requirement but a product-layer
capability. Approach: **PWA first** (lowest dev cost, runs everywhere), native
as Phase 3 stretch.

### 2.2 Architecture

```
[Phone App (PWA)]
  ├── Auth: JWT from Hermes gateway
  ├── API: REST/WS bridge to ~/.hermes/state.db (via local bridge)
  ├── Push: Web Push API for notifications
  └── Cache: IndexedDB for offline notes
         │
         ▼
[Hermes Local Bridge]
  ├── Secure reverse-proxy (nginx + JWT)
  ├── Exposes: /api/v1/sessions, /api/v1/messages, /api/v1/export
  ├── Reads: state.db (read-only)
  └── Writes: preferences, notification settings
```

### 2.3 Integration Points
- **Hermes gateway protocol**: authentication + message delivery (per hermes-features-reference §2)
- **json-chat-export module**: API endpoint for session data
- **obsidian-adapter**: API endpoint for vault notes
- **Hermes local bridge pattern**: see `desktop_ui` / `cua_browser` tools for local bridge patterns
- **PWA skills**: `creative/claude-design` (for UI prototyping), `creative/p5js` (for UI components)

### 2.4 Implementation Steps

| Step | Description | Est. Effort |
|---|---|---|
| P3-2.1 | Design REST API schema for session/message/export endpoints | 1.0 |
| P3-2.2 | Build local bridge server (Python http.server + JWT auth) | 2.0 |
| P3-2.3 | Build PWA frontend (HTML/CSS/JS, offline-first) | 3.0 |
| P3-2.4 | Add Web Push notification support | 1.5 |
| P3-2.5 | Mobile PWA install flow + manifest | 1.0 |
| **Total** | | **7.5 units** |

### 2.5 Dependencies
- HTTPS + JWT library (Python: `pyjwt`; JS: browser-native)
- No native SDKs if PWA approach
- Hermes gateway token for auth

### 2.6 Risks
- R-P3-3: Local bridge security exposure → mitigation: JWT auth + localhost binding + nginx TLS
- R-P3-4: Mobile browser limitations → mitigation: PWA install + service worker offline cache

---

## 3.0 Enterprise Cloud / On-Prem / Hybrid Deployment Layer

### 3.1 Overview
A deployment and orchestration layer for enterprise-scale Hermes + Jane OS,
supporting three deployment modes: **cloud** (hosted SaaS-like), **on-prem**
(self-hosted enterprise), and **hybrid** (local agent + cloud coordination).

### 3.2 Architecture

```
[Deployment Modes]
  ├── Cloud (hosted)
  │   ├── Central coordinator (multi-tenant)
  │   ├── Shared LLM inference (GPU cluster)
  │   ├── Centralized skill registry
  │   └── Tenant isolation (profiles)
  │
  ├── On-Prem (self-hosted)
  │   ├── Local gateway (single-tenant)
  │   ├── Local LLM inference (llama.cpp)
  │   ├── File-based skill registry (~/.hermes/skills/)
  │   └── Local state.db + memory
  │
  └── Hybrid
      ├── Local agent (on-prem profile)
      ├── Cloud coordinator (for scheduling / backup / multi-device sync)
      └── Sync bridge (encrypted, bidirectional)
         │
         ▼
[Shared Infrastructure]
  ├── Skill distribution (skill registry + versioning)
  ├── Session sync (across devices)
  ├── Credential management (vault-style)
  ├── Observability (metrics + logs)
  └── Billing (token usage tracking)
```

### 3.3 Integration Points
- **Hermes profile system**: multi-tenant isolation (per hermes-features-reference §1.3)
- **Hermes local bridge / desktop**: deployment target
- **Tiered memory system**: state persistence across deployments (Tenet 4)
- **Ten-tenets hardening**: offline-first, fail-closed judge, content-hash cache
- **Existing skills**: all 171 skills become distributable units in the registry

### 3.4 Implementation Steps

| Step | Description | Est. Effort |
|---|---|---|
| P3-3.1 | Design deployment manifest format (YAML) | 1.5 |
| P3-3.2 | Build local deployment runner (bash + python) | 2.0 |
| P3-3.3 | Build cloud coordinator (API server, multi-tenant) | 4.0 |
| P3-3.4 | Build hybrid sync bridge (encrypted) | 3.0 |
| P3-3.5 | Skill distribution + versioning registry | 2.5 |
| P3-3.6 | Observability stack (metrics + logs) | 2.0 |
| P3-3.7 | Documentation + deployment guides | 1.5 |
| **Total** | | **16.5 units** |

### 3.5 Dependencies
- Cloud provider account (AWS/GCP/Azure) for cloud mode
- Docker + Kubernetes for containerized deployment
- TLS certificates (Let's Encrypt)
- OAuth provider (for enterprise SSO)

### 3.6 Risks
- R-P3-5: Multi-tenant security isolation → mitigation: strict profile isolation + audit
- R-P3-6: Data sync conflicts → mitigation: CRDT-style conflict resolution + user mediation
- R-P3-7: Cloud vendor lock-in → mitigation: cloud-agnostic abstractions (Docker + standard APIs)

---

## 4.0 Phase 3 Dependency Graph

```
Phase 3.1 (Newsletter)
  ├── json-chat-export (Phase 2) ──► state.db
  ├── llama-cpp (embeddings/summary)
  ├── himalaya (email)
  └── Hermes cronjob + gateway (scheduling + delivery)

Phase 3.2 (Phone App)
  ├── json-chat-export API
  ├── obsidian-adapter API
  ├── Hermes gateway auth
  └── PWA frontend

Phase 3.3 (Enterprise Deploy)
  ├── Profile system (isolation)
  ├── Skill registry (distribution)
  ├── Tiered memory (state sync)
  ├── Ten-tenets hardening (fail-closed, offline-first)
  └── Local bridge (deployment target)
```

## 5.0 Phase 3 Resource Requirements

| Resource | P3.1 | P3.2 | P3.3 |
|---|---|---|---|
| PostgreSQL | Not needed | Optional (for sync) | Required (central store) |
| Exa API key | Optional | Not needed | Optional |
| Email SMTP | Required | Not needed | Required |
| HTTPS/TLS | Required | Required | Required |
| Docker/K8s | Not needed | Not needed | Required |
| Cloud account | Not needed | Not needed | Required |
| sudo | No | No | No (user-local) |

## 6.0 Phase 3 Sequencing

```
Phase 2 complete ──FS──> P3-2 (Phone App) ──FS──> P3-1 (Newsletter)
                              │                      └─FS─> P3-3 (Enterprise)
                              └────────────────────────┘
```

**Rationale:** P3-2 (Phone App) and P3-1 (Newsletter) share the json-chat-export
API as their content source. P3-3 (Enterprise) is independent and can start
once the local bridge pattern is established. P3-1 and P3-2 can be built in
parallel (both consume Phase 2's export module).
