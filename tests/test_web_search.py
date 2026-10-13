"""Tests for the web-search tool. Needs the web_api_server fixture
(conftest.py) since tools/web_search is now an HTTP client for
web_api/server.py, not a direct file reader."""

import httpx
import pytest

from tools.web_search import core, server


def test_core_search_web_finds_crm_field_limits(web_api_server):
    results = core.search_web(
        "field length limit 255 characters", base_url=web_api_server
    )
    assert len(results) == 1
    hit = results[0]
    assert hit["source_file"] == "crm-field-limits.html"
    assert "Field Limits" in hit["title"]
    assert hit["score"] > 0


def test_core_search_web_no_results_for_unrelated_query(web_api_server):
    results = core.search_web("banana smoothie recipe", base_url=web_api_server)
    assert results == []


def test_core_search_web_raises_when_server_unreachable():
    with pytest.raises(RuntimeError, match="Could not reach"):
        core.search_web("anything", base_url="http://127.0.0.1:9999")


def test_server_search_web_tool_wraps_core_correctly(web_api_server):
    result = server.search_web(
        sub_question="Does the CRM's published documentation confirm the 255-character field limit?",
        rationale="The design doc cites the CRM's public docs as the source of the 255-character limit; check that externally.",
        query="field length limit 255 characters",
        base_url=web_api_server,
    )
    assert result["result_count"] == 1
    assert result["results"][0]["source_file"] == "crm-field-limits.html"


def test_core_fetch_page_returns_full_text_not_a_snippet(web_api_server):
    search_hit = core.search_web(
        "field length limit 255 characters", base_url=web_api_server
    )[0]
    page = core.fetch_page(search_hit["source_file"], base_url=web_api_server)
    assert page["source_file"] == "crm-field-limits.html"
    assert "Field Limits" in page["title"]
    # The full text should be longer than the snippet search_web returned.
    assert len(page["text"]) > len(search_hit["snippet"])


def test_core_fetch_page_raises_on_missing_source_file(web_api_server):
    with pytest.raises(httpx.HTTPStatusError):
        core.fetch_page("does-not-exist.html", base_url=web_api_server)


def test_server_fetch_page_tool_wraps_core_correctly(web_api_server):
    result = server.fetch_page(
        sub_question="What does the CRM's field-limits page say in full?",
        rationale="search_web's snippet didn't include enough context; read the whole page.",
        source_file="crm-field-limits.html",
        base_url=web_api_server,
    )
    assert result["source_file"] == "crm-field-limits.html"
    assert len(result["text"]) > 0
