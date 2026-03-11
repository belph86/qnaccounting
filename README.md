# qnaccounting

# 🏦 CS Banking Agent — Inteligentný systém na spracovanie bankových transakcií

> Webový server + REST API pre AI agenta, ktorý automaticky páruje bankové transakcie s faktúrami a dokladmi pomocou Česká spořitelna API.

---

## 📋 Obsah

- [Popis projektu](#popis-projektu)
- [Architektúra](#architektúra)
- [Fázy vývoja](#fázy-vývoja)
- [Technológie](#technológie)
- [Rýchly štart](#rýchly-štart)
- [Štruktúra projektu](#štruktúra-projektu)
- [API pre AI agenta](#api-pre-ai-agenta)
- [Konfigurácia](#konfigurácia)

---

## 📌 Popis projektu

Systém slúži na automatizované spracovanie bankových transakcií z **Česká spořitelna** (cez Erste Developer Portal API). Hlavnou úlohou je umožniť AI agentovi:

1. **Stiahnutie transakcií** z bankového účtu v reálnom čase
2. **Párovanie faktúr** s transakciami podľa VS (variabilný symbol), SS (špecifický symbol), sumy a dátumu
3. **Zadávanie platobných príkazov** priamo z aplikácie
4. **Označovanie transakcií** — agent vie zaznačiť, či transakcia má priradený doklad / faktúru
5. **Dashboard** — prehľad nepárovaných transakcií, stav faktúr, história

Systém je navrhnutý ako **API-first** — primárnym konzumentom je AI agent (napr. Claude, GPT s tool-use), no súčasťou je aj webový dashboard pre ľudskú kontrolu.

---

## 🏗️ Architektúra

```
┌─────────────────────────────────────────────────────────┐
│                     AI Agent (Claude / GPT)              │
│              (tool-use cez HTTP REST API)                 │
└──────────────────────┬──────────────────────────────────┘
                       │  REST API volania
                       ▼
┌─────────────────────────────────────────────────────────┐
│              CS Banking Agent — API Server               │
│                    (ASP.NET Core 8)                      │
│                                                          │
│  ┌─────────────────┐    ┌────────────────────────────┐  │
│  │  Agent API      │    │  Web Dashboard (Blazor /   │  │
│  │  /api/agent/*   │    │  React frontend)            │  │
│  └────────┬────────┘    └────────────────────────────┘  │
│           │                                              │
│  ┌────────▼────────────────────────────────────────┐    │
│  │              Business Logic Layer                │    │
│  │  - TransactionService                            │    │
│  │  - MatchingService (párovanie VS/SS/suma)        │    │
│  │  - PaymentService                                │    │
│  │  - DocumentService                               │    │
│  └────────┬────────────────────────────────────────┘    │
│           │                                              │
│  ┌────────▼──────────┐    ┌────────────────────────┐    │
│  │  Erste/ČS API     │    │   Lokálna DB            │    │
│  │  Client (OAuth2)  │    │   (SQLite / PostgreSQL) │    │
│  └───────────────────┘    └────────────────────────┘    │
└─────────────────────────────────────────────────────────┘
                       │
                       ▼
┌─────────────────────────────────────────────────────────┐
│           Česká spořitelna / Erste API                   │
│   Accounts API  |  Payments API  |  OAuth2              │
└─────────────────────────────────────────────────────────┘
```

---

## 🚀 Fázy vývoja

### Fáza 1 — Základ & autentifikácia *(Core foundation)*
**Cieľ:** Funkčné pripojenie na ČS API, uloženie tokenov, sandbox prostredie

- [ ] Inicializácia projektu (ASP.NET Core 8, EF Core, SQLite)
- [ ] OAuth 2.0 flow s Erste Developer Portal (authorization code grant)
- [ ] Bezpečné uloženie a automatická obnova access/refresh tokenov
- [ ] `GET /api/accounts` — zoznam účtov
- [ ] `GET /api/accounts/{id}/transactions` — stiahnutie transakcií
- [ ] Lokálna databáza — tabuľky `Transactions`, `Accounts`, `Tokens`
- [ ] Sandbox testovanie + .env konfigurácia

---

### Fáza 2 — Správa dokladov & párovanie *(Document matching)*
**Cieľ:** Systém na nahrávanie faktúr a ich párovanie s transakciami

- [ ] Tabuľka `Documents` (faktúry, doklady) — upload PDF/obrázok
- [ ] Tabuľka `TransactionDocumentLinks` — M:N prepojenie
- [ ] Manuálne párovanie cez API (`POST /api/match`)
- [ ] Automatické párovanie podľa:
  - Variabilný symbol (VS)
  - Špecifický symbol (SS)
  - Suma + tolerancia ±0.01€
  - Dátum (±3 dni)
- [ ] Stavy transakcií: `Unmatched` | `Matched` | `Ignored` | `ManuallyMatched`
- [ ] `PATCH /api/transactions/{id}/mark` — agent môže označiť transakciu

---

### Fáza 3 — AI Agent API *(Agent interface)*
**Cieľ:** Štruktúrované API endpointy navrhnuté pre tool-use AI agentov

- [ ] OpenAPI / Swagger dokumentácia (tool definitions pre agenta)
- [ ] `GET /api/agent/unmatched` — transakcie bez dokladu
- [ ] `POST /api/agent/match` — spárovanie transakcie s dokladom
- [ ] `POST /api/agent/payments` — zadanie platobného príkazu
- [ ] `GET /api/agent/summary` — štatistiky, prehľad stavu
- [ ] `POST /api/agent/transactions/sync` — manuálny trigger synchronizácie
- [ ] API kľúč autentifikácia pre agenta (Bearer token)
- [ ] Webhook / SSE notifikácie pre nové transakcie

---

### Fáza 4 — Platobné príkazy *(Payments)*
**Cieľ:** Zadávanie platieb cez ČS Payments API

- [ ] `POST /api/payments` — vytvorenie platobného príkazu
- [ ] Podpisovanie/schvaľovanie cez OAuth SCA (Strong Customer Authentication)
- [ ] Stav príkazu: `Draft` | `Pending` | `Sent` | `Rejected`
- [ ] História odoslaných platieb
- [ ] Validácia IBAN, sumy, dátumu splatnosti

---

### Fáza 5 — Dashboard & UX *(Frontend)*
**Cieľ:** Webové rozhranie pre ľudskú kontrolu a monitoring

- [ ] Prehľad transakcií s filtrovaním (dátum, suma, stav párovania)
- [ ] Upload faktúr a drag-and-drop párovanie
- [ ] Zoznam nepárovaných transakcií (červená vlajka)
- [ ] História platieb
- [ ] Notifikácie pri nových nezodpovedaných transakciách
- [ ] Export do CSV/Excel

---

### Fáza 6 — Produkcia & hardening *(Production ready)*
**Cieľ:** Bezpečnosť, spoľahlivosť, monitoring

- [ ] Migrácia z SQLite na PostgreSQL
- [ ] Background job — automatická synchronizácia transakcií (každých N minút)
- [ ] Rate limiting na Agent API
- [ ] Audit log — kto/čo zmenil transakciu
- [ ] Docker + docker-compose
- [ ] Health check endpoint `/health`
- [ ] Základný monitoring (Serilog + Seq)

---

## 🛠️ Technológie

| Vrstva | Technológia |
|---|---|
| Backend | Python 3.11+, FastAPI |
| ORM | SQLAlchemy 2.0 (async) |
| Databáza | SQLite (dev) → PostgreSQL (prod) |
| Autentifikácia | OAuth 2.0 (Erste / ČS API) |
| HTTP klient | httpx (async) |
| Dokumentácia API | Swagger / OpenAPI 3.1 (auto-generated) |
| Kontajnerizácia | Docker + docker-compose |
| Šifrovanie | cryptography (Fernet / AES) |

---

## ⚡ Rýchly štart

### Predpoklady

- Python 3.11+
- Účet na [Erste Developer Portal](https://developers.erstegroup.com)
- Registrovaná aplikácia ako **Final API Consumer**

### Inštalácia

```bash
git clone https://github.com/<tvoj-username>/cs-banking-agent
cd cs-banking-agent
cp .env.example .env
# Vyplň CLIENT_ID, CLIENT_SECRET, REDIRECT_URI, TOKEN_ENCRYPTION_KEY v .env
pip install -r requirements.txt
python -m uvicorn src.app.main:app --reload
```

### Autorizácia

Otvor `http://localhost:8000/auth/login` — presmeruje ťa na Erste OAuth consent screen.
Po schválení sa token uloží a aplikácia začne sťahovať transakcie.

### API dokumentácia

Swagger UI: `http://localhost:8000/docs`

---

## 📡 API pre AI agenta

Agentské endpointy sú navrhnuté ako **tool definitions** pre LLM s function calling / tool use.

### Autentifikácia
```
Authorization: Bearer <AGENT_API_KEY>
```

### Kľúčové endpointy

| Metóda | Endpoint | Popis |
|---|---|---|
| `GET` | `/api/agent/unmatched` | Transakcie bez dokladu |
| `GET` | `/api/agent/transactions` | Všetky transakcie (filter: dátum, suma, stav) |
| `POST` | `/api/agent/match` | Spárovanie transakcie s dokladom |
| `PATCH` | `/api/agent/transactions/{id}/mark` | Označenie stavu transakcie |
| `POST` | `/api/agent/payments` | Zadanie platobného príkazu |
| `GET` | `/api/agent/summary` | Súhrnné štatistiky |
| `POST` | `/api/agent/sync` | Manuálna synchronizácia z banky |

### Príklad — označenie transakcie

```json
PATCH /api/agent/transactions/abc123/mark
{
  "status": "Matched",
  "documentId": "faktura-2024-042",
  "note": "Faktúra od dodávateľa X, VS 20240042"
}
```

### Príklad — zadanie platby

```json
POST /api/agent/payments
{
  "iban": "CZ6508000000192000145399",
  "amount": 1500.00,
  "currency": "CZK",
  "variableSymbol": "20240042",
  "message": "Platba faktúra 042/2024",
  "dueDate": "2024-12-31"
}
```

---

## ⚙️ Konfigurácia

`.env.example`:

```env
# Erste / ČS API
ERSTE_CLIENT_ID=your_client_id
ERSTE_CLIENT_SECRET=your_client_secret
ERSTE_REDIRECT_URI=http://localhost:5000/auth/callback
ERSTE_SANDBOX=true

# Databáza
DATABASE_URL=Data Source=banking.db

# Agent API
AGENT_API_KEY=your_secret_agent_key

# Synchronizácia
SYNC_INTERVAL_MINUTES=15
```

---

## 🔐 Bezpečnosť

- Bankové tokeny sú šifrované v databáze (AES-256)
- Agent API kľúč je oddelený od bankových prihlasovacích údajov
- Všetka komunikácia cez HTTPS
- PSD2 SCA flow pre platobné príkazy
- Audit log každej zmeny stavu transakcie

---

## 📁 Štruktúra projektu

```
cs-banking-agent/
├── src/
│   └── app/
│       ├── main.py                  # FastAPI application entry point
│       ├── core/
│       │   ├── config.py            # Settings (pydantic-settings, .env)
│       │   ├── database.py          # SQLAlchemy async engine & session
│       │   └── encryption.py        # Fernet token encryption
│       ├── models/
│       │   ├── account.py           # Account model
│       │   ├── transaction.py       # Transaction model
│       │   └── token.py             # OAuth token model
│       ├── services/
│       │   ├── erste_client.py      # Erste/ČS API HTTP client
│       │   ├── token_service.py     # Token storage & auto-refresh
│       │   └── transaction_service.py  # Sync & local CRUD
│       └── api/
│           └── routes/
│               ├── auth.py          # OAuth login/callback
│               └── accounts.py      # /api/accounts endpoints
│
├── tests/
├── requirements.txt
├── .env.example
├── .gitignore
└── README.md
```

---

## 🤝 Prispievanie

1. Fork repozitára
2. Vytvor feature branch: `git checkout -b feature/nazov-funkcie`
3. Commit: `git commit -m 'feat: popis zmeny'`
4. Push: `git push origin feature/nazov-funkcie`
5. Otvor Pull Request

---

## 📄 Licencia

MIT License
