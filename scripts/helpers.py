"""Given helper functions for scripts/run_test_questions.py: how to
actually run the agent via opencode and capture its session data, and
how to print/save results.
"""

from __future__ import annotations

import json
import subprocess
import sys
from datetime import UTC, datetime
from pathlib import Path
from typing import Any

REPO_ROOT = Path(__file__).resolve().parent.parent
# `python3 scripts/run_test_questions.py` puts only scripts/ on the import
# path. This lets it import the repo's own `tools` package too.
sys.path.insert(0, str(REPO_ROOT))
TEST_QUESTIONS = REPO_ROOT / "starter_bundle" / "test_questions.json"
RESULTS_DIR = REPO_ROOT / ".logs" / "test_runs"

# Maps each MCP server name (as it appears in a tool call's "<server>.<tool>"
# name, normalized below to "<server>_<tool>") to the source-type
# vocabulary used in starter_bundle/test_questions.json and
# tools/answer_gate/core.py's SOURCE_TYPES.
SERVER_TO_SOURCE_TYPE = {
    "codebase-search": "codebase",
    "git-history-search": "git_history",
    "design-doc-search": "design_doc",
    "web-search": "web",
}
ANSWER_GATE_TOOL = "answer-gate_submit_answer"
MCP_SERVERS = (*SERVER_TO_SOURCE_TYPE, ANSWER_GATE_TOOL.split("_", 1)[0])


def run_and_export(question: str) -> dict[str, Any]:
    """Run the agent against one question and return its full exported
    session data."""
    run_result = subprocess.run(
        [
            "opencode",
            "run",
            # A private server started from this environment. OpenCode's
            # background service keeps the environment it started with, so
            # the MCP servers it starts may not see this shell's python3 or
            # OPENAI_API_KEY.
            "--standalone",
            "--format",
            "json",
            "--agent",
            "onboarding-agent",
            question,
        ],
        cwd=REPO_ROOT,
        capture_output=True,
        text=True,
        timeout=300,
        check=False,
    )
    first_line = run_result.stdout.splitlines()[0] if run_result.stdout else ""
    try:
        session_id = json.loads(first_line)["sessionID"]
    except (IndexError, json.JSONDecodeError, KeyError) as e:
        raise RuntimeError(
            f"Could not find a session ID in opencode run's output for: "
            f"{question!r}\n--- stdout ---\n{run_result.stdout}\n"
            f"--- stderr ---\n{run_result.stderr}"
        ) from e

    RESULTS_DIR.mkdir(parents=True, exist_ok=True)
    export_path = RESULTS_DIR / f"export_{session_id}.json"
    with export_path.open("w") as export_file:
        export_result = subprocess.run(
            ["opencode", "session", "export", session_id],
            cwd=REPO_ROOT,
            stdout=export_file,
            stderr=subprocess.PIPE,
            text=True,
            timeout=60,
            check=False,
        )
    if export_result.returncode != 0:
        raise RuntimeError(
            f"opencode session export {session_id} failed:\n{export_result.stderr}"
        )
    try:
        session = json.loads(export_path.read_text())
    except json.JSONDecodeError as e:
        raise RuntimeError(
            f"opencode session export {session_id} did not return valid "
            f"JSON ({e}). Raw output saved to {export_path} for inspection."
        ) from e
    export_path.unlink()
    return session


def tool_source_type(tool_name: str) -> str | None:
    """Map a tool's full "<server>_<tool>" name to the source-type
    vocabulary, or None if it's not one of the four search servers (e.g.
    it's answer-gate, or a built-in)."""
    for server, source_type in SERVER_TO_SOURCE_TYPE.items():
        if tool_name.startswith(f"{server}_"):
            return source_type
    return None


