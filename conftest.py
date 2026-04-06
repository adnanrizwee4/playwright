"""
conftest.py — Estate Management Test Suite

FIX: Use system Google Chrome (/opt/google/chrome/chrome) instead of
     Playwright's bundled Chromium which gets SIGKILL'd by the kernel
     on this machine (seccomp filter incompatibility).

Google Chrome works confirmed:
  google-chrome --headless --no-sandbox --dump-dom http://192.168.0.129:32865/
  → returns HTML ✅
"""

import os
import json
import threading
import pytest
from playwright.sync_api import Page, Browser, sync_playwright
from typing import Dict, Any, Generator

from config import UI, SUPER_ADMIN, TIMEOUT, SCHEMA_NAME
from utils.api_client import APIClient


# ── Use system Google Chrome — confirmed working on this machine ──────────────
CHROME_EXE = "/opt/google/chrome/chrome"

LAUNCH_ARGS = [
    "--no-sandbox",
    "--disable-dev-shm-usage",
    "--disable-gpu",
]


# ── Tell pytest-playwright to use Google Chrome for ALL page/browser fixtures ─
@pytest.fixture(scope="session")
def browser_type_launch_args(pytestconfig) -> Dict[str, Any]:
    return {
        "executable_path": CHROME_EXE,
        "args": LAUNCH_ARGS,
    }


# ── 1. API client — pure HTTP, no browser ─────────────────────────────────────
@pytest.fixture(scope="session")
def api() -> APIClient:
    client = APIClient.login(SUPER_ADMIN["email"], SUPER_ADMIN["password"])
    print(f"\n🔑 API token obtained")
    return client


# ── 1b. Schema-scoped API client (adds x-estate-schema header) ────────────────
@pytest.fixture(scope="session")
def schema_api(api: APIClient) -> APIClient:
    """
    Returns an APIClient with x-estate-schema set to the first active estate's
    schema_name.  All tenant-scoped endpoints (resident-types, residences,
    contacts, visitor-schedules, etc.) require this header.
    """
    estates = api.list_estates()
    assert estates, "No estates found — create at least one estate first"
    schema_name = estates[0]["schema_name"]
    assert schema_name, f"Estate has no schema_name: {estates[0]}"

    # Clone the session so the base `api` fixture stays without a schema header
    client = APIClient(token=api.token, schema_name=schema_name)
    print(f"\n🏢 Schema API ready — x-estate-schema: {schema_name}")
    return client


# ── 2. Auth state — own isolated browser, never touches test browser ──────────
AUTH_FILE = "fixtures/.auth_state.json"

@pytest.fixture(scope="session")
def auth_state(api: APIClient) -> str:
    """
    Runs sync_playwright() in a dedicated thread so it gets its own event loop
    and doesn't conflict with pytest-playwright's asyncio loop.
    """
    os.makedirs("fixtures", exist_ok=True)

    state_holder: Dict[str, Any] = {}
    error_holder:  Dict[str, Any] = {}

    def _login():
        try:
            with sync_playwright() as pw:
                browser = pw.chromium.launch(
                    executable_path=CHROME_EXE,
                    headless=True,
                    args=LAUNCH_ARGS,
                )
                ctx  = browser.new_context()
                page = ctx.new_page()
                page.set_default_timeout(TIMEOUT["navigation"])

                print(f"\n🌐 Logging in via Google Chrome (thread)...")
                page.goto(UI["login"])
                page.wait_for_load_state("networkidle")

                page.locator(
                    "input[formcontrolname='email'], input[type='email'], input[name='email']"
                ).first.fill(SUPER_ADMIN["email"])

                page.locator(
                    "input[formcontrolname='password'], input[type='password']"
                ).first.fill(SUPER_ADMIN["password"])

                page.locator(
                    "button[type='submit'], button:has-text('Login'), button:has-text('Sign In')"
                ).first.click()

                page.wait_for_url(
                    lambda url: "/login" not in url,
                    timeout=TIMEOUT["navigation"],
                )
                page.wait_for_load_state("networkidle")

                state_holder["state"] = ctx.storage_state()
                browser.close()
        except Exception as exc:
            error_holder["exc"] = exc

    t = threading.Thread(target=_login, daemon=True)
    t.start()
    t.join(timeout=90)

    if "exc" in error_holder:
        raise error_holder["exc"]

    with open(AUTH_FILE, "w") as f:
        json.dump(state_holder["state"], f)

    print(f"✅ Auth state saved → {AUTH_FILE}")
    return AUTH_FILE


# ── 3. Authenticated page ─────────────────────────────────────────────────────
@pytest.fixture
def auth_page(browser: Browser, auth_state: str) -> Generator[Page, None, None]:
    ctx  = browser.new_context(storage_state=auth_state)
    page = ctx.new_page()
    page.set_default_timeout(TIMEOUT["default"])
    yield page
    ctx.close()


# ── 4. Auto-screenshot on failure ─────────────────────────────────────────────
@pytest.fixture(autouse=True)
def screenshot_on_failure(request):
    yield
    if hasattr(request.node, "rep_call") and request.node.rep_call.failed:
        page = (
            request.node.funcargs.get("auth_page")
            or request.node.funcargs.get("page")
        )
        if page:
            os.makedirs("screenshots", exist_ok=True)
            safe = request.node.name.replace("/", "_").replace(" ", "_")
            path = f"screenshots/FAILED_{safe}.png"
            try:
                page.screenshot(path=path, full_page=True)
                print(f"\n📸 Screenshot → {path}")
            except Exception:
                pass


@pytest.hookimpl(tryfirst=True, hookwrapper=True)
def pytest_runtest_makereport(item, call):
    outcome = yield
    rep = outcome.get_result()
    setattr(item, "rep_" + rep.when, rep)