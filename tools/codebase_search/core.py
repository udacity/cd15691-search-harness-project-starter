"""Core codebase search logic: ripgrep-based text/pattern search and a
general tree-sitter structural query over Python files."""

from __future__ import annotations

import os
from pathlib import Path
from typing import Any

import tree_sitter_python as tspython
from ripgrep_rs import search_structured
from tree_sitter import Language, Parser, Query, QueryCursor

# --------------------------------------------------------------------------
# search_code
# --------------------------------------------------------------------------


# TODO 1.1: Implement search_code using ripgrep to search for a literal
# string or regex `pattern` across the codebase under `path`. Return
# each match's file path (relative to `path`), line number, the full
# line text, and the matched span(s) within that line.
# Hint: Use `max_results` to cap how many matches are returned, and
# optionally `glob` to restrict which files are searched.
def search_code(
    pattern: str,
    path: str = ".",
    glob: str | None = None,
    max_results: int = 50,
) -> list[dict[str, Any]]:
    """Run a ripgrep text/regex search and return matches relative to `path`."""
    root = Path(path).resolve()
    if not root.exists():
        raise FileNotFoundError(f"search path does not exist: {path}")

    # TODO: Run the ripgrep search via search_structured
    raw_matches = ...

    results: list[dict[str, Any]] = []
    for m in raw_matches:
        # TODO: For each search match, build one result entry: its path
        # made relative to `root`, line number, full line text, and its
        # submatches (each with matched text + start/end byte offsets)
        results.append(
            {
                "path": ...,
                "line_number": ...,
                "line_text": ...,
                "match_spans": [
                    {"text": ..., "start": ..., "end": ...}
                    for s in m.submatches
                ],
            }
        )
    return results


# --------------------------------------------------------------------------
# query_code
# --------------------------------------------------------------------------


def _iter_python_files(root: Path):
    skip_dir_names = {
        ".git",
        "__pycache__",
        ".venv",
        "venv",
        "node_modules",
        ".pytest_cache",
    }
    for file_path in root.rglob("*.py"):
        rel_dir_parts = file_path.relative_to(root).parts[:-1]
        if any(
            part in skip_dir_names or part.startswith(".") for part in rel_dir_parts
        ):
            continue
        yield file_path


# TODO 1.2: Implement query_code using tree-sitter's Query API to run an
# arbitrary structural search across every Python file under `path`
def query_code(
    query: str, path: str = ".", max_results: int = 50
) -> list[dict[str, Any]]:
    """Run a tree-sitter structural query against every Python file under
    `path`.

    `query` is a tree-sitter S-expression pattern with @capture-name
    annotations. Examples:

        Any function definition, capturing its name:
            (function_definition name: (identifier) @name) @def

        A function definition with a specific name:
            (function_definition
              name: (identifier) @name (#eq? @name "check_row")) @def

        A module-level constant assignment:
            (module (expression_statement (assignment
              left: (identifier) @const_name) @assignment))

        An import statement:
            (import_from_statement) @import
    """
    root = Path(path).resolve()
    if not root.exists():
        raise FileNotFoundError(f"search path does not exist: {path}")

    # TODO: Build the Python Language object from the tree_sitter_python
    # grammar package -- needed to construct both the Query and the
    # Parser
    # https://github.com/tree-sitter/py-tree-sitter/tree/master#basic-parsing
    # TODO: Create a tree-sitter query using Query
    # https://github.com/tree-sitter/py-tree-sitter/tree/master#pattern-matching
    # TODO: Create a query cursor to capture the query matches
    # https://github.com/tree-sitter/py-tree-sitter/tree/master#captures
    # TODO: Create a tree-sitter parser
    # https://github.com/tree-sitter/py-tree-sitter/tree/master#basic-parsing

    results: list[dict[str, Any]] = []

    # TODO: Glob all .py files under `root` and iterate through them
    for file_path in _iter_python_files(root):
        try:
            # TODO: Read this file's source and parse it into a syntax tree
            # https://github.com/tree-sitter/py-tree-sitter/tree/master#basic-parsing
            pass
        except Exception:
            # TODO: Handle a corrupt file, permission error, encoding
            # issue, etc. -- skip the file, don't fail the whole call.
            pass

        # TODO: Execute the query by running the cursor against the file's tree
        # https://github.com/tree-sitter/py-tree-sitter/tree/master#captures
        # TODO: Return the results up to max_results -- for each
        # captured node, pull out its text and position
        # (start_byte/end_byte, start_point, end_point, type) to
        # build one result entry
        results.append(
            {
                "path": ...,
                "capture": ...,
                "node_type": ...,
                "line_number": ...,
                "end_line_number": ...,
                "text": ...,
            }
        )

    return results
