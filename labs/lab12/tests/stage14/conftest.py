"""Shared fixtures for Stage 14 API tests.

Two layers are exercised, matching stage14_api_deployment_contract.md
Section 16 ("contract-based API tests" vs "Docker service integration
tests"):

- `client`: an in-process ASGI TestClient against the real app and the
  real Stage 13 bundle (no mocking) -- fast, used by most tests.
- `live_server`: a real `uvicorn` subprocess bound to a real TCP port,
  reached over real HTTP via `httpx`. This is the layer that is actually
  different between "local" and "Docker" runs (socket binding, process
  startup, real network I/O), run identically in both environments.
"""

from __future__ import annotations

import socket
import subprocess
import sys
import time
from pathlib import Path

import httpx
import pytest

PACKAGE_ROOT = Path(__file__).resolve().parents[2]  # labs/lab12
if str(PACKAGE_ROOT) not in sys.path:
    sys.path.insert(0, str(PACKAGE_ROOT))

from api.app import app  # noqa: E402


@pytest.fixture()
def client():
    from fastapi.testclient import TestClient

    with TestClient(app) as c:
        yield c


def _free_port() -> int:
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
        s.bind(("127.0.0.1", 0))
        return s.getsockname()[1]


@pytest.fixture(scope="session")
def live_server():
    """A real uvicorn process, started once per test session, reached over real HTTP."""
    port = _free_port()
    proc = subprocess.Popen(
        [sys.executable, "-m", "uvicorn", "api.app:app", "--app-dir", str(PACKAGE_ROOT), "--host", "127.0.0.1", "--port", str(port), "--log-level", "warning"],
        stdout=subprocess.PIPE, stderr=subprocess.STDOUT, text=True,
    )
    base_url = f"http://127.0.0.1:{port}"
    deadline = time.monotonic() + 30
    last_error = None
    try:
        while time.monotonic() < deadline:
            try:
                resp = httpx.get(f"{base_url}/ready", timeout=1.0)
                if resp.status_code in (200, 503):
                    break
            except httpx.TransportError as exc:
                last_error = exc
            if proc.poll() is not None:
                output = proc.stdout.read() if proc.stdout else ""
                raise RuntimeError(f"uvicorn subprocess exited early (code={proc.returncode}):\n{output}")
            time.sleep(0.2)
        else:
            raise RuntimeError(f"uvicorn did not become reachable within 30s (last_error={last_error})")
        yield base_url
    finally:
        proc.terminate()
        try:
            proc.wait(timeout=10)
        except subprocess.TimeoutExpired:
            proc.kill()


@pytest.fixture()
def valid_shipment():
    return {
        "Line_Item_Qty_Sum": 500.0, "Line_Item_Value_Sum": 20000.0,
        "Shipment_Mode": "Air", "INCO_Term": "EXW", "Country": "Nigeria", "Product_Group": "ARV",
    }
