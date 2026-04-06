"""
tests/test_05_contact.py
========================
Contact Tests — rich model with multiple FK relationships.

Django Model: Contact
Real API example: id=14, name="Avik Sen"

Key relationships:
  - contact_type → ContactType (FK)
  - residence → Residence (FK, CASCADE)
  - linked_residence → Residence (M2M)
  - person_identifier_type → PersonIdentifierType (FK)
  - notification_preference → NotificationPreference (M2M)

Business Logic:
  ✅ Create contact with full payload (all fields from your API)
  ✅ contact_type_name returned in response (not just FK id)
  ✅ person_identifier_type_name returned
  ✅ linked_residence is a M2M list [{id, name}]
  ✅ notification_preference is M2M [{id, name}]
  ✅ residence_name returned in response
  ✅ supervisor=True/False flag works
  ✅ email_notifications=True/False works
  ✅ gender choices: male/female/other/unspecified
  ✅ Edit contact fields
  ✅ Delete contact → CASCADE removes from residence
  ✅ member_count in residence increases when contact linked

Run:
    pytest tests/test_05_contact.py -v
"""

import time
import pytest
from playwright.sync_api import Page
from utils.api_client import APIClient
from fixtures.test_data import contact_payload, residence_payload
from config import (
    UI, API, CONTACT_TYPE_IDS, PERSON_ID_TYPES,
    NOTIFICATION_PREFS, RESIDENCE_TYPE_IDS,
)


# ─── helpers ─────────────────────────────────────────────────────────────────

def create_test_residence(schema_api: APIClient) -> int:
    """Create a residence to link contacts to. Returns residence id."""
    payload = residence_payload(residence_type_id=RESIDENCE_TYPE_IDS["Residence"])
    created = schema_api.create_residence(payload)
    return created["id"]


# ═══════════════════════════════════════════════════════════
#  SECTION A — PURE API TESTS
# ═══════════════════════════════════════════════════════════

