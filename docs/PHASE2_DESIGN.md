# Phase 2 Design Document — Jane OS

> **Status:** Planning (no implementation). Per IDEA.md §67-69.
> **Scope:** Detailed design for three Phase 2 deliverables. Not built — planned.

## Executive Summary

Phase 2 of Jane OS (IDEA.md §67) has three items:
1. **pgvector semantic search / RAG**
2. **Stable JSON chat export with pagination**
3. **Exa web-page reader**

This document specifies the design, integration points, dependencies, and
estimation for each. All Phase 2 items integrate with existing Hermes Agent
capabilities — Jane OS is an overlay, not a replacement.

## Integration Anchors (Existing Hermes Skills)

Per the skill library (171 skills across 13 categories), the following existing
skills provide the integration surface for Phase 2:

| Phase 2 Item | Anchor Skill | Skill Path | Integration Point |
|---|---|---|---|
| pgvector RAG | llama-cpp | `~/.hermes/skills/llm/inference/llama-cpp` | `Llama(embedding=True)` → `llm.embed("text")` produces vectors |
| JSON chat export | hermes-features-reference | `~/.hermes/skills/agentic/agents/hermes-features-reference` | `~/.hermes/state.db` is the SQLite session store; sessions under `~/.hermes/sessions/` |
| Exa reader | web-research-custody + blocked-page-recovery | `~/.hermes/skills/web-research-custody`, `research/blocked-page-recovery` | `web_search` supports Exa backend; recovery ladder (Wayback → archive.today → Jina) |

Additional relevant skills:
- `knowledge/llm-wiki` — interlinked markdown KB (RAG pattern reference)
- `osint/input-hardening` — input validation for untrusted URLs
- `osint/secret-hygiene` — credential handling (Exa API key)

---

## 1.0 pgvector Semantic Search / RAG

### 1.1 Overview
Provide semantic similarity search over Jane OS's knowledge store (Hermes session notes,
Obsidian vault content, Exa-extracted pages) using local embeddings via llama.cpp,
stored and indexed in PostgreSQL with the pgvector extension.

### 1.2 Architecture

```
[Jane Content Sources]
  ├── Hermes sessions (~/.hermes/sessions/)
  ├── Obsidian vault (~/.obsidian/ or $OBSIDIAN_VAULT_PATH)
  └── Exa-extracted pages (corpus/)
         │
         ▼
  [Embedding Pipeline]
         │  llama.cpp: Llama(embedding=True).embed(text)
         │  (skill: llm/inference/llama-cpp)
         ▼
  [pgvector Store]   (PostgreSQL + pgvector extension)
    Table: jane_documents
      - id (serial)
      - content (text)
      - embedding (vector(768) or model-dim)
      - source (enum: hermes_session | obsidian | exa)
      - metadata (jsonb: path, timestamp, tags)
  ┌─────────────────┐
  │ Index: IVFFlat   │  for similarity search
  └─────────────────┘
         │
         ▼
  [Query Interface]
         │  Python: psycopg2 / pgvector driver
         ▼
  [Hermes Tool / CLI]
    jane vector search "<query>"
```

### 1.3 Implementation Steps (Phase 2 is PLAN only — this is the future WBS)

| Step | Description | Integration |
|---|---|---|
| P2-1.1 | Set up PostgreSQL instance (local) | System dependency (apt: postgresql, postgresql-contrib) |
| P2-1.2 | Install pgvector extension | `CREATE EXTENSION vector;` |
| P2-1.3 | Build embedding pipeline using `llama_cpp.Llama(embedding=True)` | Calls into `llama-cpp` skill workflow |
| P2-1.4 | Create `jane_documents` table schema | Content from Hermes sessions + Obsidian vault + Exa corpus |
| P2-1.5 | Build indexing CLI command (`jane vector index`) | Scans `~/.hermes/sessions/`, Obsidian vault, corpus/ |
| P2-1.6 | Build search CLI command (`jane vector search "<q>"`) | Returns top-K matches with scores |
| P2-1.7 | Expose as Hermes tool call (optional) | `vector_search(query: str) -> list[dict]` |

### 1.4 Embedding Model Selection
Per `llama-cpp` skill guidance:
- **Default:** `nomic-ai/nomic-embed-text-v1.5` (768-dim, quantizable to Q4_K_M, CPU-friendly)
- **Alternative:** `thenlper/gte-large` (1024-dim, higher quality, more compute)
- Quant: Q4_K_M (general purpose, per llama-cpp skill recommendation)

### 1.5 Dependencies
- **System:** PostgreSQL 16+, pgvector extension
- **Python:** `psycopg2-binary`, `pgvector` (pip/uv)
- **Model weights:** Nomic embed GGUF (HuggingFace Hub download)
- **Skills:** llama-cpp (already available)

### 1.6 Estimation
| Step | Effort | Notes |
|---|---|---|
| P2-1.1 | 0.5 unit | Local PostgreSQL setup |
| P2-1.2–P2-1.4 | 1.0 unit | Schema + extension |
| P2-1.5–P2-1.6 | 1.5 units | Embedding pipeline + CLI |
| P2-1.7 | 1.0 unit | Hermes tool integration |
| **Total** | **4.0 units** | CPU-bound embedding; batch indexing is the bottleneck |

