# Number Inventory Service — Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Construiește un API REST complet pentru gestionarea numerelor de telefon, cu state machine și optimistic locking, stocare in-memory.

**Architecture:** Serviciu FastAPI cu stocare în dicționar Python. Modelele sunt definite cu Pydantic v2. Tranzițiile de stare sunt validate prin `ALLOWED_TRANSITIONS`, iar concurența e controlată prin câmpul `version` (optimistic locking). Fără Kafka deocamdată — serviciul funcționează complet over REST.

**Tech Stack:** Python 3.14, FastAPI 0.140, Pydantic v2.13, pytest, httpx

---

## File Map

| Fișier | Responsabilitate |
|--------|-----------------|
| `requirements.txt` | Dependențe proiect (adăugăm pytest + httpx) |
| `app/models.py` | `PhoneStatus` enum, `PhoneNumberCreate`, `PhoneNumber`, `StatusUpdate` |
| `app/storage.py` | Dict in-memory + contor ID + funcție reset() pentru teste |
| `app/main.py` | Instanță FastAPI, include router, `GET /health` |
| `app/routers/numbers.py` | Toate endpoint-urile `/numbers`, state machine, optimistic locking |
| `tests/__init__.py` | Marchează folderul ca pachet Python |
| `tests/test_models.py` | Validare modele Pydantic |
| `tests/test_health.py` | Test endpoint `/health` |
| `tests/test_numbers.py` | Teste pentru toate endpoint-urile `/numbers` |

---

## Task 1: Actualizează requirements.txt și instalează dependențele

**Files:**
- Modify: `requirements.txt`

- [ ] **Step 1: Adaugă pytest și httpx în requirements.txt**

```
fastapi
uvicorn[standard]
pydantic
pytest
httpx
```

- [ ] **Step 2: Instalează noile dependențe**

Rulează:
```bash
cd number-inventory-service
source venv/bin/activate
pip install -r requirements.txt
```

Expected: `Successfully installed httpx-... pytest-...`

- [ ] **Step 3: Verifică instalarea**

```bash
python -m pytest --version
```

Expected: `pytest 8.x.x`

---

## Task 2: Modele Pydantic (models.py)

**Files:**
- Create: `app/models.py`
- Create: `tests/__init__.py`
- Create: `tests/test_models.py`

- [ ] **Step 1: Scrie testele pentru modele (TDD — testele merg ÎNAINTE de cod)**

Creează `tests/__init__.py` (fișier gol):
```python
```

Creează `tests/test_models.py`:
```python
import pytest
from pydantic import ValidationError
from app.models import PhoneNumber, PhoneNumberCreate, PhoneStatus


def test_phone_status_are_stringuri():
    assert PhoneStatus.AVAILABLE == "AVAILABLE"
    assert PhoneStatus.RESERVED == "RESERVED"
    assert PhoneStatus.ACTIVE == "ACTIVE"
    assert PhoneStatus.RELEASED == "RELEASED"


def test_phone_number_create_necesita_campuri():
    with pytest.raises(ValidationError):
        PhoneNumberCreate()  # type: ignore


def test_phone_number_are_valori_implicite_corecte():
    n = PhoneNumber(id=1, e164="+14155550101", country_code="US", current_carrier="Verizon")
    assert n.status == PhoneStatus.AVAILABLE
    assert n.version == 1
    assert n.customer_id is None
    assert n.signature is None


def test_phone_number_model_copy_actualizeaza_status():
    n = PhoneNumber(id=1, e164="+14155550101", country_code="US", current_carrier="Verizon")
    updated = n.model_copy(update={"status": PhoneStatus.RESERVED, "version": 2})
    assert updated.status == PhoneStatus.RESERVED
    assert updated.version == 2
    assert n.status == PhoneStatus.AVAILABLE  # originalul neschimbat
```

- [ ] **Step 2: Rulează testele — trebuie să eșueze (ImportError)**

```bash
python -m pytest tests/test_models.py -v
```

Expected: `FAILED` cu `ModuleNotFoundError: No module named 'app.models'`

- [ ] **Step 3: Implementează models.py**

