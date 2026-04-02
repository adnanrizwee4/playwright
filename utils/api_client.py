"""
utils/api_client.py
===================
Direct API client for your Django REST backend.
Used for:
  - Getting auth token before UI tests
  - Creating seed data via API (faster than UI)
  - Validating DB state after UI actions

All endpoints match your actual Django URL patterns.
"""

import requests
from config import API, SUPER_ADMIN, TIMEOUT


class APIClient:
    """Thin wrapper around requests for your estate management API."""

    def __init__(self, token: str = None, schema_name: str = None):
        self.session     = requests.Session()
        self.token       = token
        self.schema_name = schema_name
        if token:
            self.session.headers.update({
                "Authorization": f"Bearer {token}",
                "Content-Type":  "application/json",
            })
        if schema_name:
            self.session.headers.update({"x-estate-schema": schema_name})

    def set_schema(self, schema_name: str) -> "APIClient":
        """Set (or update) the x-estate-schema header on all future requests."""
        self.schema_name = schema_name
        self.session.headers.update({"x-estate-schema": schema_name})
        return self

    # ── Auth ──────────────────────────────────────────────────────────────────

    @classmethod
    def login(
        cls,
        email: str = None,
        password: str = None,
        schema_name: str = None,
    ) -> "APIClient":
        """Login and return an authenticated APIClient instance."""
        email    = email    or SUPER_ADMIN["email"]
        password = password or SUPER_ADMIN["password"]

        resp = requests.post(
            API["login"],
            json={"email": email, "password": password},
            timeout=TIMEOUT["api"],
        )
        assert resp.status_code == 200, \
            f"Login failed [{resp.status_code}]: {resp.text}"

        body  = resp.json()
        # Your API may return token under different keys — try all common ones
        token = (
            body.get("token")
            or body.get("access_token")
            or body.get("access")
            or body.get("data", {}).get("token")
            or body.get("data", {}).get("access_token")
        )
        assert token, f"Token not found in login response: {body}"
        return cls(token=token, schema_name=schema_name)

    # ── Estate (Super Admin scope) ────────────────────────────────────────────

    def list_estates(self) -> list:
        r = self.session.get(API["estates"], timeout=TIMEOUT["api"])
        r.raise_for_status()
        body = r.json()
        return body.get("results") or body.get("data") or body

    def get_estate(self, estate_id: int) -> dict:
        r = self.session.get(f"{API['estates']}{estate_id}/", timeout=TIMEOUT["api"])
        r.raise_for_status()
        return r.json().get("data") or r.json()

    def create_estate(self, payload: dict) -> dict:
        r = self.session.post(API["estates"], json=payload, timeout=TIMEOUT["api"])
        assert r.status_code in [200, 201], f"Create estate failed: {r.text}"
        return r.json().get("data") or r.json()

    def delete_estate(self, estate_id: int) -> bool:
        r = self.session.delete(f"{API['estates']}{estate_id}/", timeout=TIMEOUT["api"])
        return r.status_code in [200, 204]

    # ── Resident Types ────────────────────────────────────────────────────────

    def list_resident_types(self) -> list:
        r = self.session.get(API["resident_types"], timeout=TIMEOUT["api"])
        r.raise_for_status()
        return r.json().get("data") or r.json()

    def create_resident_type(self, payload: dict) -> dict:
        r = self.session.post(API["resident_types"], json=payload, timeout=TIMEOUT["api"])
        assert r.status_code in [200, 201], f"Create resident type failed: {r.text}"
        return r.json().get("data") or r.json()

    def get_resident_type(self, type_id: int) -> dict:
        r = self.session.get(f"{API['resident_types']}{type_id}/", timeout=TIMEOUT["api"])
        r.raise_for_status()
        return r.json().get("data") or r.json()

    def update_resident_type(self, type_id: int, payload: dict) -> dict:
        r = self.session.patch(f"{API['resident_types']}{type_id}/", json=payload, timeout=TIMEOUT["api"])
        r.raise_for_status()
        return r.json().get("data") or r.json()

    def delete_resident_type(self, type_id: int) -> bool:
        r = self.session.delete(f"{API['resident_types']}{type_id}/", timeout=TIMEOUT["api"])
        return r.status_code in [200, 204]

    # ── Residences ────────────────────────────────────────────────────────────

    def list_residences(self) -> list:
        r = self.session.get(API["residences"], timeout=TIMEOUT["api"])
        r.raise_for_status()
        return r.json().get("data") or r.json()

    def get_residence(self, res_id: int) -> dict:
        r = self.session.get(f"{API['residences']}{res_id}/", timeout=TIMEOUT["api"])
        r.raise_for_status()
        return r.json().get("data") or r.json()

    def create_residence(self, payload: dict) -> dict:
        """
        Required fields (from your model + API response):
          name, residence_type (id)
        Optional: account_no, address, city, postal_code,
                  house_no, street, suburb, erf, etc.
        """
        r = self.session.post(API["residences"], json=payload, timeout=TIMEOUT["api"])
        assert r.status_code in [200, 201], f"Create residence failed: {r.text}"
        return r.json().get("data") or r.json()

    def update_residence(self, res_id: int, payload: dict) -> dict:
        r = self.session.patch(f"{API['residences']}{res_id}/", json=payload, timeout=TIMEOUT["api"])
        r.raise_for_status()
        return r.json().get("data") or r.json()

    def delete_residence(self, res_id: int) -> bool:
        r = self.session.delete(f"{API['residences']}{res_id}/", timeout=TIMEOUT["api"])
        return r.status_code in [200, 204]

    # ── Contacts ──────────────────────────────────────────────────────────────

    def list_contacts(self) -> list:
        r = self.session.get(API["contacts"], timeout=TIMEOUT["api"])
        r.raise_for_status()
        return r.json().get("data") or r.json()

    def get_contact(self, contact_id: int) -> dict:
        r = self.session.get(f"{API['contacts']}{contact_id}/", timeout=TIMEOUT["api"])
        r.raise_for_status()
        return r.json().get("data") or r.json()

    def create_contact(self, payload: dict) -> dict:
        """
        Key fields (Contact model):
          name (required), contact_number, email_address,
          contact_type (id), residence (id), gender,
          person_identifier_type (id), person_identifier,
          notification_preference (list of ids)
        """
        r = self.session.post(API["contacts"], json=payload, timeout=TIMEOUT["api"])
        assert r.status_code in [200, 201], f"Create contact failed: {r.text}"
        return r.json().get("data") or r.json()

    def update_contact(self, contact_id: int, payload: dict) -> dict:
        r = self.session.patch(f"{API['contacts']}{contact_id}/", json=payload, timeout=TIMEOUT["api"])
        r.raise_for_status()
        return r.json().get("data") or r.json()

    def delete_contact(self, contact_id: int) -> bool:
        r = self.session.delete(f"{API['contacts']}{contact_id}/", timeout=TIMEOUT["api"])
        return r.status_code in [200, 204]

    # ── Visitor Schedules ─────────────────────────────────────────────────────

    def list_visitor_schedules(self) -> list:
        r = self.session.get(API["visitor_schedules"], timeout=TIMEOUT["api"])
        r.raise_for_status()
        return r.json().get("data") or r.json()

    def get_visitor_schedule(self, schedule_id: int) -> dict:
        r = self.session.get(f"{API['visitor_schedules']}{schedule_id}/", timeout=TIMEOUT["api"])
        r.raise_for_status()
        return r.json().get("data") or r.json()

    def create_visitor_schedule(self, payload: dict) -> dict:
        """
        Key fields (VisitorSchedule model):
          visitor_name (required), contact_number, email_address,
          residence (id), visitor_type (id), status,
          scheduled_from, scheduled_to,
          person_identifier_type (id), person_identifier,
          gender, days_selection, monday..sunday (booleans)
        """
        r = self.session.post(API["visitor_schedules"], json=payload, timeout=TIMEOUT["api"])
        assert r.status_code in [200, 201], f"Create visitor schedule failed: {r.text}"
        return r.json().get("data") or r.json()

    def update_visitor_schedule(self, schedule_id: int, payload: dict) -> dict:
        r = self.session.patch(
            f"{API['visitor_schedules']}{schedule_id}/", json=payload, timeout=TIMEOUT["api"]
        )
        r.raise_for_status()
        return r.json().get("data") or r.json()

    def delete_visitor_schedule(self, schedule_id: int) -> bool:
        r = self.session.delete(f"{API['visitor_schedules']}{schedule_id}/", timeout=TIMEOUT["api"])
        return r.status_code in [200, 204]

    # ── Lookup helpers ────────────────────────────────────────────────────────

    def list_contact_types(self) -> list:
        r = self.session.get(API["contact_types"], timeout=TIMEOUT["api"])
        r.raise_for_status()
        return r.json().get("data") or r.json()

    def list_visitor_types(self) -> list:
        r = self.session.get(API["visitor_types"], timeout=TIMEOUT["api"])
        r.raise_for_status()
        return r.json().get("data") or r.json()

    def list_person_identifier_types(self) -> list:
        r = self.session.get(API["person_identifier_types"], timeout=TIMEOUT["api"])
        r.raise_for_status()
        return r.json().get("data") or r.json()

    def list_notification_preferences(self) -> list:
        r = self.session.get(API["notification_prefs"], timeout=TIMEOUT["api"])
        r.raise_for_status()
        return r.json().get("data") or r.json()

    def list_users(self) -> list:
        r = self.session.get(API["users"], timeout=TIMEOUT["api"])
        r.raise_for_status()
        body = r.json()
        return body.get("results") or body.get("data") or body
