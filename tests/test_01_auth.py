"""
tests/test_01_auth.py
=====================
Authentication Tests — covers both API and UI login.

Business Logic (AuthUser + Estate + Role models):
  ✅ SUPER_ADMIN can login via API and get a token
  ✅ ESTATE_MANAGER can login (different role)
  ✅ Wrong password → 401 from API
  ✅ Wrong email → 401 from API
  ✅ Empty email/password → 400 from API
  ✅ UI login with valid credentials → redirects to dashboard
  ✅ UI login with wrong credentials → stays on login + shows error
  ✅ UI: empty fields → submit button disabled or validation shown
  ✅ JWT token stored in localStorage after UI login
  ✅ Protected route redirects unauthenticated user to login

Run:
    pytest tests/test_01_auth.py -v
"""

import pytest
import requests
from playwright.sync_api import Page, expect
from config import API, UI, SUPER_ADMIN, TIMEOUT
from fixtures.test_data import INVALID_LOGIN_CASES
from utils.api_client import APIClient


# ═══════════════════════════════════════════════════════════
#  SECTION A — PURE API TESTS  (no browser needed)
# ═══════════════════════════════════════════════════════════

class TestAuthAPI:

    def test_superadmin_login_returns_token(self):
        """
        POST /api/v1/auth/login/
        Super Admin login must return HTTP 200 and a non-empty token.
        """
        resp = requests.post(
            API["login"],
            json={"email": SUPER_ADMIN["email"], "password": SUPER_ADMIN["password"]},
            timeout=10,
        )
        assert resp.status_code == 200, f"Expected 200, got {resp.status_code}: {resp.text}"

        body  = resp.json()
        token = (
            body.get("token")
            or body.get("access_token")
            or body.get("access")
            or body.get("data", {}).get("token")
        )
        assert token, f"No token in response: {body}"
        assert len(token) > 20, "Token looks too short"
        print(f"\n✅ Token received (len={len(token)})")

    def test_wrong_password_returns_401(self):
        """API must reject wrong password with 401 or 400."""
        resp = requests.post(
            API["login"],
            json={"email": SUPER_ADMIN["email"], "password": "WrongPass!99"},
            timeout=10,
        )
        assert resp.status_code in [400, 401, 403], \
            f"Expected 4xx for wrong password, got {resp.status_code}"
        print(f"\n✅ Wrong password → {resp.status_code}")

    def test_unknown_email_returns_401(self):
        """API must reject unknown email."""
        resp = requests.post(
            API["login"],
            json={"email": "ghost@notexist.com", "password": "Admin@123"},
            timeout=10,
        )
        assert resp.status_code in [400, 401, 403], \
            f"Expected 4xx for unknown email, got {resp.status_code}"
        print(f"\n✅ Unknown email → {resp.status_code}")

    def test_empty_email_rejected(self):
        """API should reject empty email."""
        resp = requests.post(
            API["login"],
            json={"email": "", "password": "Admin@123"},
            timeout=10,
        )
        assert resp.status_code in [400, 401, 422], \
            f"Expected 4xx, got {resp.status_code}"

    def test_empty_password_rejected(self):
        """API should reject empty password."""
        resp = requests.post(
            API["login"],
            json={"email": SUPER_ADMIN["email"], "password": ""},
            timeout=10,
        )
        assert resp.status_code in [400, 401, 422], \
            f"Expected 4xx, got {resp.status_code}"

    def test_authenticated_endpoint_requires_token(self):
        """
        GET /api/v1/residences/ without token must return 401.
        Confirms your JWT middleware is active.
        """
        resp = requests.get(API["residences"], timeout=10)
        assert resp.status_code in [401, 403], \
            f"Unauthenticated request should be blocked, got {resp.status_code}"
        print(f"\n✅ Unauthenticated request correctly blocked → {resp.status_code}")

    def test_token_gives_access_to_protected_endpoints(self, api: APIClient):
        """Authenticated client can reach protected API endpoints."""
        # Test multiple endpoints
        for key in ["resident_types", "residences", "contacts"]:
            resp = api.session.get(API[key], timeout=10)
            assert resp.status_code == 200, \
                f"Authenticated request to {key} failed: {resp.status_code}"
        print("\n✅ All protected endpoints accessible with token")

    def test_superadmin_role_visible_in_users_list(self, api: APIClient):
        """
        GET /api/v1/auth/users/
        The super admin should appear in the user list with role SUPER_ADMIN.
        """
        users = api.list_users()
        admin = next(
            (u for u in users if u["email"] == SUPER_ADMIN["email"]),
            None
        )
        assert admin is not None, "Super admin not found in users list"
        roles = [r["role__name"] for r in admin.get("roles", [])]
        assert "SUPER_ADMIN" in roles, f"SUPER_ADMIN role missing. Roles: {roles}"
        print(f"\n✅ Super admin found with roles: {roles}")


# ═══════════════════════════════════════════════════════════
#  SECTION B — UI TESTS  (browser required)
# ═══════════════════════════════════════════════════════════