```python
from pydantic import BaseModel
from enum import Enum
from typing import Optional


class PhoneStatus(str, Enum):
    AVAILABLE = "AVAILABLE"
    RESERVED = "RESERVED"
    ACTIVE = "ACTIVE"
    RELEASED = "RELEASED"


class PhoneNumberCreate(BaseModel):
    e164: str
    country_code: str
    current_carrier: str


class PhoneNumber(BaseModel):
    id: int
    e164: str
    country_code: str
    status: PhoneStatus = PhoneStatus.AVAILABLE
    customer_id: Optional[int] = None
    current_carrier: str
    signature: Optional[str] = None
    version: int = 1


class StatusUpdate(BaseModel):
    new_status: PhoneStatus
    version: int
```

- [ ] **Step 4: Rulează testele — trebuie să treacă**

```bash
python -m pytest tests/test_models.py -v
```

Expected: `4 passed`

- [ ] **Step 5: Commit**

```bash
git add app/models.py tests/__init__.py tests/test_models.py requirements.txt
git commit -m "feat: add Pydantic models and PhoneStatus enum"
```

---

## Task 3: Storage in-memory (storage.py)

**Files:**
- Create: `app/storage.py`

Notă: storage.py nu are teste proprii — e testat indirect prin endpoint-urile din Task 4-6. Funcția `reset()` este un helper de test care va fi apelată în fixture.

- [ ] **Step 1: Implementează storage.py**

```python
from typing import Dict
from app.models import PhoneNumber

db: Dict[str, PhoneNumber] = {}
_next_id: int = 1


def get_next_id() -> int:
    global _next_id
    current = _next_id
    _next_id += 1
    return current


def reset() -> None:
    global _next_id
    db.clear()
    _next_id = 1
```

- [ ] **Step 2: Verifică că importul funcționează**

```bash
python -c "from app import storage; print(storage.db, storage.get_next_id(), storage.get_next_id())"
```

Expected: `{} 1 2`

- [ ] **Step 3: Commit**

```bash
git add app/storage.py
git commit -m "feat: add in-memory storage with optimistic lock counter"
```

---

## Task 4: App entry point și GET /health (main.py)

**Files:**
- Create: `app/main.py`
- Create: `tests/test_health.py`

- [ ] **Step 1: Scrie testul pentru /health**

Creează `tests/test_health.py`:
```python
from fastapi.testclient import TestClient
from app.main import app

client = TestClient(app)


def test_health_returneaza_ok():
    response = client.get("/health")
    assert response.status_code == 200
    assert response.json() == {"status": "ok"}
```

- [ ] **Step 2: Rulează testul — trebuie să eșueze**

```bash
python -m pytest tests/test_health.py -v
```

Expected: `FAILED` cu `ModuleNotFoundError: No module named 'app.main'`

- [ ] **Step 3: Implementează main.py**

```python
from fastapi import FastAPI
from app.routers import numbers

app = FastAPI(title="Number Inventory Service", version="0.1.0")
app.include_router(numbers.router, prefix="/numbers", tags=["numbers"])


@app.get("/health")
def health_check():
    return {"status": "ok"}
```

- [ ] **Step 4: Creează routers/numbers.py cu un router gol (altfel main.py nu pornește)**

```python
from fastapi import APIRouter

router = APIRouter()
```

- [ ] **Step 5: Rulează testul — trebuie să treacă**

```bash
python -m pytest tests/test_health.py -v
```

Expected: `1 passed`

- [ ] **Step 6: Commit**

```bash
git add app/main.py app/routers/numbers.py tests/test_health.py
git commit -m "feat: add FastAPI app entry point with /health endpoint"
```

---

## Task 5: POST /numbers

**Files:**
- Modify: `app/routers/numbers.py`
- Create: `tests/test_numbers.py`

- [ ] **Step 1: Scrie testele pentru POST /numbers**

Creează `tests/test_numbers.py`:
```python
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
```

- [ ] **Step 2: Rulează testele — trebuie să eșueze**

```bash
python -m pytest tests/test_numbers.py -v
```

Expected: `FAILED` — endpoint-ul nu există încă.

- [ ] **Step 3: Implementează POST /numbers în routers/numbers.py**

```python
from fastapi import APIRouter, HTTPException
from typing import List
from app.models import PhoneNumber, PhoneNumberCreate, PhoneStatus, StatusUpdate
from app import storage

router = APIRouter()


@router.post("/", response_model=PhoneNumber, status_code=201)
def create_number(payload: PhoneNumberCreate):
    if payload.e164 in storage.db:
        raise HTTPException(status_code=409, detail=f"Number {payload.e164} already exists")
    number = PhoneNumber(
        id=storage.get_next_id(),
        e164=payload.e164,
        country_code=payload.country_code,
        current_carrier=payload.current_carrier,
    )
    storage.db[payload.e164] = number
    return number
```