### 1.7 Risks
- R-P2-1: CPU embedding is slow (minutes for hundreds of documents) — mitigation: batch + progress
- R-P2-2: pgvector index accuracy depends on IVF nlist — mitigation: default nlist=100, tunable

---

## 2.0 Stable JSON Chat Export with Pagination

### 2.1 Overview
Export Hermes Agent conversation sessions to stable, paginated JSON format for
external consumption (analytics, backup, integration with other tools).

### 2.2 Data Source
Per `hermes-features-reference` skill (§6: Key Paths):
- `~/.hermes/state.db` — SQLite session store (primary data source)
- `~/.hermes/sessions/` — Session transcripts (raw, human-readable)

The SQLite DB is the structured source of truth; session files are supplementary.

### 2.3 JSON Schema

```json
{
  "version": "1.0",
  "exported_at": "2026-08-14T12:00:00Z",
  "sessions": [
    {
      "session_id": "20260722_204335_d62c16",
      "title": "Build Jane OS scaffold",
      "created_at": "2026-08-14T12:26:00Z",
      "updated_at": "2026-08-14T12:45:00Z",
      "profile": "default",
      "messages": [
        {
          "role": "user",
          "content": "Create a public GitHub repo...",
          "timestamp": "2026-08-14T12:26:00Z"
        },
        {
          "role": "assistant",
          "content": "...",
          "timestamp": "2026-08-14T12:28:00Z"
        }
      ]
    }
  ],
  "pagination": {
    "offset": 0,
    "limit": 50,
    "total_sessions": 127,
    "has_more": true
  }
}
```

### 2.4 CLI Design

```bash
# Export all sessions to a single JSON file (paginated internally)
python3 src/cli.py export --format json --output sessions.json

# Export with pagination (manual control)
python3 src/cli.py export --format json --offset 0 --limit 50 --output page1.json

# Export a single session
python3 src/cli.py export --format json --session-id 20260722_204335_d62c16 --output session.json
```

### 2.5 Implementation Steps

| Step | Description | Integration |
|---|---|---|
| P2-2.1 | Read session data from `~/.hermes/state.db` | SQLite query: `SELECT * FROM sessions` |
| P2-2.2 | Define JSON schema (versioned, stable) | Contract: must not break between versions |
| P2-2.3 | Implement pagination logic (offset/limit) | SQL `LIMIT ? OFFSET ?` |
| P2-2.4 | Implement single-session export | SQL `WHERE session_id = ?` |
| P2-2.5 | Implement bulk export | Stream to file, memory-safe |
| P2-2.6 | Add CLI endpoint to `src/cli.py` | `export` subcommand |

### 2.6 Stability Guarantees
- Schema includes `version` field for forward compatibility
- New fields added only as optional (never removed or renamed)
- Export is read-only — no writes to `state.db`
- Pagination metadata always included

### 2.7 Dependencies
- **Python:** `sqlite3` (stdlib), `json` (stdlib), `pathlib` (stdlib)
- **Skills:** hermes-features-reference (for state.db schema reference)
- **No external services** — pure local SQLite read

### 2.8 Estimation
| Step | Effort |
|---|---|
| P2-2.1–P2-2.3 | 1.0 unit |
| P2-2.4–P2-2.6 | 1.5 units |
| **Total** | **2.5 units** |

### 2.9 Risks
- R-P2-3: state.db schema may change between Hermes versions — mitigation: query defensively, schema-version check
- R-P2-4: Large sessions may exceed memory — mitigation: stream output, don't load all messages at once

---

## 3.0 Exa Web-Page Reader

### 3.1 Overview
Integrate Exa API (search + content extraction) as a Jane OS module that fetches
web content and stores it as Jane notes, with a fallback chain for resilience.

### 3.2 Architecture

```
[User Query]
     │
     ▼
[Exa API Client]          (requires EXA_API_KEY)
     │  Search → get results with content
     ├─ if Exa fails ──┐
     ▼                │
[Fallback Ladder]      │  (per blocked-page-recovery skill)
     │                 │
     ├── Wayback (archive.org)  │
     ├── archive.today          │  (per recovery skill §2-3)
     ├── Jina Reader (if key)   │
     └── Real browser (last)    │
     │                        │
     ▼                        │
[Content Parser]             │
     │  Strip HTML → Markdown │
     ▼                        │
[Jane Note Storage]          │
     │  Store as .md in       │
     │  corpus/ or Obsidian   │
     └────────────────────────┘
```

### 3.3 Integration with blocked-page-recovery skill
The `blocked-page-recovery` skill (§: "The ladder") defines a proven 5-step
fallback: Wayback → archive.today → Jina Reader → API-first → real browser.
The Exa reader adopts this exact ladder as its recovery chain when Exa returns
4xx/5xx or content is unavailable. This reuses a verified pattern (the skill's
script `scripts/recover_page.py` proves the ladder works).

