"""
tests/test_07_lookups.py
=========================
Lookup / Choice Table Tests.

Tests all the small lookup endpoints that power dropdowns:
  - /api/v1/contact-types/
  - /api/v1/person_identifier_types/
  - /api/v1/notification-preferences/
  - /api/v1/visitor-types/

Business Logic:
  ✅ Each endpoint returns 200 + non-empty list
  ✅ All seeded values from your DB are present
  ✅ Each item has: id, name, description, is_active, is_deleted
  ✅ All seeded items are is_active=True, is_deleted=False

Run:
    pytest tests/test_07_lookups.py -v
"""

import pytest
from utils.api_client import APIClient
from config import (
    API, CONTACT_TYPE_IDS, PERSON_ID_TYPES,
    NOTIFICATION_PREFS, VISITOR_TYPE_IDS,
)


class TestContactTypesAPI:

    def test_list_contact_types(self, api: APIClient):
        types = api.list_contact_types()
        assert isinstance(types, list)
        assert len(types) >= 13
        print(f"\n✅ {len(types)} contact types")

    def test_all_seeded_contact_types_present(self, api: APIClient):
        types = api.list_contact_types()
        names = {t["name"] for t in types}
        for name in CONTACT_TYPE_IDS:
            assert name in names, f"'{name}' missing from contact types"
        print(f"\n✅ All 13 contact types confirmed")

    def test_contact_type_fields(self, api: APIClient):
        types = api.list_contact_types()
        for t in types:
            for field in ["id", "name", "description", "is_active", "is_deleted"]:
                assert field in t
            assert t["is_active"]  is True
            assert t["is_deleted"] is False
        print(f"\n✅ All contact type fields correct")

    @pytest.mark.parametrize("name,expected_id", list(CONTACT_TYPE_IDS.items()))
    def test_each_contact_type_by_name(self, api: APIClient, name: str, expected_id: int):
        types = api.list_contact_types()
        match = next((t for t in types if t["name"] == name), None)
        assert match is not None, f"'{name}' not found"
        assert match["id"] == expected_id, \
            f"Expected id={expected_id} for '{name}', got {match['id']}"
        print(f"  ✅ {name} → id={expected_id}")


class TestPersonIdentifierTypesAPI:

    def test_list_person_identifier_types(self, api: APIClient):
        types = api.list_person_identifier_types()
        assert isinstance(types, list)
        assert len(types) >= 7
        print(f"\n✅ {len(types)} person identifier types")

    def test_all_seeded_identifier_types(self, api: APIClient):
        types = api.list_person_identifier_types()
        names = {t["name"] for t in types}
        for name in PERSON_ID_TYPES:
            assert name in names, f"'{name}' missing"
        print(f"\n✅ All 7 person identifier types confirmed")

    def test_passport_id_is_16(self, api: APIClient):
        """From your real API: Passport = id 16."""
        types = api.list_person_identifier_types()
        passport = next((t for t in types if t["name"] == "Passport"), None)
        assert passport is not None
        assert passport["id"] == 16
        print(f"\n✅ Passport id=16 confirmed")

    def test_south_african_id_is_15(self, api: APIClient):
        types = api.list_person_identifier_types()
        sa_id = next((t for t in types if t["name"] == "South African ID Number"), None)
        assert sa_id is not None
        assert sa_id["id"] == 15
        print(f"\n✅ South African ID Number id=15 confirmed")


class TestNotificationPreferencesAPI:

    def test_list_notification_prefs(self, api: APIClient):
        prefs = api.list_notification_preferences()
        assert isinstance(prefs, list)
        assert len(prefs) >= 6
        print(f"\n✅ {len(prefs)} notification preferences")

    def test_all_seeded_prefs_present(self, api: APIClient):
        prefs = api.list_notification_preferences()
        names = {p["name"] for p in prefs}
        for name in NOTIFICATION_PREFS:
            assert name in names, f"'{name}' missing from prefs"
        print(f"\n✅ All 6 notification preferences confirmed")

    def test_pref_ids_match_expected(self, api: APIClient):
        prefs  = api.list_notification_preferences()
        id_map = {p["name"]: p["id"] for p in prefs}
        for name, expected_id in NOTIFICATION_PREFS.items():
            assert id_map.get(name) == expected_id, \
                f"'{name}' expected id={expected_id}, got {id_map.get(name)}"
        print(f"\n✅ All notification preference IDs match")


class TestVisitorTypesAPI:

    def test_list_visitor_types(self, api: APIClient):
        types = api.list_visitor_types()
        assert isinstance(types, list)
        assert len(types) >= 5
        print(f"\n✅ {len(types)} visitor types")

    def test_all_seeded_visitor_types(self, api: APIClient):
        types = api.list_visitor_types()
        names = {t["name"] for t in types}
        for name in VISITOR_TYPE_IDS:
            assert name in names, f"'{name}' missing"
        print(f"\n✅ All 5 visitor types confirmed")

    def test_visitor_type_visitor_id_is_5(self, api: APIClient):
        """From your real API: 'Visitor' type = id 5."""
        types  = api.list_visitor_types()
        visitor = next((t for t in types if t["name"] == "Visitor"), None)
        assert visitor is not None
        assert visitor["id"] == 5
        print(f"\n✅ 'Visitor' type id=5 confirmed")