- [ ] **Step 4: Rulează testele — trebuie să treacă**

```bash
python -m pytest tests/test_numbers.py -v
```

Expected: `4 passed`

- [ ] **Step 5: Commit**

```bash
git add app/routers/numbers.py tests/test_numbers.py
git commit -m "feat: add POST /numbers endpoint"
```

---

## Task 6: GET /numbers și GET /numbers/{e164}

**Files:**
- Modify: `app/routers/numbers.py`
- Modify: `tests/test_numbers.py`

- [ ] **Step 1: Adaugă testele pentru GET în tests/test_numbers.py (append la fișierul existent)**

```python
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
```

- [ ] **Step 2: Rulează testele — trebuie să eșueze**

```bash
python -m pytest tests/test_numbers.py -v -k "list or get"
```

Expected: `FAILED` — endpoint-urile GET nu există.

- [ ] **Step 3: Adaugă GET endpoints în routers/numbers.py (după `create_number`)**

```python
@router.get("/", response_model=List[PhoneNumber])
def list_numbers():
    return list(storage.db.values())


@router.get("/{e164}", response_model=PhoneNumber)
def get_number(e164: str):
    number = storage.db.get(e164)
    if not number:
        raise HTTPException(status_code=404, detail=f"Number {e164} not found")
    return number
```

- [ ] **Step 4: Rulează toate testele — trebuie să treacă**

```bash
python -m pytest tests/ -v
```

Expected: `9 passed` (4 models + 1 health + 4 numbers din task 5 + 4 noi)

- [ ] **Step 5: Commit**

```bash
git add app/routers/numbers.py tests/test_numbers.py
git commit -m "feat: add GET /numbers and GET /numbers/{e164} endpoints"
```

---

## Task 7: State Machine + Optimistic Locking (PATCH /numbers/{e164}/status)

Acesta este cel mai important task. Implementăm:
1. `ALLOWED_TRANSITIONS` — dicționar cu tranzițiile legale
2. Verificare versiune (optimistic locking) → HTTP 409 dacă version nu se potrivește
3. Verificare tranziție (state machine) → HTTP 400 dacă tranziția e interzisă

**Files:**
- Modify: `app/routers/numbers.py`
- Modify: `tests/test_numbers.py`

- [ ] **Step 1: Adaugă testele pentru PATCH în tests/test_numbers.py**

```python
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
    # AVAILABLE → ACTIVE este interzis
    response = client.patch(url("+14155550101") + "/status",
                            json={"new_status": "ACTIVE", "version": 1})
    assert response.status_code == 400


def test_released_este_terminal():
    client.post("/numbers/", json=VALID)
    client.patch(url("+14155550101") + "/status", json={"new_status": "RESERVED", "version": 1})
    client.patch(url("+14155550101") + "/status", json={"new_status": "ACTIVE",   "version": 2})
    client.patch(url("+14155550101") + "/status", json={"new_status": "RELEASED", "version": 3})
    # Din RELEASED nu se poate merge nicăieri
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
```

- [ ] **Step 2: Rulează testele PATCH — trebuie să eșueze**

```bash
python -m pytest tests/test_numbers.py -v -k "tranzitie or version or released or reserved or patch or inexistent"
```

Expected: `FAILED` — endpoint-ul PATCH nu există.

- [ ] **Step 3: Implementează PATCH + state machine în routers/numbers.py**

Adaugă `ALLOWED_TRANSITIONS` și endpoint-ul. Fișierul complet:

