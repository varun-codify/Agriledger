# 🌾 AgriLedger — Smart Farm Management Platform

A full-stack, AI-powered farm management platform built with **Reflex** (Python) and **MongoDB**. Track cattle, crops, breeding cycles, income/expenses, milk & coconut sales, weather, and get AI-driven recommendations — all from one dashboard.

> **Zero-cost by default:** Email (Resend), SMS/WhatsApp (Twilio) and AI (OpenAI) integrations are stubbed or replaced with free alternatives (WhatsApp click-to-chat links, Google Gemini) so the app runs without paid API keys.

---

## ✨ Features

- **Dashboard** — KPI cards, 7 charts (expense pie, profit/loss, milk/fat/SNF trends, coconut sales, breeding alerts), weather card, smart reminders — all computed from real farm data.
- **Animal Management** — 7 species (cows, buffaloes, sheep, goats, hens, cocks, chicks), individual profiles, milk history, vaccinations, health notes, feed records, per-animal profitability.
- **Crop Management** — crop profiles with planting activities, harvests, expense breakdown, and profitability.
- **Breeding Cycles** — full reproductive tracking (hormone → insemination → pregnancy → calving), auto-calculated calving dates (cow vs buffalo gestation), calf records, follow-up checks.
- **Transactions** — 6-step wizard, keypad entry, quick-add, extended categories (milk sales with fat %/SNF %, coconut sales with auto-total).
- **AI Insights & Assistant** — conversational chatbot over your farm data (Google Gemini, with rule-based fallback), farm health score, recommendations, seasonal tips.
- **Reports & Export** — financial summaries, PDF (reportlab) and Excel (openpyxl) export, date-range filtering.
- **AG Grid Tables** — sortable/filterable tables for transactions, cattle, and breeding with CSV/Excel export.
- **Weather** — live Open-Meteo forecast (no API key) with farming suggestions and alerts.
- **Family & Farm Settings** — rename your farm (shown in the app header) and add family members who log in with their own account and share the same farm data. Invitations auto-join on sign-up.
- **i18n** — English, Tamil (தமிழ்), Hindi (हिन्दी). **Theme** — dark/light toggle. **PWA** — offline-capable manifest.

---

## 🚀 Getting Started

### Prerequisites

- Python 3.11+
- MongoDB (local `mongodb://localhost:27017` or MongoDB Atlas)

### Installation

```bash
# 1. Create a virtual environment
python -m venv .venv
source .venv/bin/activate        # Windows: .venv\Scripts\activate

# 2. Install dependencies
pip install -r requirements.txt

# 3. Configure environment (optional — sensible defaults exist)
cp .env.example .env
```

### Environment Variables

| Variable | Default | Purpose |
|---|---|---|
| `MONGODB_URI` | `mongodb://localhost:27017/agriledger_db` | MongoDB connection string |
| `MONGODB_DATABASE` | `agriledger` | Database name |
| `SECRET_KEY` | dev fallback | Signs auth tokens (required in production) |
| `GEMINI_API_KEY` | — | Enables the AI assistant (optional; rule-based fallback otherwise) |
| `APP_ENV` | `development` | `production` fails fast on missing required vars |
| `CORS_ORIGINS` | `http://localhost:3000,http://localhost:8000` | Allowed origins for the FastAPI layer |
| `RATE_LIMIT_MAX_REQUESTS` / `RATE_LIMIT_WINDOW_SECONDS` | `60` / `60` | API rate limiting |
| `TOKEN_EXPIRY_SECONDS` | `86400` | Auth token lifetime |

### Run the app

```bash
# Optimized run (fast DNS, DB caching, automated index creation)
python run.py

# Or directly with reflex
reflex run

# Production mode — compiled frontend bundle
reflex run --env prod
```

The FastAPI REST API (`/api/*`, `/users/*`, `/auth/token`, `/health`) is mounted
inside the Reflex server via `api_transformer`, serving both the UI and REST API on port 3000.
Interactive API docs: `http://localhost:3000/api/docs`.



---

## 🚀 Free Deployment (MongoDB Atlas + Reflex Cloud)

