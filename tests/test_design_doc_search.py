"""Tests for the design-doc-search (semantic/RAG) tool."""

from pathlib import Path

from tools.design_doc_search import core, server

DOCS_DIR = (
    Path(__file__).resolve().parents[1]
    / "starter_bundle"
    / "sample_repo"
    / "docs"
    / "design"
)


def test_core_search_docs_surfaces_field_length_doc():
    hits = core.search_docs(
        "why is the field length limit set the way it is",
        docs_dir=str(DOCS_DIR),
        max_results=3,
    )
    assert len(hits) == 3
    file_names = {h["file_name"] for h in hits}
    assert "field-length-limit.md" in file_names
    # Chroma L2 distance: 0 is identical, smaller is more similar.
    assert hits[0]["distance"] <= hits[-1]["distance"]


def test_core_search_docs_finds_nothing_relevant_for_unrelated_query():
    # No design doc discusses encoding-fallback rationale
    # The top hit's distance should still be notably worse than a query covered in the
    # docs.
    on_topic = core.search_docs(
        "field length limit", docs_dir=str(DOCS_DIR), max_results=1
    )
    off_topic = core.search_docs(
        "why is the encoding fallback list cp1252 then latin-1",
        docs_dir=str(DOCS_DIR),
        max_results=1,
    )
    assert off_topic[0]["distance"] > on_topic[0]["distance"]


def test_server_search_docs_tool_wraps_core_correctly():
    result = server.search_docs(
        sub_question="Is there a documented rationale for the 240-character field limit?",
        rationale="Design docs are the most likely place to find a stated rationale for a code decision.",
        query="why is the field length limit 240",
        docs_dir=str(DOCS_DIR),
        max_results=3,
    )
    assert result["hit_count"] == 3
    assert any(h["file_name"] == "field-length-limit.md" for h in result["hits"])
