"""Keeps the search tools inside starter_bundle/sample_repo/, the codebase
under investigation. Without it, a path like "." would let the agent search
the rest of this project, including starter_bundle/test_questions.json and
its expected answers."""

from __future__ import annotations

from pathlib import Path

SAMPLE_REPO = Path(__file__).resolve().parents[2] / "starter_bundle" / "sample_repo"


def ensure_inside_sample_repo(path: str, must_exist: bool = True) -> None:
    """Raise ValueError if `path` resolves to anywhere outside
    starter_bundle/sample_repo/.
    Relative paths resolve against the server's working directory, as the
    tools already do. `..`, absolute paths and symlinks are caught because
    the comparison uses the fully resolved path."""
    resolved = Path(path).resolve()
    if must_exist and not resolved.exists():
        raise FileNotFoundError(f"path does not exist: {path}")
    if not resolved.is_relative_to(SAMPLE_REPO.resolve()):
        raise ValueError(
            f"{path!r} is outside starter_bundle/sample_repo/, the codebase "
            "under investigation. Search inside starter_bundle/sample_repo/ instead."
        )