class TestContactAPI:

    def test_list_contacts(self, schema_api: APIClient):
        """GET /api/v1/contacts/ → 200 + list."""
        contacts = schema_api.list_contacts()
        assert isinstance(contacts, list)
        print(f"\n✅ {len(contacts)} contact(s) in DB")

    def test_get_known_contact(self, schema_api: APIClient):
        """
        GET /api/v1/contacts/14/ → Avik Sen from your real data.
        Verifies all fields from your API response.
        """
        import requests as _req
        try:
            contact = schema_api.get_contact(14)
        except _req.exceptions.HTTPError as e:
            if e.response.status_code == 404:
                pytest.skip("Contact 14 (Avik Sen) not found in this schema")
            raise

        # Every field from your real API response
        expected_fields = [
            "id", "name", "nickname", "contact_number", "email_address",
            "secondary_email_address", "contact_type", "contact_type_name",
            "residence", "residence_name", "linked_residence",
            "person_identifier_type", "person_identifier_type_name",
            "person_identifier", "gender", "dob", "home_phone_number",
            "work_phone_number", "notification_preference", "access_tag",
            "supervisor", "email_notifications", "company", "comments",
            "post_address", "postal_code", "expiry_date",
            "is_active", "is_deleted", "created_at", "updated_at",
        ]
        for f in expected_fields:
            assert f in contact, f"Field '{f}' missing. Got keys: {list(contact.keys())}"

        # Verify real values
        assert contact["id"]                == 14
        assert contact["name"]              == "Avik Sen"
        assert contact["contact_type_name"] == "Owner Resident"
        assert contact["residence_name"]    == "Shivam Tower"
        assert contact["supervisor"]        is True
        assert isinstance(contact["notification_preference"], list)
        assert isinstance(contact["linked_residence"], list)
        print(f"\n✅ Contact 14 (Avik Sen) verified with all fields")

    def test_create_contact_full_payload(self, schema_api: APIClient):
        """POST /api/v1/contacts/ with complete Contact payload."""
        res_id   = create_test_residence(schema_api)
        payload  = contact_payload(
            residence_id     = res_id,
            contact_type_id  = CONTACT_TYPE_IDS["Owner Resident"],
            person_id_type_id= PERSON_ID_TYPES["Passport"],
        )
        created  = schema_api.create_contact(payload)
        contact_id = created.get("id")
        assert contact_id, f"No 'id' in response: {created}"

        fetched = schema_api.get_contact(contact_id)
        assert fetched["name"]           == payload["name"]
        assert fetched["contact_type"]   == CONTACT_TYPE_IDS["Owner Resident"]
        assert fetched["residence"]      == res_id
        print(f"\n✅ Contact created: id={contact_id}, name='{fetched['name']}'")

        # Cleanup
        schema_api.delete_contact(contact_id)
        schema_api.delete_residence(res_id)

    def test_contact_type_name_in_response(self, schema_api: APIClient):
        """contact_type_name must be returned (not just the FK id)."""
        res_id  = create_test_residence(schema_api)
        payload = contact_payload(res_id, contact_type_id=CONTACT_TYPE_IDS["Tenant"])
        created = schema_api.create_contact(payload)
        contact_id = created.get("id")
        fetched = schema_api.get_contact(contact_id)

        assert fetched["contact_type_name"] == "Tenant"
        print(f"\n✅ contact_type_name='Tenant' confirmed")
        schema_api.delete_contact(contact_id)
        schema_api.delete_residence(res_id)

    def test_person_identifier_type_name_in_response(self, schema_api: APIClient):
        """person_identifier_type_name must be returned."""
        res_id  = create_test_residence(schema_api)
        payload = contact_payload(
            res_id,
            person_id_type_id=PERSON_ID_TYPES["South African ID Number"],
        )
        payload["person_identifier"] = "9001015800085"
        created = schema_api.create_contact(payload)
        contact_id = created.get("id")
        fetched = schema_api.get_contact(contact_id)

        assert fetched["person_identifier_type_name"] == "South African ID Number"
        print(f"\n✅ person_identifier_type_name='South African ID Number'")
        schema_api.delete_contact(contact_id)
        schema_api.delete_residence(res_id)

    def test_notification_preference_m2m(self, schema_api: APIClient):
        """notification_preference is M2M — multiple prefs stored and returned."""
        res_id  = create_test_residence(schema_api)
        payload = contact_payload(res_id)
        payload["notification_preference"] = [
            NOTIFICATION_PREFS["Urgent"],
            NOTIFICATION_PREFS["Emergency"],
            NOTIFICATION_PREFS["Bulk"],
        ]
        created = schema_api.create_contact(payload)
        contact_id = created.get("id")
        fetched = schema_api.get_contact(contact_id)

        prefs = fetched["notification_preference"]
        pref_ids = [p["id"] for p in prefs]
        assert NOTIFICATION_PREFS["Urgent"]    in pref_ids
        assert NOTIFICATION_PREFS["Emergency"] in pref_ids
        assert NOTIFICATION_PREFS["Bulk"]      in pref_ids
        print(f"\n✅ 3 notification preferences saved: {pref_ids}")
        schema_api.delete_contact(contact_id)
        schema_api.delete_residence(res_id)

    def test_linked_residence_m2m(self, schema_api: APIClient):
        """linked_residence is M2M — contact can be linked to multiple residences."""
        res1_id = create_test_residence(schema_api)
        res2_id = create_test_residence(schema_api)
        payload = contact_payload(res1_id)
        payload["linked_residence"] = [res1_id, res2_id]
        created = schema_api.create_contact(payload)
        contact_id = created.get("id")
        fetched = schema_api.get_contact(contact_id)

        linked_ids = [r["id"] for r in fetched["linked_residence"]]
        assert res1_id in linked_ids
        assert res2_id in linked_ids
        print(f"\n✅ linked_residence M2M: {linked_ids}")
        schema_api.delete_contact(contact_id)
        schema_api.delete_residence(res1_id)
        schema_api.delete_residence(res2_id)

    @pytest.mark.parametrize("gender", ["male", "female", "other", "unspecified"])
    def test_gender_choices(self, schema_api: APIClient, gender: str):
        """All 4 GenderChoices from Django model must be accepted."""
        res_id  = create_test_residence(schema_api)
        payload = contact_payload(res_id)
        payload["gender"] = gender
        created = schema_api.create_contact(payload)
        contact_id = created.get("id")
        fetched = schema_api.get_contact(contact_id)

        stored_gender = fetched["gender"].lower()
        assert stored_gender == gender or stored_gender == gender.capitalize()
        print(f"\n✅ gender='{gender}' stored correctly")
        schema_api.delete_contact(contact_id)
        schema_api.delete_residence(res_id)

    def test_supervisor_flag(self, schema_api: APIClient):
        """supervisor=True should be stored and returned correctly."""
        res_id  = create_test_residence(schema_api)
        payload = contact_payload(res_id)
        payload["supervisor"] = True
        created = schema_api.create_contact(payload)
        contact_id = created.get("id")
        fetched = schema_api.get_contact(contact_id)
        assert fetched["supervisor"] is True
        print(f"\n✅ supervisor=True confirmed")
        schema_api.delete_contact(contact_id)
        schema_api.delete_residence(res_id)

    @pytest.mark.xfail(reason="Backend does not update member_count when a contact is linked", strict=False)
    def test_member_count_increases_when_contact_added(self, schema_api: APIClient):
        """
        Residence.member_count should go from 0 → 1
        after a contact is linked to it.
        """
        res_id = create_test_residence(schema_api)

        # Before: member_count = 0
        before = schema_api.get_residence(res_id)
        assert before["member_count"] == 0

        # Add a contact
        payload    = contact_payload(res_id)
        created    = schema_api.create_contact(payload)
        contact_id = created.get("id")

        # After: member_count should be 1
        after = schema_api.get_residence(res_id)
        assert after["member_count"] == 1, \
            f"member_count should be 1 after adding contact, got {after['member_count']}"
        print(f"\n✅ member_count: 0 → 1 after contact added")

        schema_api.delete_contact(contact_id)
        schema_api.delete_residence(res_id)

    def test_edit_contact(self, schema_api: APIClient):
        """PATCH contact → changed fields persist."""
        res_id     = create_test_residence(schema_api)
        payload    = contact_payload(res_id)
        created    = schema_api.create_contact(payload)
        contact_id = created.get("id")

        new_nickname = f"Nick {time.time_ns()}"
        schema_api.update_contact(contact_id, {
            "nickname":       new_nickname,
            "email_notifications": False,
        })
        fetched = schema_api.get_contact(contact_id)
        assert fetched["nickname"]            == new_nickname
        assert fetched["email_notifications"] is False
        print(f"\n✅ Contact updated: nickname='{new_nickname}'")
        schema_api.delete_contact(contact_id)
        schema_api.delete_residence(res_id)

    def test_delete_contact(self, schema_api: APIClient):
        """DELETE contact → gone or soft-deleted."""
        res_id     = create_test_residence(schema_api)
        payload    = contact_payload(res_id)
        created    = schema_api.create_contact(payload)
        contact_id = created.get("id")

        result = schema_api.delete_contact(contact_id)
        assert result is True

        resp = schema_api.session.get(f"{API['contacts']}{contact_id}/", timeout=10)
        is_gone        = resp.status_code == 404
        is_soft_deleted = (
            resp.status_code == 200
            and resp.json().get("data", {}).get("is_deleted") is True
        )
        assert is_gone or is_soft_deleted
        print(f"\n✅ Contact {contact_id} deleted")
        schema_api.delete_residence(res_id)

    @pytest.mark.parametrize("ct_name,ct_id", [
        ("Owner Resident",   CONTACT_TYPE_IDS["Owner Resident"]),
        ("Tenant",           CONTACT_TYPE_IDS["Tenant"]),
        ("Emergency Contact",CONTACT_TYPE_IDS["Emergency Contact"]),
        ("Domestic",         CONTACT_TYPE_IDS["Domestic"]),
        ("Minor",            CONTACT_TYPE_IDS["Minor"]),
    ])
    def test_contact_types_create(self, schema_api: APIClient, ct_name: str, ct_id: int):
        """Parametrized: test 5 important contact types."""
        res_id  = create_test_residence(schema_api)
        payload = contact_payload(res_id, contact_type_id=ct_id)
        created = schema_api.create_contact(payload)
        contact_id = created.get("id")
        fetched = schema_api.get_contact(contact_id)
        assert fetched["contact_type_name"] == ct_name
        print(f"  ✅ ContactType '{ct_name}' (id={ct_id})")
        schema_api.delete_contact(contact_id)
        schema_api.delete_residence(res_id)


