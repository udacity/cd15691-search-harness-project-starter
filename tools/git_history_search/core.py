"""Core git-history search logic: pickaxe search (git log -S) for when a
string was introduced/removed, and git blame for which commit last touched
a specific line. Shells out to `git` directly."""

from __future__ import annotations

import subprocess
from pathlib import Path
from typing import Any

_FIELD_SEP = "\x1f"  # unit separator


def _run_git(args: list[str], cwd: Path) -> str:
    result = subprocess.run(
        ["git", *args],
        cwd=cwd,
        capture_output=True,
        text=True,
        check=True,
    )
    return result.stdout


# TODO 1.4: Implement search_commits using git's pickaxe search (`git log
# -S<query>`) to find commits whose diff introduced or removed an exact
# occurrence of `query`. Return each matching commit's hash, date, author,
# and subject line.
# Hint: https://git-scm.com/book/en/v2/Git-Tools-Searching
def search_commits(
    query: str,
    path: str = ".",
    max_results: int = 20,
) -> list[dict[str, Any]]:
    """Find commits whose diff introduced or removed an exact occurrence of
    `query` (git's pickaxe search, `-S`). This is how you find WHEN and in
    WHICH commit a specific string (a constant name, an error message) was
    added or removed.

    Example: query="MAX_FIELD_LENGTH" runs the equivalent of
    `git log -S"MAX_FIELD_LENGTH"`, finding the commit that introduced
    that name.
    """
    root = Path(path).resolve()
    if not root.exists():
        raise FileNotFoundError(f"path does not exist: {path}")

    # TODO: Use _run_git to run the git log command: pickaxe search for
    # `query` (-S<query>), with --format set so each commit prints as one
    # line of hash, date, author, and subject, joined by _FIELD_SEP
    # instead of a space or comma (a commit's author name or subject can
    # contain either, which would break a naive split() later).
    # Hint: build the --format string from git's pretty-format
    # placeholders (%H, %ad, %an, %s), each one separated by _FIELD_SEP:
    # https://git-scm.com/docs/git-log#Documentation/git-log.txt-formatformat-string

    # TODO: Parse each output line into a commit dict and collect them.
    commits: list[dict[str, Any]] = []
    commits.append({"commit": ..., "date": ..., "author": ..., "subject": ...})
    return commits


def get_commit_message(commit_hash: str, path: str = ".") -> str:
    """Full commit message (subject + body) for a given commit hash."""
    root = Path(path).resolve()
    if not root.exists():
        raise FileNotFoundError(f"path does not exist: {path}")
    return _run_git(["log", "-1", "--format=%B", commit_hash], cwd=root).strip()


# TODO 1.5: Implement blame_line using `git blame` to find which commit last
# modified a specific line of a file. Return that commit's hash and full
# message.
def blame_line(file_path: str, line_number: int, path: str = ".") -> dict[str, Any]:
    """Find which commit last modified a specific line (git blame), and
    return that commit's metadata plus its full message."""
    root = Path(path).resolve()
    target = root / file_path
    if not target.exists():
        raise FileNotFoundError(f"file does not exist: {file_path}")

    # TODO: Use _run_git to run git blame on just this one line
    # (-L start,end) with the porcelain format.
    # Hint: https://git-scm.com/docs/git-blame#_the_porcelain_format
    # Note: an invalid line_number (e.g. past the end of the file) makes
    # git blame fail with a nonzero exit code, which _run_git's
    # check=True turns into a subprocess.CalledProcessError. Catch that
    # here and raise a ValueError instead, so callers get a clear message
    # about what was wrong with line_number rather than a raw
    # subprocess error.
    # TODO: Split the porcelain output into lines for parsing below.
    # Hint: the output already comes with one piece of metadata per
    # line, separated by newlines.
    # TODO: The first line of porcelain output starts with the commit
    # hash; pull it out. Then scan the remaining lines for the
    # "author ", "author-time ", and "summary " metadata lines and take
    # the text after the first space on each.
    # TODO: The porcelain summary is just the commit's subject line;
    # fetch the full message (subject + body) with get_commit_message.

    # TODO: Return the commit's metadata and message, plus the file/line
    # it was found at.
    return {
        "commit": ...,
        "author": ...,
        "author_time": ...,
        "summary": ...,
        "message": ...,
        "file_path": ...,
        "line_number": ...,
    }
