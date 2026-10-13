"""Tests for web_api/server.py, called in-process (no running server needed)."""

import pytest
from fastapi.testclient import TestClient

from web_api.server import app

client = TestClient(app)


def test_pages_serves_a_fixture_page():
    response = client.get("/pages", params={"source_file": "crm-field-limits.html"})
    assert response.status_code == 200
    assert "255" in response.json()["text"]


@pytest.mark.parametrize(
    "source_file",
    [
        "../../scripts/test_questions.json",
        "../server.py",
        "../../README.md",
        "/etc/hosts",
        "does-not-exist.html",
    ],
)
def test_pages_refuses_anything_but_a_fixture_page(source_file):
    response = client.get("/pages", params={"source_file": source_file})
    assert response.status_code == 404
    assert "expected_answer" not in response.text


def test_urls_dont_give_away_the_repo_path():
    hit = client.get("/search", params={"q": "field length"}).json()["results"][0]
    page = client.get("/pages", params={"source_file": hit["source_file"]}).json()
    for url in (hit["url"], page["url"]):
        assert not url.startswith("file://")
        assert url.endswith("/pages?source_file=crm-field-limits.html")
