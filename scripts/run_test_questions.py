"""Run the onboarding-agent against test scenarios and
check whether its actual behavior matches what each question expects:
which source-type categories it touched, whether it escalated, and what
it cost.
"""

from __future__ import annotations

import json
import sys
from typing import Any

from helpers import (
    ANSWER_GATE_TOOL,
    REPO_ROOT,
    TEST_QUESTIONS,
    print_metrics,
    print_result,
    run_and_export,
    save_results,
    scenario_passed,
    tool_calls_in_session,
    tool_source_type,
)
from tools.answer_gate.core import MIN_DISTINCT_SOURCES_FOR_CONFIDENT_ANSWER


# TODO 5.1: Implement check_scenario to run one test scenario and compare
# the agent's actual behavior against what test_questions.json
# expects for it:
# - which source-type categories it actually used (from its tool calls),
#   vs. the scenario's own `tool_calls` field
# - whether it called submit_answer, and with what confidence
# - whether that confidence maps to the expected `escalate` value
def check_scenario(scenario: dict[str, Any]) -> dict[str, Any]:
    session = run_and_export(scenario["question"])
    tool_calls = tool_calls_in_session(session)

    # TODO: Figure out which source-type categories were actually used.
    # Map each tool call's name through tool_source_type, and drop the
    # ones that come back None (submit_answer isn't a search tool).
    # Hint: Use tool_source_type in helpers.py
    expected_types = sorted(scenario["tool_calls"])

    # TODO: Find the submit_answer call(s), and specifically the one(s)
    # that actually succeeded. A rejected call (ValueError inside the
    # tool, see tools/answer_gate/server.py) doesn't reach status
    # "completed", only count calls that did.
    # TODO: Read the last accepted call's own `confidence` input (it's a
    # parameter the agent passed in, not something to parse out of a
    # separate output), then map that to a "yes"/"no" escalate value to
    # compare against the scenario's own `escalate` field ("low"
    # confidence means the agent escalated).

    # TODO: Compute wall-clock latency from the session's own
    # info.time.created/updated timestamps (milliseconds since epoch).

    return {
        "id": scenario["id"],
        "question": scenario["question"],
        "session_id": session["info"]["id"],
        "cost_usd": session["info"]["cost"],
        "tokens": session["info"]["tokens"],
        "latency_s": latency_s,
        "tool_call_count": len(tool_calls),
        "submit_answer_calls": len(submit_calls),
        "submit_answer_rejections": len(submit_calls) - len(accepted),
        "submitted_answer": confidence is not None,
        "expected_types": expected_types,
        "actual_types": actual_types,
        "types_cover_required": len(actual_types)
        >= MIN_DISTINCT_SOURCES_FOR_CONFIDENT_ANSWER,
        "over_fetched": sorted(set(actual_types) - set(expected_types)),
        "expected_escalate": scenario["escalate"],
        "actual_escalate": actual_escalate,
        "escalate_match": actual_escalate == scenario["escalate"],
        "session": session,
    }


# TODO 5.2: Implement compute_metrics to aggregate the per-scenario results
# into summary numbers: pass rate, submit_answer rate, evidence coverage
# rate, total cost/tokens/latency, and escalation precision/recall (see
# the docstring below for why precision/recall, not just a match rate).
def compute_metrics(results: list[dict[str, Any]]) -> dict[str, Any]:
    """Aggregate metrics across all scenarios in this run.

    Escalation is scored as a binary classifier ("escalate" is the
    positive class) rather than a single match rate, because the two
    mismatch directions aren't equally bad: escalating something that
    didn't need it is just over-cautious, but answering confidently on a
    question that should have been escalated is exactly the
    overconfident-fabrication failure mode this whole project exists to
    catch. Recall specifically catches that severe case.
    """
    # TODO: Implement basic counts: how many scenarios total, how many
    # passed (scenario_passed), called submit_answer, covered the
    # required evidence types, over-fetched beyond what was required,
    # and how many gate rejections happened before a call finally
    # succeeded.
    # Hint: Use scenario_passed in helpers.py

    # TODO: Sum cost, tokens, and latency across every scenario, and
    # compute the average latency per scenario.

    # TODO: Score escalation as a binary classifier, "escalate" is the
    # positive class. In one pass over results, count:
    #   tp: expected=yes, actual=yes  (correctly escalated)
    #   fp: expected=no,  actual=yes  (escalated unnecessarily)
    #   fn: expected=yes, actual=no   (should have escalated, didn't --
    #                                  the severe, overconfident case)
    #   tn: expected=no,  actual=no   (correctly resolved)
    # Then precision = tp/(tp+fp) (of the times it escalated, how often
    # that was warranted) and recall = tp/(tp+fn) (of the times it
    # should have escalated, how often it actually did; recall < 1 means
    # it missed a required escalation).

    return {
        "total_scenarios": total,
        "passed": passed,
        "submit_answer_rate": submitted / total if total else None,
        "required_evidence_coverage_rate": covered_required / total if total else None,
        "over_fetched_count": over_fetched,
        "gate_rejections_before_success": rejections,
        "total_cost_usd": total_cost,
        "total_tokens": total_tokens,
        "total_latency_s": total_latency,
        "avg_latency_s": avg_latency,
        "escalation": {
            "precision": precision,
            "recall": recall,
            "missed_escalations": fn,
        },
    }


def main() -> None:
    if not TEST_QUESTIONS.exists():
        raise SystemExit(f"{TEST_QUESTIONS} not found.")

    scenarios = json.loads(TEST_QUESTIONS.read_text())

    print("=" * 70)
    print(f"Running {len(scenarios)} test scenario(s) against onboarding-agent")
    print("=" * 70)

    results = []
    for scenario in scenarios:
        print(f"\nRunning {scenario['id']}...")
        results.append(check_scenario(scenario))

    print("\n" + "=" * 70)
    print("SUMMARY")
    print("=" * 70)
    for r in results:
        print_result(r)

    metrics = compute_metrics(results)
    print_metrics(metrics)

    out_path = save_results(results, metrics)
    print(
        f"\nFull results (including exported sessions) saved to {out_path.relative_to(REPO_ROOT)}"
    )

    sys.exit(0 if metrics["passed"] == metrics["total_scenarios"] else 1)


if __name__ == "__main__":
    main()