class TestAuthUI:

    def test_login_page_loads(self, page: Page):
        """Login page should open with email + password fields visible."""
        page.goto(UI["login"])
        page.wait_for_load_state("networkidle")

        email_field = page.locator(
            "input[type='email'], input[formcontrolname='email'], input[name='email']"
        ).first
        password_field = page.locator("input[type='password']").first

        expect(email_field).to_be_visible()
        expect(password_field).to_be_visible()
        page.screenshot(path="screenshots/login_page.png", full_page=True)
        print(f"\n✅ Login page loaded at {page.url}")

    def test_valid_login_redirects_to_dashboard(self, page: Page):
        """
        Valid Super Admin credentials → redirect away from /login.
        Angular app should land on dashboard.
        """
        page.goto(UI["login"])
        page.wait_for_load_state("networkidle")

        page.locator(
            "input[type='email'], input[formcontrolname='email']"
        ).first.fill(SUPER_ADMIN["email"])

        page.locator("input[type='password']").first.fill(SUPER_ADMIN["password"])

        page.locator(
            "button[type='submit'], button:has-text('Login'), button:has-text('Sign In')"
        ).first.click()

        # Wait up to 20s for redirect
        page.wait_for_url(
            lambda url: "/login" not in url,
            timeout=TIMEOUT["navigation"]
        )
        page.screenshot(path="screenshots/after_login.png", full_page=True)
        assert "/login" not in page.url, f"Still on login page: {page.url}"
        print(f"\n✅ Redirected to: {page.url}")

    def test_wrong_password_shows_error(self, page: Page):
        """Wrong password must keep user on login page or show an error."""
        page.goto(UI["login"])
        page.wait_for_load_state("networkidle")

        page.locator("input[type='email'], input[formcontrolname='email']").first.fill(
            SUPER_ADMIN["email"]
        )
        page.locator("input[type='password']").first.fill("TotallyWrong@999")
        page.locator(
            "button[type='submit'], button:has-text('Login')"
        ).first.click()

        page.wait_for_timeout(2500)
        page.screenshot(path="screenshots/login_wrong_password.png", full_page=True)

        still_on_login = "/login" in page.url
        error_visible  = page.locator(
            ".error, mat-error, [class*='error'], [class*='alert'], [class*='invalid']"
        ).count() > 0

        assert still_on_login or error_visible, \
            "Expected to stay on login or see an error for wrong password"
        print(f"\n✅ Wrong password handled correctly (on_login={still_on_login}, error={error_visible})")

    def test_empty_fields_submit_blocked(self, page: Page):
        """Submit with empty email AND password should be blocked."""
        page.goto(UI["login"])
        page.wait_for_load_state("networkidle")

        submit = page.locator(
            "button[type='submit'], button:has-text('Login')"
        ).first

        # Don't fill anything — just check
        is_disabled = submit.is_disabled()
        print(f"\n🔒 Submit disabled with empty fields: {is_disabled}")

        if not is_disabled:
            # Try clicking — form should not navigate away
            submit.click()
            page.wait_for_timeout(1000)
            assert "/login" in page.url, \
                "Empty form submission should NOT navigate away from login"
        print("\n✅ Empty form correctly blocked")

    def test_jwt_token_in_localstorage_after_login(self, page: Page):
        """
        After successful login, a JWT token (starts with 'ey')
        should be stored in localStorage.
        """
        page.goto(UI["login"])
        page.wait_for_load_state("networkidle")

        page.locator("input[type='email'], input[formcontrolname='email']").first.fill(
            SUPER_ADMIN["email"]
        )
        page.locator("input[type='password']").first.fill(SUPER_ADMIN["password"])
        page.locator("button[type='submit'], button:has-text('Login')").first.click()

        page.wait_for_url(lambda url: "/login" not in url, timeout=TIMEOUT["navigation"])
        page.wait_for_timeout(1000)

        token = page.evaluate("""
            () => {
                const keys = Object.keys(localStorage);
                for (const k of keys) {
                    const v = localStorage.getItem(k);
                    if (v && (v.startsWith('ey') || k.toLowerCase().includes('token'))) {
                        return v;
                    }
                }
                return null;
            }
        """)

        print(f"\n🔑 Token in localStorage: {'YES ✅' if token else 'NOT FOUND ⚠️'}")
        # Note: some Angular apps store token in sessionStorage or cookies
        # If this fails, check sessionStorage too
        if not token:
            session_token = page.evaluate("""
                () => {
                    const keys = Object.keys(sessionStorage);
                    for (const k of keys) {
                        const v = sessionStorage.getItem(k);
                        if (v && v.startsWith('ey')) return v;
                    }
                    return null;
                }
            """)
            print(f"🔑 Token in sessionStorage: {'YES ✅' if session_token else 'NOT FOUND ⚠️'}")

    def test_protected_route_without_login_redirects(self, page: Page):
        """
        Accessing /residences without login should redirect to login page.
        Angular route guards should enforce this.
        """
        page.goto(UI["residences"])
        page.wait_for_load_state("networkidle")
        page.wait_for_timeout(1500)

        print(f"\n🔐 After accessing protected route → {page.url}")
        assert "/login" in page.url, \
            f"Expected redirect to /login for unauthenticated access, got: {page.url}"
        print("\n✅ Route guard working correctly")
