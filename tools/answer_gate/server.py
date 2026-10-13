"""MCP server exposing the confidence/escalation gate as a submit_answer
tool.
"""

from __future__ import annotations

from typing import Any, Literal

from fastmcp import FastMCP

from tools.answer_gate import core
from tools.shared.logging_setup import get_logger

# TODO 3.3: Create the FastMCP server instance
# Give it a name and, ideally `instructions` describing what it's for
# https://gofastmcp.com/servers/server
# TODO: Set up logging using the shared helper in tools/shared/logging_setup.py


# TODO: Register submit_answer as an MCP tool
# https://gofastmcp.com/servers/tools#the-tool-decorator
def submit_answer(
    question: str,
    answer: str,
    confidence: Literal["high", "low"],
    sources: list[dict[str, Any]],
    escalation_reason: str | None = None,
) -> dict[str, Any]:
    # TODO: Write the docstring for the tool's description.
    # https://gofastmcp.com/servers/tools#docstring-descriptions

    # TODO: Add logging
    # TODO: run the gate
    # TODO: add logging
    # TODO: return the result
    pass


def main() -> None:
    mcp.run(transport="stdio")


if __name__ == "__main__":
    main()