def tool_calls_in_session(session: dict[str, Any]) -> list[dict[str, Any]]:
    """Every MCP tool call across every assistant message in this
    session, in order.

    """
    calls = []
    for message in session["messages"]:
        if message.get("type") != "assistant":
            continue
        for item in message.get("content", []):
            if item.get("type") != "tool":
                continue
            if item.get("name") != "execute":
                # With "codemode": false, MCP tools are called directly,
                # named "<server>_<tool>".
                if item.get("name", "").split("_", 1)[0] in MCP_SERVERS:
                    state = item.get("state", {})
                    calls.append(
                        {
                            "tool": item["name"],
                            "status": state.get("status"),
                            "input": state.get("input", {}),
                        }
                    )
                continue
            nested = item.get("state", {}).get("metadata", {}).get("toolCalls", [])
            for tc in nested:
                tool_name = tc.get("tool", "")
                if "." not in tool_name:
                    continue  # OpenCode's own meta-tools, e.g. "search"
                calls.append(
                    {
                        "tool": tool_name.replace(".", "_", 1),
                        "status": tc.get("status"),
                        "input": tc.get("input", {}),
                    }
                )
    return calls


def scenario_passed(r: dict[str, Any]) -> bool:
    return r["submitted_answer"] and r["types_cover_required"] and r["escalate_match"]


def print_result(r: dict[str, Any]) -> bool:
    passed = scenario_passed(r)
    status = "PASS" if passed else "FAIL"
    print(f"\n[{status}] {r['id']}: {r['question']}")
    print(
        f"  session: {r['session_id']}  cost: ${r['cost_usd']:.4f}  "
        f"latency: {r['latency_s']:.1f}s  tool calls: {r['tool_call_count']}"
    )
    print(f"  called submit_answer: {r['submitted_answer']}", end="")
    if r["submit_answer_rejections"]:
        print(
            f"  ({r['submit_answer_rejections']} rejected attempt(s) before succeeding)"
        )
    else:
        print()
    print(
        f"  tool_calls  scenario hints={r['expected_types']}  actual={r['actual_types']}"
        f"  {'ok' if r['types_cover_required'] else 'INSUFFICIENT INDEPENDENT EVIDENCE'}"
    )
    if r["over_fetched"]:
        print(
            f"  note: also used {r['over_fetched']}, beyond what this question requires"
        )
    print(
        f"  escalate    expected={r['expected_escalate']}  actual={r['actual_escalate']}"
        f"  {'ok' if r['escalate_match'] else 'MISMATCH'}"
    )
    return passed


def print_metrics(metrics: dict[str, Any]) -> None:
    print("\n" + "=" * 70)
    print("METRICS")
    print("=" * 70)
    print(f"pass rate: {metrics['passed']}/{metrics['total_scenarios']}")
    print(f"submit_answer called: {metrics['submit_answer_rate']:.0%}")
    print(
        f"required evidence covered: {metrics['required_evidence_coverage_rate']:.0%}"
    )
    print(f"over-fetched (used more than required): {metrics['over_fetched_count']}")
    print(
        f"gate rejections before success: {metrics['gate_rejections_before_success']}"
    )
    print(
        f"total cost: ${metrics['total_cost_usd']:.4f}  total tokens: {metrics['total_tokens']}"
    )
    esc = metrics["escalation"]
    precision = "n/a" if esc["precision"] is None else f"{esc['precision']:.0%}"
    recall = "n/a" if esc["recall"] is None else f"{esc['recall']:.0%}"
    print(f"escalation precision: {precision}  recall: {recall}")
    if esc["missed_escalations"] > 0:
        print(
            f"  ^ severe: {esc['missed_escalations']} question(s) answered with "
            "confidence when the evidence didn't actually support it."
        )


def save_results(results: list[dict[str, Any]], metrics: dict[str, Any]) -> Path:
    RESULTS_DIR.mkdir(parents=True, exist_ok=True)
    timestamp = datetime.now(UTC).strftime("%Y-%m-%dT%H-%M-%SZ")
    out_path = RESULTS_DIR / f"run_{timestamp}.json"
    out_path.write_text(
        json.dumps(
            {"timestamp": timestamp, "metrics": metrics, "results": results}, indent=2
        )
    )
    return out_path
