"""Tests for the git-history-search tool."""

from pathlib import Path

from tools.git_history_search import core, server

SAMPLE_REPO = Path(__file__).resolve().parents[1] / "sample_repo"
EXPECTED_COMMIT_SUBJECT = "Add field length validation to catch import truncation early"


def test_core_search_commits_finds_the_introducing_commit():
    commits = core.search_commits("MAX_FIELD_LENGTH", path=str(SAMPLE_REPO))
    assert len(commits) == 1
    assert commits[0]["subject"] == EXPECTED_COMMIT_SUBJECT
    assert len(commits[0]["commit"]) == 40  # full SHA


def test_core_blame_line_finds_same_commit_and_full_message():
    result = core.blame_line("csvcheck/validators.py", 3, path=str(SAMPLE_REPO))
    assert result["summary"] == EXPECTED_COMMIT_SUBJECT
    assert "docs/design/field-length-limit.md" in result["message"]


def test_core_blame_line_raises_on_missing_file():
    try:
        core.blame_line("csvcheck/does_not_exist.py", 1, path=str(SAMPLE_REPO))
        assert False, "expected FileNotFoundError"
    except FileNotFoundError:
        pass


def test_server_search_commits_tool_wraps_core_correctly():
    result = server.search_commits(
        sub_question="When and why was MAX_FIELD_LENGTH introduced?",
        rationale="Pickaxe search for the exact constant name finds the introducing commit.",
        query="MAX_FIELD_LENGTH",
        path=str(SAMPLE_REPO),
    )
    assert result["commit_count"] == 1
    assert result["commits"][0]["subject"] == EXPECTED_COMMIT_SUBJECT


def test_server_blame_line_tool_wraps_core_correctly():
    result = server.blame_line(
        sub_question="Which commit last touched line 3 of validators.py?",
        rationale="Blame pinpoints the exact commit for a known line.",
        file_path="csvcheck/validators.py",
        line_number=3,
        path=str(SAMPLE_REPO),
    )
    assert result["summary"] == EXPECTED_COMMIT_SUBJECT
