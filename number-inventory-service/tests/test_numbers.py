import urllib.parse
import pytest
from fastapi.testclient import TestClient
from app.main import app
from app import storage

client = TestClient(app)


def url(e164: str) -> str:
    """URL-encodează e164 ('+' → '%2B') pentru a fi valid în path."""
    return f"/numbers/{urllib.parse.quote(e164, safe='')}"


@pytest.fixture(autouse=True)
def reset_storage():
    storage.reset()
    yield


VALID = {"e164": "+14155550101", "country_code": "US", "current_carrier": "Verizon"}


# ── POST /numbers ────────────────────────────────────────────

def test_create_number_returneaza_201():
    response = client.post("/numbers/", json=VALID)
    assert response.status_code == 201


def test_create_number_seteaza_valorile_implicite():
    body = client.post("/numbers/", json=VALID).json()
    assert body["status"] == "AVAILABLE"
    assert body["version"] == 1
    assert body["customer_id"] is None
    assert body["id"] == 1
    assert body["e164"] == "+14155550101"


def test_create_numar_duplicat_returneaza_409():
    client.post("/numbers/", json=VALID)
    response = client.post("/numbers/", json=VALID)
    assert response.status_code == 409


def test_id_incrementat_automat():
    r1 = client.post("/numbers/", json=VALID).json()
    r2 = client.post("/numbers/", json={**VALID, "e164": "+14155550102"}).json()
    assert r1["id"] == 1
    assert r2["id"] == 2


# ── GET /numbers ─────────────────────────────────────────────

def test_list_numbers_gol():
    response = client.get("/numbers/")
    assert response.status_code == 200
    assert response.json() == []


def test_list_numbers_returneaza_toate():
    client.post("/numbers/", json=VALID)
    client.post("/numbers/", json={**VALID, "e164": "+14155550102"})
    response = client.get("/numbers/")
    assert len(response.json()) == 2


# ── GET /numbers/{e164} ──────────────────────────────────────

def test_get_number_returneaza_datele_corecte():
    client.post("/numbers/", json=VALID)
    response = client.get(url("+14155550101"))
    assert response.status_code == 200
    assert response.json()["e164"] == "+14155550101"


def test_get_numar_inexistent_returneaza_404():
    response = client.get(url("+99999999999"))
    assert response.status_code == 404


# ── PATCH /numbers/{e164}/status ─────────────────────────────

def test_tranzitie_valida_available_la_reserved():
    client.post("/numbers/", json=VALID)
    response = client.patch(url("+14155550101") + "/status",
                            json={"new_status": "RESERVED", "version": 1})
    assert response.status_code == 200
    body = response.json()
    assert body["status"] == "RESERVED"
    assert body["version"] == 2


def test_conflict_versiune_returneaza_409():
    client.post("/numbers/", json=VALID)
    response = client.patch(url("+14155550101") + "/status",
                            json={"new_status": "RESERVED", "version": 99})
    assert response.status_code == 409


def test_tranzitie_ilegala_returneaza_400():
    client.post("/numbers/", json=VALID)
    response = client.patch(url("+14155550101") + "/status",
                            json={"new_status": "ACTIVE", "version": 1})
    assert response.status_code == 400


def test_released_este_terminal():
    client.post("/numbers/", json=VALID)
    client.patch(url("+14155550101") + "/status", json={"new_status": "RESERVED", "version": 1})
    client.patch(url("+14155550101") + "/status", json={"new_status": "ACTIVE",   "version": 2})
    client.patch(url("+14155550101") + "/status", json={"new_status": "RELEASED", "version": 3})
    response = client.patch(url("+14155550101") + "/status",
                            json={"new_status": "AVAILABLE", "version": 4})
    assert response.status_code == 400


def test_version_creste_la_fiecare_update():
    client.post("/numbers/", json=VALID)
    r1 = client.patch(url("+14155550101") + "/status",
                      json={"new_status": "RESERVED", "version": 1})
    assert r1.json()["version"] == 2
    r2 = client.patch(url("+14155550101") + "/status",
                      json={"new_status": "ACTIVE", "version": 2})
    assert r2.json()["version"] == 3


def test_reserved_poate_reveni_la_available():
    client.post("/numbers/", json=VALID)
    client.patch(url("+14155550101") + "/status", json={"new_status": "RESERVED",  "version": 1})
    response = client.patch(url("+14155550101") + "/status",
                            json={"new_status": "AVAILABLE", "version": 2})
    assert response.status_code == 200
    assert response.json()["status"] == "AVAILABLE"


def test_numar_inexistent_patch_returneaza_404():
    response = client.patch(url("+99999999999") + "/status",
                            json={"new_status": "RESERVED", "version": 1})
    assert response.status_code == 404
