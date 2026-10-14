"""Core web search logic: an HTTP client for the local web-search API
(web_api/server.py), a local, fully deterministic stand-in for a real
search provider (Exa, Tavily, Brave, etc.).
Needs web_api/server.py running first:
    python3 -m web_api.server
"""

from __future__ import annotations

from typing import Any

import httpx

DEFAULT_BASE_URL = "http://127.0.0.1:8000"


# TODO 1.10: Implement search_web to call the local web-search API's /search
# endpoint and return its ranked results.
def search_web(
    query: str, max_results: int = 5, base_url: str = DEFAULT_BASE_URL
) -> list[dict[str, Any]]:
    """Keyword-search the local web-search API for `query`, returning
    its ranked results (title, snippet, score, source_file per hit)."""
    # TODO: Call httpx.get() against f"{base_url}/search", passing `q`
    # and `max_results` as query parameters.
    # Wrap the call in a try/except for httpx.ConnectError, raising a
    # clear RuntimeError telling the caller the API isn't reachable and
    # how to start it.
    # Hint: https://www.python-httpx.org/quickstart/#passing-parameters-in-urls
    # TODO: Raise for a non-2xx response (a bad request, a server error)
    # rather than silently returning whatever came back.
    # Hint: https://www.python-httpx.org/quickstart/#exceptions
    # TODO: Parse the JSON response and return its `results` list.


# TODO 1.11: Implement fetch_page to call the local web-search API's /pages
# endpoint and return the full page it gives back.
def fetch_page(source_file: str, base_url: str = DEFAULT_BASE_URL) -> dict[str, Any]:
    """Read one page from the local web-search API in full, returning
    its title and complete extracted text rather than a snippet."""
    # TODO: Call httpx.get() against f"{base_url}/pages", passing
    # `source_file` as a query parameter, with the same
    # ConnectError-to-RuntimeError handling as search_web above.
    # TODO: Raise for a non-2xx response (e.g. 404 if source_file
    # doesn't exist)
    # TODO: Parse and return the JSON response.
