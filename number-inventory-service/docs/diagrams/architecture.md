# Number Inventory Service — Arhitectura componentelor

Arată cum sunt legate fișierele proiectului și cum ajunge un request HTTP de la client până la stocare.

```mermaid
flowchart TB
    Client(["🖥️ Tu (curl / Postman / browser)"])

    subgraph Calculator["💻 Calculatorul tău — procesul Python"]
        UV["uvicorn\n(serverul web)"]

        subgraph App["app/"]
            MAIN["main.py\n• creează app FastAPI\n• înregistrează router\n• GET /health"]
            ROUTER["routers/numbers.py\n• POST /numbers/\n• GET /numbers/\n• GET /numbers/{e164}\n• PATCH /{e164}/status\n• state machine\n• optimistic locking"]
            MODELS["models.py\n• PhoneStatus (enum)\n• PhoneNumberCreate\n• PhoneNumber\n• StatusUpdate"]
            STORAGE["storage.py\n• db = {} (dicționar)\n• get_next_id()\n• reset()"]
        end
    end

    Client -->|"HTTP request\n(port 8000)"| UV
    UV -->|"rutează request-ul"| MAIN
    MAIN -->|"prefix /numbers"| ROUTER
    ROUTER -->|"validare input/output"| MODELS
    ROUTER -->|"citire / scriere"| STORAGE
    UV -->|"HTTP response\n(JSON)"| Client

    style Calculator fill:#F0F4FF,stroke:#6B7FD4,stroke-width:2px
    style App fill:#E8EEFF,stroke:#8B9FE8,stroke-width:1px
    style UV fill:#DBEAFE,stroke:#3B82F6,color:#1D4ED8
    style MAIN fill:#EDE9FE,stroke:#7C3AED,color:#4C1D95
    style ROUTER fill:#D1FAE5,stroke:#059669,color:#065F46
    style MODELS fill:#FEF3C7,stroke:#D97706,color:#78350F
    style STORAGE fill:#FFE4E6,stroke:#E11D48,color:#881337
    style Client fill:#F0FDF4,stroke:#16A34A,color:#14532D
```

## Legendă

| Componentă | Fișier | Responsabilitate |
|---|---|---|
| uvicorn | — (server extern) | Ascultă pe portul 8000, primește conexiuni TCP |
| main.py | `app/main.py` | Punctul de intrare, înregistrează router-ul |
| Router | `app/routers/numbers.py` | Logica de business, state machine, locking |
| Models | `app/models.py` | Validare automată date (Pydantic) |
| Storage | `app/storage.py` | Dicționar Python ca bază de date temporară |
```