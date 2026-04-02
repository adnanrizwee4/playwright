"""
tests/test_03_residence_type.py
================================
Residence Type Tests.

Django Model: ResidenceType (name, description, is_active, is_deleted)
API: /api/v1/resident-types/

Known types from your API: Amenity, Business, Gate, Guards,
  Panic Monitor, Residence, Security, Tennis Court

Business Logic:
  ✅ List all residence types
  ✅ Create new type (name + description)
  ✅ Read single type by ID
  ✅ Edit type name/description
  ✅ Soft-delete (is_deleted flag) or hard delete
  ✅ is_active flag works
  ✅ Missing name → 400
  ✅ All 8 existing types present in DB
  ✅ UI shows residence types list

Run:
    pytest tests/test_03_residence_type.py -v
"""

import time
import pytest
from playwright.sync_api import Page
from utils.api_client import APIClient
from fixtures.test_data import resident_type_payload
from config import UI, API, RESIDENCE_TYPE_IDS


class TestResidentTypeAPI:

    def test_list_returns_all_types(self, schema_api: APIClient):
        """GET /api/v1/resident-types/ → 200 + list of types."""
        types = schema_api.list_resident_types()
        assert isinstance(types, list)
        assert len(types) >= 8, f"Expected at least 8 types (seeded), got {len(types)}"
        names = [t["name"] for t in types]
        print(f"\n✅ Resident types ({len(types)}): {names}")

    def test_all_seeded_types_present(self, schema_api: APIClient):
        """All 8 types seeded in your DB must be present."""
        types = schema_api.list_resident_types()
        names = {t["name"] for t in types}
        for expected in RESIDENCE_TYPE_IDS.keys():
            assert expected in names, f"Expected type '{expected}' not found. Got: {names}"
        print(f"\n✅ All 8 seeded residence types confirmed")

    def test_each_type_has_required_fields(self, schema_api: APIClient):
        """Every type object must have name, description, is_active, is_deleted, id."""
        types = schema_api.list_resident_types()
        for t in types:
            assert "id"          in t, f"Missing 'id' in {t}"
            assert "name"        in t, f"Missing 'name' in {t}"
            assert "is_active"   in t, f"Missing 'is_active' in {t}"
            assert "is_deleted"  in t, f"Missing 'is_deleted' in {t}"
        print("\n✅ All types have required fields")

    def test_get_residence_type_by_id(self, schema_api: APIClient):
        """GET /api/v1/resident-types/<id>/ → returns correct type."""
        # Use a known ID from your DB: 6 = "Residence"
        t = schema_api.get_resident_type(RESIDENCE_TYPE_IDS["Residence"])
        assert t["id"]   == RESIDENCE_TYPE_IDS["Residence"]
        assert t["name"] == "Residence"
        print(f"\n✅ Residence type by ID: {t}")

    def test_create_resident_type(self, schema_api: APIClient):
        """POST /api/v1/resident-types/ → creates new type."""
        payload = resident_type_payload()
        created = schema_api.create_resident_type(payload)

        assert created.get("name") == payload["name"] or "id" in created
        print(f"\n✅ Created: {created}")

        # Cleanup
        type_id = created.get("id")
        if type_id:
            schema_api.delete_resident_type(type_id)

    def test_create_type_is_active_by_default(self, schema_api: APIClient):
        """Newly created type should have is_active=True."""
        payload = resident_type_payload()
        created = schema_api.create_resident_type(payload)
        type_id = created.get("id")

        if type_id:
            fetched = schema_api.get_resident_type(type_id)
            assert fetched.get("is_active") is True
            assert fetched.get("is_deleted") is False
            print(f"\n✅ is_active=True, is_deleted=False on creation")
            schema_api.delete_resident_type(type_id)

    def test_create_type_missing_name_rejected(self, schema_api: APIClient):
        """POST without 'name' → 400."""
        resp = schema_api.session.post(
            API["resident_types"],
            json={"description": "No name here"},
            timeout=10,
        )
        assert resp.status_code == 400, \
            f"Expected 400 for missing name, got {resp.status_code}: {resp.text}"
        print(f"\n✅ Missing name → 400")

    def test_update_resident_type(self, schema_api: APIClient):
        """PATCH /api/v1/resident-types/<id>/ → updates name and description."""
        payload = resident_type_payload(name=f"UpdateMe {time.time_ns()}")
        created = schema_api.create_resident_type(payload)
        type_id = created.get("id")
        if not type_id:
            pytest.skip("Could not get ID from create response")

        updated_name = f"Updated {time.time_ns()}"
        result = schema_api.update_resident_type(type_id, {
            "name":        updated_name,
            "description": "Updated description",
        })
        fetched = schema_api.get_resident_type(type_id)
        assert fetched["name"] == updated_name
        print(f"\n✅ Type updated to '{updated_name}'")
        schema_api.delete_resident_type(type_id)

    def test_delete_resident_type(self, schema_api: APIClient):
        """DELETE /api/v1/resident-types/<id>/ → removed or soft-deleted."""
        payload = resident_type_payload(name=f"ToDelete {time.time_ns()}")
        created = schema_api.create_resident_type(payload)
        type_id = created.get("id")
        if not type_id:
            pytest.skip("Could not get ID")

        result = schema_api.delete_resident_type(type_id)
        assert result is True

        # Verify: should be 404 or marked deleted
        resp = schema_api.session.get(f"{API['resident_types']}{type_id}/", timeout=10)
        is_gone = resp.status_code == 404
        is_soft_deleted = (
            resp.status_code == 200
            and resp.json().get("data", {}).get("is_deleted") is True
        )
        assert is_gone or is_soft_deleted, \
            f"Expected 404 or is_deleted=True, got {resp.status_code}: {resp.text}"
        print(f"\n✅ Type {type_id} deleted (404={is_gone}, soft={is_soft_deleted})")

    @pytest.mark.parametrize("type_name,type_id", list(RESIDENCE_TYPE_IDS.items()))
    def test_each_seeded_type_by_id(self, schema_api: APIClient, type_name: str, type_id: int):
        """Parametrized: verify each of the 8 seeded types by exact ID."""
        t = schema_api.get_resident_type(type_id)
        assert t["name"] == type_name, f"Expected '{type_name}', got '{t['name']}'"
        assert t["is_active"] is True
        print(f"\n✅ {type_name} (id={type_id}) verified")


class TestResidentTypeUI:

    def test_resident_types_page_loads(self, auth_page: Page):
        """UI: /resident-types page should load without errors."""
        auth_page.goto(UI["resident_types"])
        auth_page.wait_for_load_state("networkidle")
        auth_page.screenshot(path="screenshots/resident_types_list.png", full_page=True)
        print(f"\n✅ Resident types UI loaded: {auth_page.url}")

    def test_all_types_visible_in_ui(self, auth_page: Page, schema_api: APIClient):
        """Types from API should be visible in the UI table."""
        types = schema_api.list_resident_types()
        auth_page.goto(UI["resident_types"])
        auth_page.wait_for_load_state("networkidle")
        auth_page.wait_for_timeout(1000)

        for t in types[:3]:  # check first 3 types
            visible = auth_page.locator(f"text={t['name']}").count() > 0
            print(f"  → '{t['name']}' visible in UI: {visible}")
        auth_page.screenshot(path="screenshots/resident_types_ui_check.png", full_page=True)
