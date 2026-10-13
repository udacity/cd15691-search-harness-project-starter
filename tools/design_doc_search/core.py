"""Core semantic/RAG search logic over internal design docs: chunk markdown
files by H2 section, embed with OpenAI's embeddings API (via Chroma's
OpenAIEmbeddingFunction), index in Chroma, and search via cosine similarity.
"""

from __future__ import annotations

import os
from functools import cache, lru_cache
from pathlib import Path
from typing import Any

import chromadb
from chromadb.api.models.Collection import Collection
from chromadb.utils.embedding_functions.openai_embedding_function import (
    OpenAIEmbeddingFunction,
)

_EMBEDDING_MODEL_NAME = "text-embedding-3-small"


@lru_cache(maxsize=1)
def _get_embedding_function() -> OpenAIEmbeddingFunction:
    api_key = os.environ.get("OPENAI_API_KEY")
    if not api_key:
        raise RuntimeError(
            "OPENAI_API_KEY is not set. design_doc_search needs it to call "
            "OpenAI's embeddings API."
        )
    api_base = os.environ.get("OPENAI_BASE_URL")
    return OpenAIEmbeddingFunction(
        api_key=api_key, model_name=_EMBEDDING_MODEL_NAME, api_base=api_base
    )


@lru_cache(maxsize=1)
def _get_chroma_client() -> chromadb.ClientAPI:
    return chromadb.Client()


def _chunk_markdown(text: str, file_name: str) -> list[dict[str, str]]:
    """Split a markdown doc into chunks by H2 (##) section, each chunk
    prefixed with the doc's H1 title for context so a chunk read in
    isolation still says what document it came from."""
    lines = text.splitlines()
    title = ""
    for line in lines:
        if line.startswith("# "):
            title = line[2:].strip()
            break

    chunks: list[dict[str, str]] = []
    current_heading = ""
    current_lines: list[str] = []

    def flush() -> None:
        body = "\n".join(current_lines).strip()
        if body:
            prefix = title if not current_heading else f"{title} — {current_heading}"
            chunks.append(
                {"heading": current_heading or title, "text": f"{prefix}\n{body}"}
            )

    for line in lines:
        if line.startswith("## "):
            flush()
            current_heading = line[3:].strip()
            current_lines = []
        else:
            current_lines.append(line)
    flush()

    if not chunks:
        chunks = [{"heading": title, "text": text.strip()}]

    for i, chunk in enumerate(chunks):
        chunk["chunk_id"] = f"{file_name}::{i}"
        chunk["file_name"] = file_name
    return chunks


# NOTE: @cache is here for speed. Chunking, embedding, and indexing a
# whole docs directory is expensive, so we only want to do that work once per
# docs_dir rather than on every single search_docs call.
#
# Tradeoff: @cache keys purely on the `resolved_docs_dir` argument, not on
# the actual contents of that directory. If a .md file is added or edited
# after this has already been called once for a given path, the cache
# will keep returning the old, now-stale collection.
# Not an issue for this project, but worth knowing.
@cache
def _build_collection(resolved_docs_dir: str) -> Collection:
    """Chunk, embed, and index every .md file under a resolved docs
    directory."""
    root = Path(resolved_docs_dir)
    all_chunks: list[dict[str, str]] = []
    for md_file in sorted(root.rglob("*.md")):
        text = md_file.read_text(encoding="utf-8")
        rel_name = str(md_file.relative_to(root))
        all_chunks.extend(_chunk_markdown(text, rel_name))

    if not all_chunks:
        raise RuntimeError(f"no .md files found under {resolved_docs_dir}")

    # TODO 1.7: Get or create a Chroma collection for this docs_dir, with the
    # OpenAI embedding function attached.
    # https://docs.trychroma.com/docs/embeddings/openai
    # TODO: Add the chunks (ids, documents, metadatas) to the collection
    # https://docs.trychroma.com/docs/collections/add-data
    return collection


def _get_collection(docs_dir: str) -> Collection:
    root = Path(docs_dir).resolve()
    if not root.exists():
        raise FileNotFoundError(f"docs directory does not exist: {docs_dir}")
    return _build_collection(str(root))


# TODO 1.8: Implement search_docs as a RAG pipeline over the markdown design
# docs under `docs_dir`: chunk each file, embed the
# chunks with OpenAI embeddings, index them in Chroma, embed the query
# the same way, and return the top `max_results` most similar chunks with
# their source file, heading, text, and similarity distance.
def search_docs(
    query: str, docs_dir: str, max_results: int = 5
) -> list[dict[str, Any]]:
    """Semantically search the design docs under `docs_dir` for `query`,
    building (and caching) the index on first use."""
    # TODO: Get (or build) the cached collection for this docs_dir

    # TODO: Run the similarity query against the collection
    # https://docs.trychroma.com/docs/querying-collections/query-and-get

    # TODO: Build one hit dict per result: chunk_id, file_name, heading,
    # text, and distance
    return hits
