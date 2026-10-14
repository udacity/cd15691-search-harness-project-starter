"""MCP server exposing web search via FastMCP."""

from __future__ import annotations

from typing import Any

from fastmcp import FastMCP

from tools.shared.logging_setup import get_logger
from tools.web_search import core

# TODO 1.12: Create the FastMCP server instance
# Give it a name and, ideally `instructions` describing what it's for
# https://gofastmcp.com/servers/server
# TODO: Set up logging using the shared helper in tools/shared/logging_setup.py


# TODO: Register search_web as an MCP tool
# https://gofastmcp.com/servers/tools#the-tool-decorator
def search_web(
    sub_question: str,
    rationale: str,
    query: str,
    max_results: int = 5,
    base_url: str = core.DEFAULT_BASE_URL,
) -> dict[str, Any]:
    # TODO: Write the docstring for the tool's description.
    # https://gofastmcp.com/servers/tools#docstring-descriptions

    # TODO: Add logging
    # TODO: run the search
    # TODO: add logging
    # TODO: return the results
    pass


# TODO: Register fetch_page as an MCP tool
# https://gofastmcp.com/servers/tools#the-tool-decorator
def fetch_page(
    sub_question: str,
    rationale: str,
    source_file: str,
    base_url: str = core.DEFAULT_BASE_URL,
) -> dict[str, Any]:
    # TODO: Write the docstring for the tool's description.
    # https://gofastmcp.com/servers/tools#docstring-descriptions

    # TODO: Add logging
    # TODO: fetch the page
    # TODO: add logging
    # TODO: return the result
    pass


def main() -> None:
    mcp.run(transport="stdio")


if __name__ == "__main__":
    main()
