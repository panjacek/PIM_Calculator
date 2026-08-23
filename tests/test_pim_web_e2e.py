"""Playwright e2e tests: spawn streamlit headless, drive the default flow.

Requires the web group plus a chromium install:
    uv sync --group dev --group web
    uv run playwright install chromium
Go/mojo engine paths are guarded by skipif so the default suite stays green
where the binary/toolchain is absent.
"""

from __future__ import annotations

import socket
import subprocess
import sys
import time
import urllib.request
from pathlib import Path
from typing import Any

import pytest
from playwright.sync_api import Page, expect

import pim_web

ROOT = Path(__file__).resolve().parent.parent


def _free_port() -> int:
    with socket.socket() as sock:
        sock.bind(("127.0.0.1", 0))
        return int(sock.getsockname()[1])


@pytest.fixture(scope="session")
def streamlit_url() -> Any:
    port = _free_port()
    cmd = [
        sys.executable,
        "-m",
        "streamlit",
        "run",
        str(ROOT / "web" / "app.py"),
        "--server.headless=true",
        f"--server.port={port}",
        "--browser.gatherUsageStats=false",
    ]
    proc = subprocess.Popen(
        cmd, cwd=ROOT, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL
    )
    url = f"http://127.0.0.1:{port}"
    deadline = time.time() + 60
    ready = False
    while time.time() < deadline and proc.poll() is None:
        try:
            with urllib.request.urlopen(f"{url}/_stcore/health", timeout=2) as resp:
                if resp.status == 200:
                    ready = True
                    break
        except OSError:
            time.sleep(0.5)
    if not ready:
        proc.terminate()
        pytest.fail("streamlit did not become healthy in time")
    yield url
    try:
        proc.terminate()
        proc.wait(timeout=10)
    except subprocess.TimeoutExpired:
        proc.kill()
        proc.wait()


def _assert_no_exception(page: Page) -> None:
    expect(page.locator('[data-testid="stException"]')).to_have_count(0)


def test_default_python_flow(streamlit_url: str, page: Page) -> None:
    page.goto(streamlit_url)
    expect(page.get_by_text("PIM Calculator")).to_be_visible()

    # Two editors (TX/RX) rendered with defaults.
    editors = page.locator('[data-testid="stDataFrame"]')
    expect(editors).to_have_count(2)

    # Engine radio present, python selectable.
    expect(page.get_by_text("python", exact=True)).to_be_visible()

    # Calculate produces tables and an altair SVG chart.
    page.get_by_role("button", name="Calculate").click()
    expect(page.locator("svg").first).to_be_visible(timeout=15000)
    _assert_no_exception(page)


@pytest.mark.skipif(
    not pim_web.engine_available("go"), reason="go/pim_calc binary not built"
)
def test_go_engine_flow(streamlit_url: str, page: Page) -> None:
    page.goto(streamlit_url)
    page.get_by_text("go", exact=True).click()
    page.get_by_role("button", name="Calculate").click()
    expect(page.get_by_text("engine: go")).to_be_visible(timeout=20000)
    _assert_no_exception(page)


@pytest.mark.parametrize("engine", ["mojo", "mojo_py"])
@pytest.mark.skipif(
    not pim_web.engine_available("mojo"), reason="mojo toolchain unavailable"
)
def test_mojo_engine_flow(engine: str, streamlit_url: str, page: Page) -> None:
    page.goto(streamlit_url)
    page.get_by_text(engine, exact=True).click()
    page.get_by_role("button", name="Calculate").click()
    expect(page.get_by_text(f"engine: {engine}")).to_be_visible(timeout=30000)
    _assert_no_exception(page)


def test_unavailable_engine_shows_hint(streamlit_url: str, page: Page) -> None:
    page.goto(streamlit_url)
    for engine in ("go", "mojo", "mojo_py"):
        if not pim_web.engine_available(engine):
            hint = pim_web.ENGINE_HINTS[engine]
            label = f"{engine} ({hint})"
            expect(page.get_by_text(label, exact=True)).to_be_visible()
            page.get_by_text(label, exact=True).click()
            page.get_by_role("button", name="Calculate").click()
            expect(page.get_by_text(f"{engine} unavailable")).to_be_visible()