```python
from fastapi import APIRouter, HTTPException
from typing import List
from app.models import PhoneNumber, PhoneNumberCreate, PhoneStatus, StatusUpdate
from app import storage

router = APIRouter()

ALLOWED_TRANSITIONS = {
    PhoneStatus.AVAILABLE: [PhoneStatus.RESERVED],
    PhoneStatus.RESERVED:  [PhoneStatus.ACTIVE, PhoneStatus.AVAILABLE],
    PhoneStatus.ACTIVE:    [PhoneStatus.RELEASED],
    PhoneStatus.RELEASED:  [],
}


@router.post("/", response_model=PhoneNumber, status_code=201)
def create_number(payload: PhoneNumberCreate):
    if payload.e164 in storage.db:
        raise HTTPException(status_code=409, detail=f"Number {payload.e164} already exists")
    number = PhoneNumber(
        id=storage.get_next_id(),
        e164=payload.e164,
        country_code=payload.country_code,
        current_carrier=payload.current_carrier,
    )
    storage.db[payload.e164] = number
    return number


@router.get("/", response_model=List[PhoneNumber])
def list_numbers():
    return list(storage.db.values())


@router.get("/{e164}", response_model=PhoneNumber)
def get_number(e164: str):
    number = storage.db.get(e164)
    if not number:
        raise HTTPException(status_code=404, detail=f"Number {e164} not found")
    return number


@router.patch("/{e164}/status", response_model=PhoneNumber)
def update_status(e164: str, payload: StatusUpdate):
    number = storage.db.get(e164)
    if not number:
        raise HTTPException(status_code=404, detail=f"Number {e164} not found")

    if number.version != payload.version:
        raise HTTPException(
            status_code=409,
            detail=f"Version conflict: DB has version {number.version}, got {payload.version}"
        )

    if payload.new_status not in ALLOWED_TRANSITIONS[number.status]:
        raise HTTPException(
            status_code=400,
            detail=f"Illegal transition: {number.status} → {payload.new_status}"
        )

    updated = number.model_copy(update={
        "status": payload.new_status,
        "version": number.version + 1,
    })
    storage.db[e164] = updated
    return updated
```

- [ ] **Step 4: Rulează toate testele — trebuie să treacă**

```bash
python -m pytest tests/ -v
```

Expected: `20 passed` (4 models + 1 health + 15 numbers)

- [ ] **Step 5: Commit**

```bash
git add app/routers/numbers.py tests/test_numbers.py
git commit -m "feat: add state machine and optimistic locking via PATCH /numbers/{e164}/status"
```

---

## Task 8: Smoke test manual cu uvicorn

- [ ] **Step 1: Pornește serverul**

```bash
uvicorn app.main:app --reload
```

Expected: `Uvicorn running on http://127.0.0.1:8000`

- [ ] **Step 2: Testează health check**

```bash
curl -s http://127.0.0.1:8000/health | python -m json.tool
```

Expected:
```json
{"status": "ok"}
```

- [ ] **Step 3: Adaugă un număr**

```bash
curl -s -X POST http://127.0.0.1:8000/numbers/ \
  -H "Content-Type: application/json" \
  -d '{"e164": "+14155550101", "country_code": "US", "current_carrier": "Verizon"}' \
  | python -m json.tool
```

Expected: obiect JSON cu `status: "AVAILABLE"`, `version: 1`

- [ ] **Step 4: Schimbă status-ul cu versiunea corectă**

```bash
curl -s -X PATCH "http://127.0.0.1:8000/numbers/%2B14155550101/status" \
  -H "Content-Type: application/json" \
  -d '{"new_status": "RESERVED", "version": 1}' \
  | python -m json.tool
```

Expected: `status: "RESERVED"`, `version: 2`

- [ ] **Step 5: Testează optimistic locking — trimite din nou cu version: 1 (stale)**

```bash
curl -s -X PATCH "http://127.0.0.1:8000/numbers/%2B14155550101/status" \
  -H "Content-Type: application/json" \
  -d '{"new_status": "ACTIVE", "version": 1}' \
  | python -m json.tool
```

Expected: HTTP 409 cu `"Version conflict: DB has version 2, got 1"`

- [ ] **Step 6: Deschide Swagger UI**

Navighează la: `http://127.0.0.1:8000/docs`

Verifică că toate 5 endpoint-urile apar și pot fi testate din browser.

- [ ] **Step 7: Commit final**

```bash
git add .
git commit -m "feat: complete Number Inventory Service REST API"
```

---

## Rezumat endpoint-uri livrate

| Metodă | Path | Status codes |
|--------|------|-------------|
| GET | `/health` | 200 |
| POST | `/numbers/` | 201, 409 |
| GET | `/numbers/` | 200 |
| GET | `/numbers/{e164}` | 200, 404 |
| PATCH | `/numbers/{e164}/status` | 200, 400, 404, 409 |
