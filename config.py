"""
config.py
=========
Central config for the Estate Management test suite.
All values come from your real API responses and Django models.
"""

# ── Base URLs ─────────────────────────────────────────────────────────────────
BASE_UI  = "http://192.168.0.129:4200"
BASE_API = "http://192.168.0.155:3004/api/v1"

# ── Super Admin credentials (AuthUser model) ──────────────────────────────────
SUPER_ADMIN = {
    "email":    "admin@estate.com",
    "password": "Admin@123",          # ← update if different
}

# ── UI routes ─────────────────────────────────────────────────────────────────
UI = {
    "login":           f"{BASE_UI}/auth/login",
    "dashboard":       f"{BASE_UI}/dashboard",
    "estates":         f"{BASE_UI}/estates",
    "residences":      f"{BASE_UI}/residences",
    "resident_types":  f"{BASE_UI}/resident-types",
    "contacts":        f"{BASE_UI}/contacts",
    "visitors":        f"{BASE_UI}/visitors",
}

# ── API endpoints (matching your Django URL patterns) ─────────────────────────
API = {
    # Super-admin scope
    "login":           f"{BASE_API}/auth/login/",
    "estates":         f"{BASE_API}/auth/estates/",
    "users":           f"{BASE_API}/auth/users/",

    # Estate-tenant scope
    "resident_types":        f"{BASE_API}/resident-types/",
    "residences":            f"{BASE_API}/residences/",
    "contacts":              f"{BASE_API}/contacts/",
    "contact_types":         f"{BASE_API}/contact-types/",
    "person_identifier_types": f"{BASE_API}/person_identifier_types/",
    "notification_prefs":    f"{BASE_API}/notification-preferences/",
    "visitor_types":         f"{BASE_API}/visitor-types/",
    "visitor_schedules":     f"{BASE_API}/visitor-schedules/",
}

# ── Known lookup IDs from your real API ───────────────────────────────────────
# Residence Types (from /api/v1/resident-types/)
RESIDENCE_TYPE_IDS = {
    "Amenity":       1,
    "Business":      2,
    "Gate":          3,
    "Guards":        4,
    "Panic Monitor": 5,
    "Residence":     6,
    "Security":      7,
    "Tennis Court":  8,
}

# Contact Types (from /api/v1/contact-types/)
CONTACT_TYPE_IDS = {
    "Administrator":        27,
    "Communication":        28,
    "Do Not Disturb":       29,
    "Domestic":             30,
    "Emergency Contact":    31,
    "Estate Agent":         32,
    "Long Term Contractor": 33,
    "Minor":                34,
    "Owner Landlord":       35,
    "Owner Resident":       36,
    "Remote Only":          37,
    "Tenant":               38,
    "Unknown":              39,
}

# Person Identifier Types (from /api/v1/person_identifier_types/)
PERSON_ID_TYPES = {
    "South African ID Number":           15,
    "Passport":                          16,
    "International Identification Card": 17,
    "Internation Drivers License":       18,
    "Asylum Paper":                      19,
    "Passport MRZ":                      20,
    "System":                            21,
}

# Notification Preferences (from /api/v1/notification-preferences/)
NOTIFICATION_PREFS = {
    "Urgent":     1,
    "Emergency":  2,
    "Bulk":       3,
    "Enter":      4,
    "Exit":       5,
    "Promotions": 6,
}

# Visitor Types (from /api/v1/visitor-types/)
VISITOR_TYPE_IDS = {
    "Contractor":              1,
    "Contracter Staff":        2,
    "Domestic":                3,
    "Shared Service Provider": 4,
    "Visitor":                 5,
}

# VisitStatus choices (from Django model)
VISIT_STATUS = {
    "scheduled":  "scheduled",
    "confirmed":  "confirmed",
    "checked_in": "checked_in",
    "completed":  "completed",
    "cancelled":  "cancelled",
    "no_show":    "no_show",
    "expired":    "expired",
    "active":     "active",
}

# GenderChoices (from Django model)
GENDERS = ["male", "female", "other", "unspecified"]

# Estate status choices
ESTATE_STATUS = ["active", "inactive", "pending"]

# ── Default estate schema for tenant-scoped tests ────────────────────────────
# This schema contains the seeded test data (contact 14 "Avik Sen",
# residence 7 "3-A1", visitor schedule 11 "Addy") used in known-entity tests.
SCHEMA_NAME = "estate_rsh_signature"

# ── Timeouts ──────────────────────────────────────────────────────────────────
TIMEOUT = {
    "default":    12_000,
    "navigation": 20_000,
    "api":         8_000,
}