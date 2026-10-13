"""Tests for the codebase-search tool."""

from pathlib import Path

from tools.codebase_search import core, server

SAMPLE_REPO = Path(__file__).resolve().parents[1] / "sample_repo"


def test_core_search_code_finds_max_field_length():
    matches = core.search_code(
        pattern="MAX_FIELD_LENGTH",
        path=str(SAMPLE_REPO),
        glob="*.py",
        max_results=50,
    )
    hits = [m for m in matches if m["path"] == "csvcheck/validators.py"]
    assert any(m["line_number"] == 3 for m in hits)
    definition_hit = next(m for m in hits if m["line_number"] == 3)
    assert definition_hit["match_spans"][0]["text"] == "MAX_FIELD_LENGTH"


def test_core_query_code_finds_check_row_definition():
    matches = core.query_code(
        '(function_definition name: (identifier) @name (#eq? @name "check_row")) @def',
        path=str(SAMPLE_REPO),
    )
    def_hits = [m for m in matches if m["capture"] == "def"]
    assert len(def_hits) == 1
    hit = def_hits[0]
    assert hit["path"] == "csvcheck/validators.py"
    assert hit["line_number"] == 18
    assert hit["node_type"] == "function_definition"
    assert hit["text"].startswith("def check_row")


def test_core_query_code_finds_module_level_constants():
    matches = core.query_code(
        "(module (expression_statement (assignment left: (identifier) @name) @assignment))",
        path=str(SAMPLE_REPO),
    )
    names = {m["text"] for m in matches if m["capture"] == "name"}
    assert {"MAX_FIELD_LENGTH", "DEFAULT_ENCODING_FALLBACKS", "MAX_ROWS"} <= names


def test_core_query_code_raises_on_bad_path():
    try:
        core.query_code("(function_definition) @def", path="/does/not/exist")
        assert False, "expected FileNotFoundError"
    except FileNotFoundError:
        pass


def test_server_search_code_tool_wraps_core_correctly():
    result = server.search_code(
        sub_question="Where is MAX_FIELD_LENGTH defined?",
        rationale="A text search for the exact constant name will surface its definition and every reference.",
        pattern="MAX_FIELD_LENGTH",
        path=str(SAMPLE_REPO),
        glob="*.py",
        max_results=10,
    )
    assert result["match_count"] >= 1
    assert result["pattern"] == "MAX_FIELD_LENGTH"


def test_server_query_code_tool_wraps_core_correctly():
    result = server.query_code(
        sub_question="Where is check_row actually defined, not just referenced?",
        rationale="A structural query distinguishes the real definition site from any incidental mention.",
        query='(function_definition name: (identifier) @name (#eq? @name "check_row")) @def',
        path=str(SAMPLE_REPO),
        max_results=10,
    )
    def_hits = [m for m in result["matches"] if m["capture"] == "def"]
    assert len(def_hits) == 1
    assert def_hits[0]["line_number"] == 18


def test_server_query_code_tool_raises_on_bad_path():
    try:
        server.query_code(
            sub_question="Where is check_row defined?",
            rationale="Structural lookup for a known function name.",
            query='(function_definition name: (identifier) @name (#eq? @name "check_row")) @def',
            path="/does/not/exist",
        )
        assert False, "expected FileNotFoundError"
    except FileNotFoundError:
        pass