### 3.4 Integration with web-research-custody skill
The `web-research-custody` skill defines a provenance discipline: every fetched
page must carry a provenance record (`manifest.csv` with sha256 hash + source URL).
The Exa reader adopts this for chain-of-custody: each fetched page is hashed and
recorded before storage, so claims are auditable.

### 3.5 Implementation Steps

| Step | Description | Integration |
|---|---|---|
| P2-3.1 | Build Exa API client (search + content fetch) | `web_search` skill supports Exa backend |
| P2-3.2 | Implement fallback ladder (Wayback → archive.today → Jina) | Reuse `blocked-page-recovery` patterns |
| P2-3.3 | Implement content parser (HTML → clean Markdown) | Use existing extraction patterns |
| P2-3.4 | Implement provenance tracking (hash + manifest) | Reuse `web-research-custody` manifest format |
| P2-3.5 | Store as Jane note (corpus/ or Obsidian vault) | Reuses `note-taking/obsidian` vault path convention |
| P2-3.6 | CLI: `jane read "<url>"` or `jane search "<query>"` | New CLI subparser |
| P2-3.7 | Honest citation: preserve source URL + timestamp | Per custody discipline |

### 3.6 Credentials & Security
Per `osint/secret-hygiene` skill:
- `EXA_API_KEY` stored in `~/.hermes/.env` (never in repo)
- Key never logged or echoed
- API key passed via header (`Authorization: Bearer $EXA_API_KEY`)
- No proxy relays (per blocked-page-recovery §"Proxy relays: don't")

### 3.7 Dependencies
- **External:** Exa API key (`EXA_API_KEY`)
- **System:** `curl`, `python3` (std lib `urllib`, `json`, `hashlib`)
- **Skills:** blocked-page-recovery, web-research-custody, osint/secret-hygiene

### 3.8 Estimation
| Step | Effort | Notes |
|---|---|---|
| P2-3.1 | 0.5 unit | Exa API is well-documented |
| P2-3.2–P2-3.4 | 1.5 units | Recovery ladder + provenance |
| P2-3.5–P2-3.7 | 1.0 unit | CLI + storage |
| **Total** | **3.0 units** | Network-bound; API-dependent |

### 3.9 Risks
- R-P2-5: Exa is paid API — requires user credential → mitigation: document as prerequisite, suggest free alternatives
- R-P2-6: Fallback to browser (last ladder step) requires `browser_exec` tool → mitigation: only use for interactive recovery

---

## 4.0 Phase 2 Dependency Graph

```
Phase 2 Items
  ├── pgvector RAG ──► llama-cpp (embedding) ──► llama.cpp binary
  │                     └──► PostgreSQL + pgvector
  ├── JSON Export ──► hermes-features-reference (state.db schema)
  │                     └──► stdlib sqlite3/json
  └── Exa Reader ──► web-research-custody (provenance)
                     ├──► blocked-page-recovery (fallback ladder)
                     ├──► osint/secret-hygiene (credential handling)
                     ├──► note-taking/obsidian (vault path convention)
                     └──► Exa API (external, paid)
```

## 5.0 Phase 2 Resource Requirements

| Resource | Phase 2.1 (pgvector) | Phase 2.2 (JSON Export) | Phase 2.3 (Exa) |
|---|---|---|---|
| PostgreSQL | Required | Not needed | Not needed |
| pgvector ext | Required | Not needed | Not needed |
| llama.cpp | For embeddings | Not needed | Not needed |
| Exa API key | Not needed | Not needed | Required (paid) |
| Nous credits | Not needed | Not needed | Falls back to curl (offline-first) |
| sudo | No | No | No |

## 6.0 Phase 2 Sequencing

```
[Phase 1 done] ──FS──> P2-2 (JSON Export) ──FS──> P2-1 (pgvector RAG)
                                             └─FS──> P2-3 (Exa Reader)
```

**P2-2 (JSON Export)** is sequenced first — it has zero external dependencies (pure stdlib SQLite read)
and establishes the session export format that P2-1 will consume (exported sessions → embedded in pgvector).

**P2-1 (pgvector)** and **P2-3 (Exa Reader)** are independent of each other; both consume P2-2 output.

**Rationale:** P2-2 is the foundational data-access layer; P2-1 and P2-3 both build on exported session
data. This sequencing minimizes rework if the JSON schema needs adjustment.

---

## 7.0 Phase 2 Acceptance Criteria (for future execution)

- [A1] `jane vector index` populates pgvector from Hermes sessions
- [A2] `jane vector search "<query>"` returns correct top-K results (verified against known content)
- [A3] `jane export --format json --output` produces valid JSON matching schema
- [A4] `jane export --offset N --limit M` returns exactly M sessions (or fewer at end)
- [A5] `jane read "<url>"` fetches content via Exa, stores with provenance hash
- [A6] Exa reader falls back to Wayback/archive.today when Exa returns errors
- [A7] All Phase 2 modules pass smoke_test.sh and are installable via `src/cli.py`
