"""Core logic for the search-quality / confidence gate."""

from __future__ import annotations

from typing import Any, Literal

SOURCE_TYPES = {"codebase", "git_history", "design_doc", "web"}

MIN_DISTINCT_SOURCES_FOR_CONFIDENT_ANSWER = 2


# TODO 3.1: Implement evaluate_gate to check whether `sources` clears the
# confidence bar: validate every source's type against SOURCE_TYPES, then
# count how many DISTINCT types are present (not the raw number of
# citations) and compare that against MIN_DISTINCT_SOURCES_FOR_CONFIDENT_ANSWER.
def evaluate_gate(sources: list[dict[str, Any]]) -> dict[str, Any]:
    """Check whether `sources` clears the confidence bar.

    Each entry in `sources` is a citation the agent is relying on, shaped
    like {"type": "git_history", "detail": "commit a72c040: Add field
    length validation..."}, `type` must be one of SOURCE_TYPES.

    Distinct *types* are what count, not raw citation count: three
    search_code hits are still only one source of evidence (the codebase
    itself), and don't corroborate each other the way a commit message
    and a design doc do.
    """
    # TODO: Reject any source whose type isn't in SOURCE_TYPES.

    # TODO: Count distinct source TYPES, not raw citations -- a set
    # comprehension dedupes this for you (see the docstring above).
    # TODO: Build the gate result: whether it passes, which types were
    # seen, how many distinct types, and the total citation count.


# TODO 3.2: Implement submit_answer to validate a final answer against the
# confidence gate before accepting it. Raise ValueError (not a silent
# fallback) for every way the call can be internally inconsistent or
# under-supported
def submit_answer(
    question: str,
    answer: str,
    confidence: Literal["high", "low"],
    sources: list[dict[str, Any]],
    escalation_reason: str | None = None,
) -> dict[str, Any]:
    """Validate and package a final answer against the confidence gate.

    Raises ValueError, rather than silently accepting the call, when:
      - confidence="high" isn't actually backed by
        MIN_DISTINCT_SOURCES_FOR_CONFIDENT_ANSWER distinct source types, or
      - confidence="low" has no escalation_reason explaining what's
        missing, or
      - confidence="high" is paired with an escalation_reason (a
        contradiction).
    """
    # TODO: Reject anything other than "high" or "low".

    # TODO: Reject confidence="high" paired with an escalation_reason

    # TODO: Reject confidence="low" with no escalation_reason. An
    # escalation needs to say what's actually missing.

    # TODO: Run the actual confidence gate over `sources`.

    # TODO: Reject confidence="high" if the gate didn't actually pass

    # TODO: Package the validated answer, its confidence, whether it was
    # escalated, and the gate result together for the caller.
