"""
fixtures/test_data.py
=====================
Test data factories matching your exact Django model fields.
All field names come from your real API responses.
"""

import time
from faker import Faker
from config import (
    RESIDENCE_TYPE_IDS, CONTACT_TYPE_IDS,
    PERSON_ID_TYPES, NOTIFICATION_PREFS,
    VISITOR_TYPE_IDS, VISIT_STATUS,
)

fake = Faker()

# ── Estate (Super Admin model) ────────────────────────────────────────────────

def estate_payload(name: str = None) -> dict:
    """
    Matches Estate model:
      name, schema_name, address, city, status
    """
    tag = str(time.time_ns())[-6:]
    n   = name or f"Test Estate {tag}"
    return {
        "name":    n,
        "address": fake.street_address(),
        "city":    fake.city(),
        "status":  "active",
    }

# ── Residence Type (ResidenceType model) ──────────────────────────────────────

def resident_type_payload(name: str = None) -> dict:
    """
    Matches ResidenceType model:
      name, description
    """
    return {
        "name":        name or f"Type {time.time_ns()}",
        "description": fake.sentence(nb_words=6),
    }

# ── Residence (Residence model — full field set from API response) ─────────────

def residence_payload(
    residence_type_id: int = RESIDENCE_TYPE_IDS["Residence"],
    name: str = None,
) -> dict:
    """
    Matches Residence model fields visible in your API response:
      name, residence_type, account_no, billing_account_no,
      address, city, postal_code, house_no, street, suburb,
      township, village, scheme, scheme_no, section_no, sub_no,
      erf, portion, erf_extent_m2, building_floor_m2,
      building_footprint_m2, building_no_of_floors,
      max_number_of_adults, max_number_of_minors,
      max_number_of_parking_bays, latitude, longitude,
      comments, postal_address
    """
    tag = str(time.time_ns())[-5:]
    return {
        "name":                     name or f"R-{tag}",
        "residence_type":           residence_type_id,
        "account_no":               f"ACC{tag}",
        "billing_account_no":       f"BILL{tag}",
        "address":                  fake.street_address(),
        "city":                     "Pretoria",
        "postal_code":              "700100",
        "house_no":                 str(fake.building_number()),
        "street":                   fake.street_name(),
        "suburb":                   fake.city_suffix(),
        "township":                 fake.city(),
        "village":                  fake.city(),
        "scheme":                   f"Scheme {tag}",
        "scheme_no":                tag,
        "section_no":               tag,
        "sub_no":                   tag,
        "erf":                      tag,
        "portion":                  fake.word(),
        "erf_extent_m2":            fake.random_int(min=100, max=500),
        "building_floor_m2":        fake.random_int(min=50, max=300),
        "building_footprint_m2":    fake.random_int(min=50, max=200),
        "building_no_of_floors":    fake.random_int(min=1, max=10),
        "max_number_of_adults":     fake.random_int(min=2, max=10),
        "max_number_of_minors":     fake.random_int(min=0, max=5),
        "max_number_of_parking_bays": fake.random_int(min=1, max=4),
        "latitude":                 str(round(fake.latitude(), 4)),
        "longitude":                str(round(fake.longitude(), 4)),
        "comments":                 fake.sentence(),
        "postal_address":           fake.address(),
        "date_registered":          "2026-01-01",
    }

# ── Contact (Contact model — full field set from API) ─────────────────────────

