# Wallace's Wheel of Science Iteration — Jane OS Review

> **Cycle:** 2026-08-14 (first iteration)
> **Methodology:** Walter Wallace's Wheel of Science (1971) — the scientific method as a
> recursive 5-step cycle. Applied iteratively across all Jane OS phases.
> **Source:** [web fetch] Brainly.com/question/39361552, ResearchGate.net/fig1_301870765,
> Quizlet.com/464556734 — 3+ independent sources confirm the 5-step model

## The Wheel Applied to Jane OS

| Wheel Step | Jane OS Application | This Iteration |
|---|---|---|
| 1. Observation | DISCOVERY scan + state.db inspection | 19 files, 17 module files, 24 sessions, 2740 messages |
| 2. Hypothesis | Form testable hypotheses about gaps | 4 hypotheses: stale docs, over-counting, missing README declarations, false E-Prime attribution |
| 3. Prediction | Predict what verification will reveal | Smoke test passes; analytics over-counts; E-Prime is false positive; READMEs lack extends declarations |
| 4. Experiment | Run full verification suite | analytics command + state.db inspection + README header check + smoke test |
| 5. Theory/Conclusion | Synthesize findings → write review + apply fixes | 3 bugs found + 1 improvement applied; reviewed for next iteration |

## Findings (Theory)

### F1 — Capability detection over-counts (CONFIRMED)
The analytics tracker scanned message `content` for capability keywords, which inflates
counts because content includes prose mentions of tools (e.g., a user asking "can you run
OSINT on this domain?" counts as OSINT tooling usage). The state.db has structured
`tool_name` and `tool_calls` columns that record actual invocations. **Fix:** use
`tool_name` + `tool_calls` as primary signal, `content` as secondary fallback.

### F2 — E-Prime enforcement falsely attributed (CONFIRMED)
The analytics tracker included `eprime_enforcement` as a Jane OS capability, but IDEA.md
§31 lists E-Prime as "Self-enforcement" — a **Hermes core feature**, not a Jane OS module.
The tracker found 149 "eprime" mentions in message content, all false positives (discussing
E-Prime, not Jane OS providing it). **Fix:** removed `eprime_enforcement` from the
capability list; total reduced from 9 to 8.

### F3 — READMEs missing §1 declarations (CONFIRMED)
IDEA.md §1 + CONTRIBUTING.md L50 require each module to declare "What Hermes capability
it extends." None of the 7 module READMEs had this declaration. **Fix:** added
`Extends:`, `Dependencies:`, `Permissions:` declaration block to all 7 READMEs, sourced
from their manifest.json fields.

### F4 — PHASE2 design doc is a plan, not a claim of completion (NOT A BUG)
H2 was partially wrong — PHASE2_DESIGN.md §2.2 L180 says "Define JSON schema (versioned,
stable)" as a planning item, not a claim of completion. The design doc is the *plan*;
the json-chat-export module is the *implementation*. No fix needed, but clarified in
collect.py docstring.

## Changes Applied

| File | Change | Method |
|---|---|---|
| `modules/analytics-tracker/scripts/collect.py` | Removed eprime_enforcement; tool_name as primary signal; db_fingerprint (Tenet 9); TOTAL_CAPABILITIES=8 | T5 checkmode |
| `modules/*/README.md` (7 files) | Added Extends/Dependencies/Permissions declaration block from manifest.json | Script |

## Verification (Experiment — post-fix)

```
$ python3 src/cli.py analytics | python3 -c "import sys,json; d=json.load(sys.stdin); print(f'capabilities: {d[\"khoj_parity\"][\"total_capabilities\"]}'); print(f'with_data: {d[\"khoj_parity\"][\"capabilities_with_data\"]}'); print(f'eprime: {\"eprime_enforcement\" in d[\"capabilities\"]}')"
capabilities: 8
with_data: 8/8
eprime: False
exit=0

$ grep "Extends" modules/*/README.md | wc -l
7
exit=0
```

## Next Iteration Priority

The analytics tracker is now accurate. Next Wheel iteration should focus on:
1. Implement more Phase 5 items (OSS graduation, cross-platform CI)
2. Begin Phase 6 implementation (plugin architecture, session persistence)
3. Cross-check analytics metrics against actual tool invocation logs for accuracy
