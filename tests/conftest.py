"""Shared pytest fixtures for the onboarding-agent tool tests."""

import socket
import subprocess
import sys
import time
from pathlib import Path

import pytest

REPO_ROOT = Path(__file__).resolve().parents[1]
SAMPLE_REPO = REPO_ROOT / "sample_repo"
WEB_API_HOST = "127.0.0.1"
WEB_API_PORT = 8000
WEB_API_BASE_URL = f"http://{WEB_API_HOST}:{WEB_API_PORT}"


@pytest.fixture(scope="session", autouse=True)
def ensure_sample_repo() -> Path:
    """Clone scripts/sample_repo.bundle if the checkout isn't
    already present.
    """
    if not (SAMPLE_REPO / "csvcheck" / "validators.py").exists():
        subprocess.run(
            [
                "bash",
                str(REPO_ROOT / "scripts" / "clone_sample_repo.sh"),
            ],
            check=True,
        )
    return SAMPLE_REPO


@pytest.fixture(scope="session")
def web_api_server() -> str:
    """Start web_api/server.py as a subprocess for the test session, and
    tear it down afterward.
    """
    process = subprocess.Popen(
        [sys.executable, "-m", "web_api.server"],
        cwd=REPO_ROOT,
        stdout=subprocess.DEVNULL,
        stderr=subprocess.DEVNULL,
    )
    deadline = time.monotonic() + 10
    while time.monotonic() < deadline:
        try:
            with socket.create_connection((WEB_API_HOST, WEB_API_PORT), timeout=0.5):
                break
        except OSError:
            time.sleep(0.2)
    else:
        process.terminate()
        raise RuntimeError("web_api server did not start within 10 seconds")

    yield WEB_API_BASE_URL

    process.terminate()
    process.wait(timeout=5)