def contact_payload(
    residence_id: int,
    contact_type_id: int = CONTACT_TYPE_IDS["Owner Resident"],
    person_id_type_id: int = PERSON_ID_TYPES["Passport"],
) -> dict:
    """
    Matches Contact model fields from your API response:
      name, nickname, contact_number, email_address,
      secondary_email_address, contact_type, residence,
      linked_residence, gender, dob, home_phone_number,
      work_phone_number, person_identifier_type, person_identifier,
      expiry_date, notification_preference, access_tag,
      company, supervisor, email_notifications, comments,
      post_address, postal_code
    """
    return {
        "name":                    fake.name(),
        "nickname":                fake.first_name(),
        "contact_number":          fake.numerify("9########"),
        "email_address":           fake.email(),
        "secondary_email_address": fake.email(),
        "contact_type":            contact_type_id,
        "residence":               residence_id,
        "linked_residence":        [residence_id],
        "gender":                  "male",
        "dob":                     "1990-06-15",
        "home_phone_number":       fake.numerify("6########"),
        "work_phone_number":       fake.numerify("7########"),
        "person_identifier_type":  person_id_type_id,
        "person_identifier":       fake.numerify("#########"),
        "expiry_date":             "2030-12-31",
        "notification_preference": [
            NOTIFICATION_PREFS["Urgent"],
            NOTIFICATION_PREFS["Emergency"],
        ],
        "access_tag":              "GENERAL",
        "company":                 fake.company(),
        "supervisor":              False,
        "email_notifications":     True,
        "comments":                fake.sentence(),
        "post_address":            fake.address(),
        "postal_code":             "700100",
    }

# ── Visitor Schedule (VisitorSchedule model — full field set) ─────────────────

def visitor_schedule_payload(
    residence_id: int,
    visitor_type_id: int = VISITOR_TYPE_IDS["Visitor"],
    person_id_type_id: int = PERSON_ID_TYPES["Passport"],
    status: str = VISIT_STATUS["scheduled"],
) -> dict:
    """
    Matches VisitorSchedule model fields from your API:
      visitor_name, contact_number, email_address,
      residence, visitor_type, person_identifier_type, person_identifier,
      gender, dob, company, designation, message,
      send_sms, shared, status,
      scheduled_from, scheduled_to,
      days_selection, monday..sunday,
      comments, supervisor_comment,
      undesired, blocked
    """
    return {
        "visitor_name":            fake.name(),
        "contact_number":          fake.numerify("9########"),
        "email_address":           fake.email(),
        "residence":               residence_id,
        "visitor_type":            visitor_type_id,
        "person_identifier_type":  person_id_type_id,
        "person_identifier":       fake.numerify("#########"),
        "gender":                  "male",
        "dob":                     "1995-03-20",
        "company":                 fake.company(),
        "designation":             fake.job(),
        "message":                 fake.sentence(),
        "send_sms":                False,
        "shared":                  False,
        "status":                  status,
        "scheduled_from":          "2026-04-01T09:00:00Z",
        "scheduled_to":            "2026-12-31T18:00:00Z",
        "days_selection":          True,
        "monday":                  True,
        "tuesday":                 True,
        "wednesday":               True,
        "thursday":                True,
        "friday":                  True,
        "saturday":                False,
        "sunday":                  False,
        "comments":                fake.sentence(),
        "supervisor_comment":      "",
        "undesired":               False,
        "blocked":                 False,
        "external_id":             fake.numerify("#####"),
        "tmt_external_id":         fake.numerify("#####"),
    }

# ── Negative/invalid payloads ─────────────────────────────────────────────────

INVALID_LOGIN_CASES = [
    {"email": "wrong@estate.com", "password": "BadPass",       "label": "wrong credentials"},
    {"email": "",                 "password": "Admin@123",      "label": "empty email"},
    {"email": "admin@estate.com", "password": "",               "label": "empty password"},
    {"email": "notanemail",       "password": "Admin@123",      "label": "invalid email format"},
    {"email": "admin@estate.com", "password": "a",              "label": "too short password"},
]

INVALID_RESIDENCE_CASES = {
    "missing_name":  {"residence_type": RESIDENCE_TYPE_IDS["Residence"]},
    "missing_type":  {"name": "No-Type-Res"},
    "long_name":     {"name": "A" * 300, "residence_type": RESIDENCE_TYPE_IDS["Residence"]},
}

INVALID_CONTACT_CASES = {
    "missing_name":   {"contact_number": "9876543210"},
    "invalid_email":  {"name": "Test", "email_address": "notanemail"},
}
