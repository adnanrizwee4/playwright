# 🏘️ Estate Management — Playwright Test Suite

Complete test suite for a Django REST + Angular estate management system.
Built for backend developers — heavy API testing + UI smoke tests.

---

## 📁 Project Structure

```
estate_tests/
│
├── config.py                    # All URLs, credentials, known IDs
├── conftest.py                  # Fixtures: api client, auth_page, screenshots
├── requirements.txt
├── pytest.ini
│
├── utils/
│   └── api_client.py            # HTTP client wrapping all your endpoints
│
├── fixtures/
│   └── test_data.py             # Data factories matching your Django models
│
├── tests/
│   ├── test_01_auth.py          # Login API + UI (AuthUser, JWT, roles)
│   ├── test_02_estate.py        # Estate CRUD + status + manager assign
│   ├── test_03_residence_type.py# ResidenceType CRUD + 8 seeded types
│   ├── test_04_residence.py     # Residence CRUD + all 30+ fields
│   ├── test_05_contact.py       # Contact CRUD + FK + M2M relationships
│   ├── test_06_visitor_schedule.py # VisitorSchedule + lifecycle + flags
│   └── test_07_lookups.py       # All lookup endpoints (contact-types, etc.)
│
├── screenshots/                 # Auto-saved on failure + on demand
└── reports/                     # HTML test report (after each run)
```

---

## 🚀 Setup

```bash
pip install -r requirements.txt
playwright install chromium
```

Update credentials in `config.py` if needed:
```python
SUPER_ADMIN = {
    "email":    "admin@estate.com",
    "password": "Admin@123",
}
```

---

## ▶️ Running Tests

```bash
# Run everything
pytest

# API tests only (no browser — fastest)
pytest tests/test_07_lookups.py tests/test_03_residence_type.py -v

# Single module
pytest tests/test_06_visitor_schedule.py -v

# Run without browser (headless)
pytest --headless

# Run with visible browser + slow motion
pytest --headed --slowmo=1000

# Stop at first failure
pytest -x

# Show print() output
pytest -s -v

# Parallel (needs pytest-xdist)
pytest -n 4
```

---

## 🗂️ Test Coverage

### test_01_auth.py — Authentication
| Test | Type | What it checks |
|------|------|----------------|
| superadmin login returns token | API | POST /auth/login/ → JWT token |
| wrong password → 401 | API | wrong credentials rejected |
| unknown email → 401 | API | unknown user rejected |
| unauthenticated endpoint blocked | API | JWT middleware active |
| token gives access | API | protected endpoints work |
| superadmin role in users list | API | SUPER_ADMIN role assigned |
| login page loads | UI | email + password fields visible |
| valid login redirects | UI | angular route guard works |
| wrong password shows error | UI | error message or stays on login |
| JWT in localStorage | UI | token persisted after login |
| protected route redirects | UI | /residences → /login without auth |

### test_02_estate.py — Estate (Super Admin)
| Test | Type | What it checks |
|------|------|----------------|
| list estates | API | GET /auth/estates/ |
| get estate by id | API | id, name, schema_name, managers[] |
| create estate | API | POST with name, address, city, status |
| estate statuses (active/inactive/pending) | API | parametrized × 3 |
| missing name → 400 | API | validation |
| edit estate (city, status) | API | PATCH |
| delete estate + confirm gone | API | 404 after delete |
| managers[] in response | API | UserRole relationship |

### test_03_residence_type.py — ResidenceType
| Test | Type | What it checks |
|------|------|----------------|
| list returns 8+ types | API | all seeded types |
| all 8 seeded types present | API | Amenity, Business, Gate, etc. |
| each type by ID (parametrized × 8) | API | exact ID match |
| required fields | API | id, name, is_active, is_deleted |
| create type | API | POST + is_active=True default |
| missing name → 400 | API | validation |
| edit type | API | PATCH name + description |
| delete type | API | 404 or is_deleted=True |

### test_04_residence.py — Residence (30+ fields)
| Test | Type | What it checks |
|------|------|----------------|
| get known residence (id=7) | API | All fields from real API response |
| create full payload | API | All 30+ fields saved |
| residence_type_name in response | API | FK → human name |
| different residence types (× 3) | API | FK works for all types |
| capacity fields | API | max_adults, max_minors, parking |
| GPS fields (lat/lng as text) | API | TextField storage |
| member_count = 0 on creation | API | computed read-only field |
| is_active=True, is_deleted=False | API | soft-delete pattern |
| PATCH single field | API | partial update |
| delete + confirm gone | API | soft or hard delete |
| missing name → 400 | API | validation |

### test_05_contact.py — Contact (FK + M2M)
| Test | Type | What it checks |
|------|------|----------------|
| get known contact (id=14, Avik Sen) | API | All fields from real response |
| create full Contact payload | API | All fields saved |
| contact_type_name in response | API | FK → name |
| person_identifier_type_name | API | FK → name |
| notification_preference M2M | API | multiple prefs saved |
| linked_residence M2M | API | multiple residences linked |
| gender choices (× 4) | API | male/female/other/unspecified |
| supervisor flag | API | boolean field |
| member_count 0→1 | API | residence count updated |
| edit contact | API | PATCH nickname, email_notifications |
| delete contact | API | gone or soft-deleted |
| contact types (× 5 parametrized) | API | Owner, Tenant, Emergency, etc. |

### test_06_visitor_schedule.py — VisitorSchedule (most complex)
| Test | Type | What it checks |
|------|------|----------------|
| get known schedule (id=11, Addy) | API | All fields from real response |
| create full VisitorSchedule | API | All fields saved |
| visitor_guid auto-generated | API | UUID editable=False |
| weekday flags Mon-Fri | API | days_selection + 7 booleans |
| weekend-only schedule | API | sat+sun=True |
| all 8 VisitStatus values (parametrized) | API | scheduled/confirmed/etc |
| full lifecycle scheduled→completed | API | status transitions |
| cancelled status | API | terminal state |
| undesired flag | API | boolean |
| blocked flag | API | boolean |
| shared flag | API | boolean |
| external_id + tmt_external_id | API | 3rd party integration fields |
| all 5 visitor types (parametrized) | API | Contractor, Domestic, etc. |
| delete schedule | API | soft or hard delete |

### test_07_lookups.py — Lookup Endpoints
All 4 lookup endpoints verified with exact seeded IDs.

---

## 🔧 How to Adapt to Your UI

Since this is an Angular app, locators may need tuning.
Open browser dev tools and inspect the actual HTML, then update selectors.

Common Angular patterns:
```python
# Angular reactive form inputs
page.locator("input[formcontrolname='email']")

# Angular Material select dropdowns
page.locator("mat-select[formcontrolname='status']").click()
page.locator("mat-option:has-text('Active')").click()

# Angular Material buttons
page.locator("button[mat-raised-button]:has-text('Save')")
```

---

## 🔜 Next Steps

1. Add `VisitorScheduledLog` tests (check-in/check-out logs)
2. Add role-based access tests (ESTATE_MANAGER vs SUPER_ADMIN)
3. Add pagination tests for large datasets
4. Add file/photo upload tests (Contact.photo, facial_image)
5. Add CI/CD pipeline (GitHub Actions)
6. Add `pytest-xdist` for parallel test runs
