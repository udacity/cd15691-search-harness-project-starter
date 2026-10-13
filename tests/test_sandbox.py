"""Tests that the search tools refuse paths outside sample_repo/."""

from pathlib import Path

import pytest

from tools.codebase_search import server as codebase_server
from tools.design_doc_search import server as design_doc_server
from tools.git_history_search import server as git_server
from tools.shared.sandbox import ensure_inside_sample_repo

REPO_ROOT = Path(__file__).resolve().parents[1]
SAMPLE_REPO = REPO_ROOT / "sample_repo"
ASK = {"sub_question": "Where is it?", "rationale": "Testing the sandbox."}


@pytest.mark.parametrize("path", [SAMPLE_REPO, SAMPLE_REPO / "csvcheck", SAMPLE_REPO / "docs" / "design"])
def test_paths_inside_sample_repo_are_allowed(path):
    ensure_inside_sample_repo(str(path))


def test_the_relative_default_is_allowed(monkeypatch):
    monkeypatch.chdir(REPO_ROOT)  # the MCP servers run from the repo root
    ensure_inside_sample_repo("sample_repo")


@pytest.mark.parametrize(
    "path",
    [
        ".",
        "..",
        "scripts",
        "sample_repo/..",
        "sample_repo/../scripts/test_questions.json",
        str(REPO_ROOT),
        "/",
    ],
)
def test_paths_outside_sample_repo_are_refused(path, monkeypatch):
    monkeypatch.chdir(REPO_ROOT)
    with pytest.raises(ValueError, match="outside sample_repo"):
        ensure_inside_sample_repo(path)


def test_a_missing_path_still_raises_file_not_found():
    with pytest.raises(FileNotFoundError):
        ensure_inside_sample_repo(str(SAMPLE_REPO / "does_not_exist"))


def test_every_search_tool_refuses_the_repo_root(monkeypatch):
    monkeypatch.chdir(REPO_ROOT)
    calls = [
        lambda: codebase_server.search_code(**ASK, pattern="expected_answer", path="."),
        lambda: codebase_server.query_code(**ASK, query="(function_definition) @def", path="."),
        lambda: git_server.search_commits(**ASK, query="test", path="."),
        lambda: git_server.blame_line(**ASK, file_path="README.md", line_number=1, path="."),
        lambda: design_doc_server.search_docs(**ASK, query="test", docs_dir="."),
    ]
    for call in calls:
        with pytest.raises(ValueError, match="outside sample_repo"):
            call()


def test_blame_line_refuses_a_file_path_that_climbs_out(monkeypatch):
    monkeypatch.chdir(REPO_ROOT)
    with pytest.raises(ValueError, match="outside sample_repo"):
        git_server.blame_line(
            **ASK, file_path="../scripts/test_questions.json", line_number=1, path="sample_repo"
        )
