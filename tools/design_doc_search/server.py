"""MCP server exposing semantic/RAG search over internal design docs via
FastMCP."""

from __future__ import annotations

from typing import Any

from fastmcp import FastMCP

from tools.design_doc_search import core
from tools.shared.logging_setup import get_logger
from tools.shared.sandbox import ensure_inside_sample_repo

# TODO 1.9: Create the FastMCP server instance
# Give it a name and, ideally `instructions` describing what it's for
# https://gofastmcp.com/servers/server
# TODO: Set up logging using the shared helper in tools/shared/logging_setup.py


# TODO: Register search_docs as an MCP tool
# https://gofastmcp.com/servers/tools#the-tool-decorator
def search_docs(
    sub_question: str,
    rationale: str,
    query: str,
    docs_dir: str = "sample_repo/docs/design",
    max_results: int = 5,
) -> dict[str, Any]:
    # TODO: Write the docstring for the tool's description.
    # https://gofastmcp.com/servers/tools#docstring-descriptions

    # TODO: Add logging
    # Refuse anything outside sample_repo/ (see tools/shared/sandbox.py).
    ensure_inside_sample_repo(docs_dir)
    # TODO: run the search
    # TODO: add logging
    # TODO: return the results


def main() -> None:
    mcp.run(transport="stdio")


if __name__ == "__main__":
    main()
