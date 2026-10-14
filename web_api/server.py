"""A local HTTP API standing in for a real web search
provider (Exa, Tavily, Brave, etc.). Keyword-searches the fabricated
external HTML fixture pages under external_sources and
serves them over plain HTTP.

    python3 -m web_api.server

Then it's reachable at http://127.0.0.1:8000 (see DEFAULT_BASE_URL in
tools/web_search/core.py for the default the tool itself expects).
"""

from __future__ import annotations

import re
from html.parser import HTMLParser
from pathlib import Path
from typing import Any

import uvicorn
from fastapi import FastAPI, HTTPException, Query, Request

SOURCES_DIR = Path(__file__).resolve().parent / "external_sources"

_SNIPPET_RADIUS = 80

app = FastAPI(
    title="Local Web Search API",
    description=(
        "A local stand-in for a real web search API, serving fixed, "
        "fabricated content so results stay reproducible."
    ),
)


class _TextExtractor(HTMLParser):
    """Strips HTML tags, capturing plain text and the <title> separately."""

    def __init__(self) -> None:
        super().__init__()
        self.title = ""
        self._in_title = False
        self._chunks: list[str] = []

    def handle_starttag(self, tag: str, attrs) -> None:
        if tag == "title":
            self._in_title = True

    def handle_endtag(self, tag: str) -> None:
        if tag == "title":
            self._in_title = False

    def handle_data(self, data: str) -> None:
        if self._in_title:
            self.title += data
        else:
            self._chunks.append(data)

    @property
    def text(self) -> str:
        return " ".join(" ".join(self._chunks).split())


def _extract(html: str) -> tuple[str, str]:
    """Returns (title, plain_text)."""
    parser = _TextExtractor()
    parser.feed(html)
    return parser.title.strip(), parser.text


def _snippet(text: str, query_terms: list[str]) -> str:
    lower = text.lower()
    for term in query_terms:
        idx = lower.find(term)
        if idx != -1:
            start = max(0, idx - _SNIPPET_RADIUS)
            end = min(len(text), idx + len(term) + _SNIPPET_RADIUS)
            prefix = "..." if start > 0 else ""
            suffix = "..." if end < len(text) else ""
            return f"{prefix}{text[start:end].strip()}{suffix}"
    return text[: _SNIPPET_RADIUS * 2].strip()


def _page_url(request: Request, source_file: str) -> str:
    """This API's own address for a page, rather than its file:// path,
    which would give away where the repo lives on disk."""
    return str(request.url_for("get_page").include_query_params(source_file=source_file))


@app.get("/search")
def search(
    request: Request, q: str, max_results: int = Query(default=5, ge=1)
) -> dict[str, Any]:
    """Keyword-search the fixture pages, ranked by how many query terms
    appear in each page's text. Mirrors what a real search API's results
    endpoint returns: a ranked list with a title, url, and snippet per
    hit, not full page content (see /pages for that)."""
    query_terms = [t for t in re.findall(r"\w+", q.lower()) if t]
    if not query_terms:
        raise HTTPException(status_code=400, detail="query has no searchable terms")

    results: list[dict[str, Any]] = []
    for html_file in sorted(SOURCES_DIR.rglob("*.html")):
        html_content = html_file.read_text(encoding="utf-8")
        title, text = _extract(html_content)
        lower_text = text.lower()
        score = sum(lower_text.count(term) for term in query_terms)
        if score == 0:
            continue
        source_file = str(html_file.relative_to(SOURCES_DIR))
        results.append(
            {
                "url": _page_url(request, source_file),
                "title": title or html_file.name,
                "snippet": _snippet(text, query_terms),
                "score": score,
                "source_file": source_file,
            }
        )

    results.sort(key=lambda r: r["score"], reverse=True)
    return {"query": q, "results": results[:max_results]}


@app.get("/pages")
def get_page(request: Request, source_file: str) -> dict[str, Any]:
    """Read one fixture page in full: its title and complete extracted
    text, not just a snippet. `source_file` is the value a /search
    result's own `source_file` field gave you."""
    target = (SOURCES_DIR / source_file).resolve()
    # Only the fixture pages: "../../starter_bundle/test_questions.json" must not
    # reach the rest of the repo. Outside paths get the same 404 as a
    # missing page, so this doesn't reveal what exists elsewhere.
    inside = target.is_relative_to(SOURCES_DIR.resolve())
    if not inside or target.suffix != ".html" or not target.is_file():
        raise HTTPException(
            status_code=404, detail=f"source file does not exist: {source_file}"
        )

    html_content = target.read_text(encoding="utf-8")
    title, text = _extract(html_content)

    return {
        "source_file": source_file,
        "url": _page_url(request, source_file),
        "title": title or target.name,
        "text": text,
    }


def main() -> None:
    uvicorn.run(app, host="127.0.0.1", port=8000)


if __name__ == "__main__":
    main()
