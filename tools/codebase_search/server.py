"""MCP server exposing codebase search tools via FastMCP."""

from __future__ import annotations

from typing import Any

from fastmcp import FastMCP

from tools.codebase_search import core
from tools.shared.logging_setup import get_logger
from tools.shared.sandbox import ensure_inside_sample_repo

# TODO 1.3: Create the FastMCP server instance
# Give it a name and, ideally `instructions` describing what it's for
# https://gofastmcp.com/servers/server
# TODO: Set up logging using the shared helper in tools/shared/logging_setup.py


# TODO: Register the search_code as an MCP tool
# https://gofastmcp.com/servers/tools#the-tool-decorator
def search_code(
    sub_question: str,
    rationale: str,
    pattern: str,
    path: str = "starter_bundle/sample_repo",
    glob: str | None = None,
    max_results: int = 50,
) -> dict[str, Any]:
    # TODO: Write the docstring for the tool's description.
    # https://gofastmcp.com/servers/tools#docstring-descriptions

    # TODO: Add logging
    # Refuse anything outside starter_bundle/sample_repo/ (see tools/shared/sandbox.py).
    ensure_inside_sample_repo(path)
    # TODO: run search code
    # TODO: add logging
    # TODO: return the results


# TODO: Register the query_code as an MCP tool
def query_code(
    sub_question: str,
    rationale: str,
    query: str,
    path: str = "starter_bundle/sample_repo",
    max_results: int = 50,
) -> dict[str, Any]:
    # TODO: Write the docstring for the tool's description.
    # https://gofastmcp.com/servers/tools#docstring-descriptions

    # TODO: Add logging
    # Refuse anything outside starter_bundle/sample_repo/ (see tools/shared/sandbox.py).
    ensure_inside_sample_repo(path)
    # TODO: run the query
    # TODO: add logging
    # TODO: return the results


def main() -> None:
    mcp.run(transport="stdio")


if __name__ == "__main__":
    main()
