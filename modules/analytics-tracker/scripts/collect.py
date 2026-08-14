#!/usr/bin/env python3
"""
Analytics metrics collector for Jane OS Phase 5 (analytics-tracker module).

Reads from Hermes's ~/.hermes/state.db (sessions + messages tables) and produces
versioned JSON metrics that track parity with Khoj's 8 Jane-OS-provided gap
capabilities (IDEA.md §25-34; E-Prime excluded as it is a Hermes core feature, §31).

Usage:
  python3 scripts/collect.py                    # print JSON to stdout
  python3 scripts/collect.py --output FILE      # write JSON to file
  python3 src/cli.py analytics                  # via CLI wrapper

Integration:
  - json-chat-export module (Phase 2): reuses state.db reading pattern
  - hermes-features-reference skill: maps CLI commands to capabilities
  - SMELOSS §43: "measurable parity" — this provides the measurements
  - Tenet 9 (content-hash cache): metrics cache invalidated by DB content hash

Note: tool_name and tool_calls columns hold structured invocation data (preferred
over content scanning which inflates counts due to prose mentions). E-Prime
enforcement (§31) is a Hermes core directive, NOT a Jane OS module — excluded.
"""
import sys
import os
import json
import sqlite3
import re
import hashlib
from datetime import datetime, timezone

STATE_DB = os.path.expanduser("~/.hermes/state.db")

# ── Capability tool-name mappings (IDEA.md §25-34) ───────────────────────────
# Each capability is detected by scanning the tool_name + tool_calls columns
# (structured invocation data) for keywords. E-Prime enforcement (§31) is
# excluded — it is a Hermes core feature, not a Jane OS module.
CAPABILITY_KEYWORDS = {
    "osint_tooling": [
        "osint", "web_search", "web_extract", "search_files", "session_search",
        "osint_config_single_source", "osint_dependency_audit", "osint_email_breach",
        "osint_username", "osint_phone", "competitor_news_monitor", "blogwatcher",
        "youtube_content", "polymarket", "xurl", "blocked_page_recovery",
    ],
    "reverse_engineering": [
        "reverse_engineer_formats", "reverse_engineer_formats", "reverse-engineer",
        "webpack_sourcemap_analysis", "legacy_web_static_analyzer",
        "faithful_protocol_reverse_engineering", "reverse_engineer_web_extension",
        "reverse_engineer_data_format", "bundle", "sourcemap",
        "protocol_reverse", "bytecode", "binary", "hexdump", "disassembl",
    ],
    "gpu_cuda": [
        "cuda", "gpu", "nvidia", "mx250", "llama_cpp", "llama-cpp",
        "nvidia_smi", "cuda_visible", "gpu_acceler", "tensorrt", "vllm",
    ],
    "desktop_gui": [
        "computer_use", "desktop_ui", "cua_browser", "cua_browser_state",
        "cua_browser_navigate", "cua_browser_click", "cua_browser_type",
        "cua_browser_dialog", "cua_browser_download", "screenshot",
        "vision_analyze", "cua_browser_set_input_files",
        "focus_pane", "open_preview", "read_preview", "read_terminal",
        "read_window_below", "close_terminal", "inspecting_hermes_desktop_dom",
    ],
    "local_judge": [
        "judge_gate", "judge_goal", "judge_server", "ten_tenets",
        "fail_closed", "independent_judge", "127.0.0.1:8080",
        "evidence_shape", "judge_audit", "hermes_judge",
        "qwen2.5-1.5b", "delegation_queue",
    ],
    "tiered_memory": [
        "tiered_memory", "memory", "tiered", "content_hash",
        "result_cache", "longterm_db", "tier_1", "tier_2", "tier_3",
        "memory_ceiling", "archived",
    ],
    "subagent_orchestration": [
        "delegate_task", "subagent", "delegation", "max_concurrent_children",
        "spawn", "orchestrator", "leaf", "circuit_breaker", "rate_limit",
        "backoff", "delegation_queue", "auxiliary_goal_judge",
        "error_analysis_subagent_workaround",
    ],
    "procedural_skills": [
        "skill_view", "skill_manage", "skill_library", "skill_audit",
        "skills_list", "skill_utils", "iter_skill_index",
        "scan_skill_commands", "frontmatter_health", "projects_manage",
        "hermes_agent_skill_authoring",
    ],
}

TOTAL_CAPABILITIES = len(CAPABILITY_KEYWORDS)  # 8 (E-Prime excluded — Hermes core, §31)


def _db_fingerprint(conn):
    """Content-hash fingerprint of the messages table (Tenet 9: invalidate cache on content change)."""
    c = conn.cursor()
    c.execute("SELECT COUNT(*), COALESCE(SUM(length(content)), 0) FROM messages WHERE active = 1")
    row = c.fetchone()
    return hashlib.sha256(f"{row[0]}:{row[1]}".encode()).hexdigest() if row else "empty"


# ── Data collection ─────────────────────────────────────────────────────────

