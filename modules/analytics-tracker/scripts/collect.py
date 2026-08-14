#!/usr/bin/env python3
"""
Analytics metrics collector for Jane OS Phase 5 (analytics-tracker module).

Reads from Hermes's ~/.hermes/state.db (sessions + messages tables) and produces
versioned JSON metrics that track parity with Khoj's 9 gap capabilities
(IDEA.md §25-34).

Usage:
  python3 scripts/collect.py                    # print JSON to stdout
  python3 scripts/collect.py --output FILE      # write JSON to file
  python3 src/cli.py analytics                  # via CLI wrapper

Integration:
  - json-chat-export module (Phase 2): reuses state.db reading pattern
  - hermes-features-reference skill: maps CLI commands to capabilities
  - SMELOSS §43: "measurable parity" — this provides the measurements
"""
import sys
import os
import json
import sqlite3
import re
from datetime import datetime, timezone
from pathlib import Path

STATE_DB = os.path.expanduser("~/.hermes/state.db")

# ── Capability keyword mappings (IDEA.md §25-34) ────────────────────────────
# Each capability is detected by scanning message content and tool calls for
# keywords that indicate usage of that capability.

CAPABILITY_KEYWORDS = {
    "osint_tooling": [
        "osint", "web_search", "web_extract", "search_files", "session_search",
        "osint_config_single_source", "osint_dependency_audit", "osint_email_breach",
        "osint_username", "osint_phone", "competitor", "blogwatcher", "youtube_content",
        "polymarket", "xurl", "arcbrowser", "blocked_page_recovery"
    ],
    "reverse_engineering": [
        "reverse_engineer", "reverse-engineer", "webpack", "legacy-web-static",
        "faithful_protocol", "binary", "hexdump", "disassembl", "IDA", "ghidra",
        "bytecode", "bundle", "sourcemap", "protocol_reverse"
    ],
    "gpu_cuda": [
        "cuda", "gpu", "nvidia", "mx250", "ollama", "llama.cpp", "llama-cpp",
        "vllm", "nvidia-smi", "cuda_visible", "gpu_acceler", "tensorrt"
    ],
    "desktop_gui": [
        "computer_use", "desktop_ui", "cua_driver", "cua-browser", "screenshot",
        "click", "vision_analyze", "ax_tree", "accessibility", "desktop_app",
        "focus_pane", "open_preview", "read_preview", "read_terminal",
        "read_window_below", "close_terminal"
    ],
    "local_judge": [
        "judge_gate", "judge_goal", "judge_server", "ten-tenets", "fail_closed",
        "fail-closed", "independent_judge", "127.0.0.1:8080", "local_model",
        "evidence_shape", "judge_audit", "hermes-judge", "qwen2.5-1.5b"
    ],
    "tiered_memory": [
        "tiered_memory", "MEMORY.md", "longterm.db", "session_summary",
        "tiered", "memory_ceiling", "content_hash", "result_cache", "archived",
        "tier_1", "tier_2", "tier_3", "memory_char_limit"
    ],
    "eprime_enforcement": [
        "eprime", "e-prime", "E-Prime", "self-enforce", "self-enforcement",
        "eprime_compliance", "eprime-bulk", "e_prime", "prime_compliance"
    ],
    "subagent_orchestration": [
        "delegate_task", "subagent", "delegation", "max_concurrent_children",
        "spawn", "orchestrator", "leaf", "circuit_breaker", "rate_limit",
        "429", "backoff", "delegation_queue", "auxiliary_goal_judge"
    ],
    "procedural_skills": [
        "skill_view", "skill_manage", "SKILL.md", "skill_library", "skill_audit",
        "/skill", "skill:", "skills_list", "skill_utils", "iter_skill_index",
        "scan_skill_commands", "frontmatter_health", "project-manage"
    ],
}


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
            "khoj_parity": {"total_capabilities": 9, "capabilities_with_data": 0, "capabilities_without_data": 9},
        }

    conn = sqlite3.connect(STATE_DB)
    conn.row_factory = sqlite3.Row
    c = conn.cursor()

    # ── Aggregate metrics (sessions + messages tables) ──────────────────────
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

    # ── Capability metrics (scan message content + tool calls) ───────────────
    # We scan the most recent 200 messages for capability keywords
    c.execute("""
        SELECT session_id, role, content, tool_calls, tool_name
        FROM messages WHERE active = 1
        ORDER BY timestamp DESC LIMIT 200
    """)

    capability_metrics = {}
    for cap_name, keywords in CAPABILITY_KEYWORDS.items():
        keyword_patterns = [re.compile(re.escape(kw), re.IGNORECASE) for kw in keywords]

        c2 = conn.cursor()
        c2.execute("""
            SELECT session_id, content, tool_calls, tool_name
            FROM messages WHERE active = 1
        """)
        sessions_with_cap = set()
        messages_with_cap = 0

        for row in c2.fetchall():
            text = " ".join(filter(None, [
                row["content"] or "",
                row["tool_calls"] or "",
                row["tool_name"] or ""
            ]))
            for pattern in keyword_patterns:
                if pattern.search(text):
                    sessions_with_cap.add(row["session_id"])
                    messages_with_cap += 1
                    break  # count each message once

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
            "total_capabilities": 9,
            "capabilities_with_data": caps_with_data,
            "capabilities_without_data": caps_without_data,
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
    else:
        print(json.dumps(metrics, indent=2, ensure_ascii=False))


if __name__ == "__main__":
    main()