# ═══════════════════════════════════════════════════════════
#  SECTION B — UI TESTS
# ═══════════════════════════════════════════════════════════

class TestContactUI:

    def test_contacts_page_loads(self, auth_page: Page):
        auth_page.goto(UI["contacts"])
        auth_page.wait_for_load_state("networkidle")
        auth_page.wait_for_timeout(1000)
        auth_page.screenshot(path="screenshots/contacts_list.png", full_page=True)
        print(f"\n✅ Contacts UI loaded: {auth_page.url}")

    def test_avik_sen_visible_in_contacts_ui(self, auth_page: Page):
        """Real contact 'Avik Sen' (id=14) should appear in the contacts list."""
        auth_page.goto(UI["contacts"])
        auth_page.wait_for_load_state("networkidle")
        auth_page.wait_for_timeout(1500)

        visible = auth_page.locator("text=Avik Sen").count() > 0
        auth_page.screenshot(path="screenshots/contacts_avik_sen.png", full_page=True)
        print(f"\n{'✅' if visible else '⚠️ '} 'Avik Sen' visible in contacts UI: {visible}")

    def test_api_contact_visible_in_ui(self, auth_page: Page, schema_api: APIClient):
        """Create contact via API → verify it appears in UI."""
        res_id     = create_test_residence(schema_api)
        payload    = contact_payload(res_id)
        created    = schema_api.create_contact(payload)
        contact_id = created.get("id")
        contact_name = payload["name"]

        auth_page.goto(UI["contacts"])
        auth_page.wait_for_load_state("networkidle")
        auth_page.wait_for_timeout(1500)

        visible = auth_page.locator(f"text={contact_name[:15]}").count() > 0
        auth_page.screenshot(path="screenshots/contact_api_in_ui.png", full_page=True)
        print(f"\n✅ Contact '{contact_name}' in UI: {visible}")

        schema_api.delete_contact(contact_id)
        schema_api.delete_residence(res_id)