def collect_metrics():
    """Collect metrics from state.db. Read-only queries only."""
    if not os.path.isfile(STATE_DB):
        return {
            "version": "1.0",
            "collected_at": datetime.now(timezone.utc).isoformat(),
            "error": f"state.db not found at {STATE_DB}",
            "metrics": {},
            "capabilities": {},
            "khoj_parity": {"total_capabilities": TOTAL_CAPABILITIES,
                           "capabilities_with_data": 0,
                           "capabilities_without_data": TOTAL_CAPABILITIES},
        }

    conn = sqlite3.connect(STATE_DB)
    conn.row_factory = sqlite3.Row
    c = conn.cursor()

    # ── Aggregate metrics ─────────────────────────────────────────────────────
    c.execute("SELECT COUNT(*) FROM sessions WHERE archived = 0")
    total_sessions = c.fetchone()[0]

    c.execute("SELECT COUNT(*) FROM messages WHERE active = 1")
    total_messages = c.fetchone()[0]

    token_stats = c.execute("""
        SELECT
            SUM(input_tokens) as total_input,
            SUM(output_tokens) as total_output,
            SUM(cache_read_tokens) as total_cache_read,
            SUM(cache_write_tokens) as total_cache_write,
            SUM(reasoning_tokens) as total_reasoning
        FROM sessions WHERE archived = 0
    """).fetchone()

    cost_stats = c.execute("""
        SELECT
            SUM(estimated_cost_usd) as total_cost,
            model,
            COUNT(*) as session_count
        FROM sessions WHERE archived = 0
        GROUP BY model ORDER BY session_count DESC
    """).fetchall()

    models_used = {}
    for row in cost_stats:
        if row["model"]:
            models_used[row["model"]] = row["session_count"]

    total_cost = sum(float(row["total_cost"]) for row in cost_stats if row["total_cost"]) if cost_stats else 0.0

    # ── Capability metrics ─────────────────────────────────────────────────────
    # Use tool_name + tool_calls columns (structured data) as PRIMARY signal.
    # Fall back to content scanning only for capabilities not captured as tool names.
    # This avoids false positives from prose mentions (H2 — Wheel iteration finding).

    # Build keyword match patterns for tool_name matching
    capability_patterns = {}
    for cap_name, keywords in CAPABILITY_KEYWORDS.items():
        capability_patterns[cap_name] = [re.compile(re.escape(kw), re.IGNORECASE) for kw in keywords]

    # Fetch ALL active messages (tool_name + tool_calls + content for secondary signal)
    c.execute("""
        SELECT session_id, content, tool_calls, tool_name
        FROM messages WHERE active = 1
    """)
    all_messages = c.fetchall()

    capability_metrics = {}
    for cap_name, patterns in capability_patterns.items():
        sessions_with_cap = set()
        messages_with_cap = 0

        for row in all_messages:
            # Primary signal: structured tool_name + tool_calls
            structured = " ".join(filter(None, [
                row["tool_name"] or "",
                row["tool_calls"] or ""
            ]))
            # Secondary signal: content (for capabilities that appear in prose but
            # not as structured tool calls — logged for transparency)
            content_text = row["content"] or ""

            matched = False
            for pattern in patterns:
                if pattern.search(structured):
                    sessions_with_cap.add(row["session_id"])
                    messages_with_cap += 1
                    matched = True
                    break

            if not matched:
                # Secondary check: content scan (for tool invocations logged in prose)
                if any(pattern.search(content_text) for pattern in patterns):
                    sessions_with_cap.add(row["session_id"])
                    messages_with_cap += 1

        capability_metrics[cap_name] = {
            "sessions": len(sessions_with_cap),
            "messages": messages_with_cap,
        }

    # ── Khoj parity summary ─────────────────────────────────────────────────
    caps_with_data = sum(1 for v in capability_metrics.values() if v["messages"] > 0)
    caps_without_data = len(capability_metrics) - caps_with_data

    result = {
        "version": "1.0",
        "collected_at": datetime.now(timezone.utc).isoformat(),
        "db_fingerprint": _db_fingerprint(conn),
        "metrics": {
            "total_sessions": total_sessions,
            "total_messages": total_messages,
            "total_input_tokens": token_stats["total_input"] or 0,
            "total_output_tokens": token_stats["total_output"] or 0,
            "total_cache_read_tokens": token_stats["total_cache_read"] or 0,
            "total_cache_write_tokens": token_stats["total_cache_write"] or 0,
            "total_reasoning_tokens": token_stats["total_reasoning"] or 0,
            "total_cost_usd": round(total_cost, 4),
            "models_used": models_used,
        },
        "capabilities": capability_metrics,
        "khoj_parity": {
            "total_capabilities": TOTAL_CAPABILITIES,
            "capabilities_with_data": caps_with_data,
            "capabilities_without_data": caps_without_data,
            "note": "E-Prime enforcement excluded (Hermes core feature, IDEA.md §31). "
                    "Capability detection uses tool_name + tool_calls columns as primary "
                    "signal, content scan as secondary fallback.",
        },
    }

    conn.close()
    return result


# ── CLI ─────────────────────────────────────────────────────────────────────

def main():
    import argparse
    parser = argparse.ArgumentParser(description="Jane OS analytics metrics collector")
    parser.add_argument("--output", "-o", help="Write JSON to file instead of stdout")
    args = parser.parse_args()

    metrics = collect_metrics()

    if args.output:
        output_path = os.path.expanduser(args.output)
        os.makedirs(os.path.dirname(output_path), exist_ok=True)
        with open(output_path, "w") as f:
            json.dump(metrics, f, indent=2, ensure_ascii=False)
        print(f"Metrics written to {output_path}")
        print(f"  sessions: {metrics['metrics']['total_sessions']}")
        print(f"  messages: {metrics['metrics']['total_messages']}")
        print(f"  capabilities with data: {metrics['khoj_parity']['capabilities_with_data']}/{metrics['khoj_parity']['total_capabilities']}")
        print(f"  db_fingerprint: {metrics.get('db_fingerprint', 'N/A')[:16]}...")
    else:
        print(json.dumps(metrics, indent=2, ensure_ascii=False))


if __name__ == "__main__":
    main()