The app is fully deployable **for free** using MongoDB Atlas (database) and
Reflex Cloud (hosting). Reflex's backend uses WebSockets, so it cannot run on
Vercel's stateless serverless functions — Reflex Cloud is the supported host.

### 1. Create a free MongoDB Atlas database

1. Go to https://www.mongodb.com/cloud/atlas/register and create a free account.
2. Click **Build a Database** → choose the **M0 (free)** tier → a cloud provider
   and region (e.g. AWS / ap-south-1) → **Create**. It takes ~2 minutes.
3. Under **Database Access**, add a database user and set a strong password
   (remember both).
4. Under **Network Access**, click **Add IP Address** → **Allow access from
   anywhere** (`0.0.0.0/0`) → Confirm.
5. Click **Connect** → **Drivers** → copy the connection string. It looks like:
   `mongodb+srv://<dbuser>:<password>@cluster0.xxxxx.mongodb.net/` — replace
   `<dbuser>` and `<password>` with the credentials from step 3 and append the
   database name: `mongodb+srv://<dbuser>:<password>@cluster0.xxxxx.mongodb.net/agriledger?retryWrites=true&w=majority`
6. Put it in your local `.env` file:
   `MONGODB_URI=mongodb+srv://<dbuser>:<password>@cluster0.xxxxx.mongodb.net/agriledger?retryWrites=true&w=majority`

### 2. Deploy to Reflex Cloud (free)

```bash
pip install -r requirements.txt
reflex login          # create a free Reflex account when prompted
reflex deploy --env MONGODB_URI="<your atlas uri>" --env SECRET_KEY="<a long random string>"
```

Follow the prompts (pick a region close to you). When it finishes it prints
your live URL. Optional env vars: `GEMINI_API_KEY` (AI + bill-scanning),
`GEMINI_MODEL`.

> On the free plan the app may sleep after inactivity and take a few seconds to
> wake on the first request — that's normal.

---

## 🏗️ Architecture

```
app/
├── app.py               # Entry point — page routes, on_load hooks, API mount
├── api.py               # FastAPI REST API (mounted into the Reflex server)
├── config.py            # Centralized, validated configuration
├── security.py          # bcrypt hashing + HMAC-signed bearer tokens
├── components/          # UI building blocks (pages & widgets)
│   ├── dashboard.py     # Charts, KPI cards, weather, reminders
│   ├── cattle/ crops/ breeding/ transactions/ insights/ reports/ settings/
│   └── landing.py layout.py
├── states/              # Reflex state classes (data + logic per module)
├── database/
│   ├── models.py        # TypedDict schemas for all collections
│   ├── connection.py    # Shared async Motor client
│   ├── crud.py          # Async CRUD + seed helpers
│   └── indexes.py       # MongoDB index creation
├── services/            # email (stub), sms/WhatsApp (links), scheduler (alerts)
└── middleware/          # In-memory rate limiter
```

**Data flow:** Reflex states → `crud.py` (async Motor) → MongoDB. The FastAPI layer shares the same `connection.get_db()` client. Page loads fetch all data in parallel via `app_data_state.py` (`asyncio.gather`) instead of one DB round-trip per widget.

---

## 🧪 Testing

```bash
python -m pytest tests/ -q
```

The suite covers password hashing, config, models, i18n translations, service stubs, and state logic (transaction keypad, theme/language toggles, notifications, reports).

---

## 🔐 Security Notes

- Passwords hashed with **bcrypt** (never stored in plaintext).
- UI sessions are signed, HttpOnly cookies — they survive server restarts, and the user's password hash is never serialized to the browser.
- REST API tokens are HMAC-SHA256 signed and expire (`SECRET_KEY` required in production).
- Login lockout after 5 failed attempts (15-minute window).
- Rate limiting middleware on the API (Reflex infra paths like `/_event` and `/_static` are exempt); CORS restricted to explicit origins.
- Security headers (`X-Content-Type-Options`, `X-Frame-Options`, `Referrer-Policy`) on API responses.
- Roles are assigned server-side (`viewer` on registration) — clients cannot self-promote.
