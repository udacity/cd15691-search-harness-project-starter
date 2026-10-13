"""MCP server exposing git-history search tools via FastMCP."""

from __future__ import annotations

from pathlib import Path
from typing import Any

from fastmcp import FastMCP

from tools.git_history_search import core
from tools.shared.logging_setup import get_logger
from tools.shared.sandbox import ensure_inside_sample_repo

# TODO 1.6: Create the FastMCP server instance
# Give it a name and, ideally `instructions` describing what it's for
# https://gofastmcp.com/servers/server
# TODO: Set up logging using the shared helper in tools/shared/logging_setup.py


# TODO: Register search_commits as an MCP tool
# https://gofastmcp.com/servers/tools#the-tool-decorator
def search_commits(
    sub_question: str,
    rationale: str,
    query: str,
    path: str = "sample_repo",
    max_results: int = 20,
) -> dict[str, Any]:
    # TODO: Write the docstring for the tool's description.
    # https://gofastmcp.com/servers/tools#docstring-descriptions

    # TODO: Add logging
    # Refuse anything outside sample_repo/ (see tools/shared/sandbox.py).
    ensure_inside_sample_repo(path)
    # TODO: run the search
    # TODO: add logging
    # TODO: return the results


# TODO: Register blame_line as an MCP tool
# https://gofastmcp.com/servers/tools#the-tool-decorator
def blame_line(
    sub_question: str,
    rationale: str,
    file_path: str,
    line_number: int,
    path: str = "sample_repo",
) -> dict[str, Any]:
    # TODO: Write the docstring for the tool's description.
    # https://gofastmcp.com/servers/tools#docstring-descriptions

    # TODO: Add logging
    # Refuse anything outside sample_repo/ (see tools/shared/sandbox.py).
    ensure_inside_sample_repo(path)
    ensure_inside_sample_repo(str(Path(path) / file_path), must_exist=False)
    # TODO: run the blame lookup
    # TODO: add logging
    # TODO: return the result


def main() -> None:
    mcp.run(transport="stdio")


if __name__ == "__main__":
    main()
