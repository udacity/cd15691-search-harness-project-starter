"""Tests for the answer_gate (confidence/escalation gate) tool."""

import pytest
from tools.answer_gate import core, server

QUESTION = "Why is this configured the way it is?"

SOURCE_A = {"type": "codebase", "detail": "source A"}
SOURCE_B = {"type": "git_history", "detail": "source B"}
SOURCE_C = {"type": "design_doc", "detail": "source C"}


def test_evaluate_gate_passes_with_two_distinct_source_types():
    gate = core.evaluate_gate([SOURCE_A, SOURCE_B])
    assert gate["passes_gate"] is True
    assert gate["distinct_source_count"] == 2
    assert gate["distinct_source_types"] == ["codebase", "git_history"]


def test_evaluate_gate_fails_with_only_one_distinct_source_type_even_with_multiple_citations():
    # Three citations, but all "codebase" -- they don't corroborate each
    # other the way two different source types would.
    gate = core.evaluate_gate(
        [
            SOURCE_A,
            {"type": "codebase", "detail": "another codebase citation"},
            {"type": "codebase", "detail": "yet another codebase citation"},
        ]
    )
    assert gate["passes_gate"] is False
    assert gate["distinct_source_count"] == 1


def test_evaluate_gate_rejects_unknown_source_type():
    with pytest.raises(ValueError):
        core.evaluate_gate([{"type": "not_a_real_type", "detail": "x"}])


def test_submit_answer_accepts_high_confidence_with_enough_sources():
    result = core.submit_answer(
        question=QUESTION,
        answer="It's configured this way because of A and B.",
        confidence="high",
        sources=[SOURCE_A, SOURCE_B, SOURCE_C],
    )
    assert result["confidence"] == "high"
    assert result["escalated"] is False
    assert result["gate"]["passes_gate"] is True


def test_submit_answer_rejects_high_confidence_with_thin_evidence():
    with pytest.raises(ValueError, match="distinct source"):
        core.submit_answer(
            question=QUESTION,
            answer="Probably because of B.",
            confidence="high",
            sources=[SOURCE_B],
        )


def test_submit_answer_accepts_low_confidence_with_escalation_reason():
    result = core.submit_answer(
        question=QUESTION,
        answer="There's a setting, but no source explains why it has this value.",
        confidence="low",
        sources=[SOURCE_B],
        escalation_reason="Source B mentions the setting was added, but not why "
        "this specific value was chosen; no other source addresses it either.",
    )
    assert result["escalated"] is True
    assert result["confidence"] == "low"


def test_submit_answer_rejects_low_confidence_without_escalation_reason():
    with pytest.raises(ValueError, match="escalation_reason"):
        core.submit_answer(
            question=QUESTION,
            answer="Not sure.",
            confidence="low",
            sources=[SOURCE_B],
        )


def test_submit_answer_rejects_high_confidence_paired_with_escalation_reason():
    with pytest.raises(ValueError, match="contradiction"):
        core.submit_answer(
            question=QUESTION,
            answer="It's configured this way because of A and B.",
            confidence="high",
            sources=[SOURCE_A, SOURCE_B],
            escalation_reason="This shouldn't be set alongside confidence='high'.",
        )


def test_server_submit_answer_tool_wraps_core_correctly():
    result = server.submit_answer(
        question=QUESTION,
        answer="It's configured this way because of A, B, and C.",
        confidence="high",
        sources=[SOURCE_A, SOURCE_B, SOURCE_C],
    )
    assert result["confidence"] == "high"
    assert result["gate"]["distinct_source_count"] == 3
