# 📋 THE EXACT PROMPT — Copy everything below the line into your AI

Copy everything between the `---` lines below and paste it into the AI of your choice. It is a single self-contained build prompt that recreates **AgriLedger** feature-for-feature and detail-for-detail, including data models, seed data, validation rules, calculations, exact UI copy, exact toast/error messages, routing, PWA setup, i18n, and the FastAPI layer.

---

**Build a full-stack farm management web application called "AgriLedger" exactly as specified below. Reproduce every feature, every page, every validation rule, every formula, every UI string, and every small detail. Do not skip or simplify anything. Follow the specification precisely.**

## 0. Tech Stack (exact versions)

- **Reflex 0.8.17** (Python web framework) with the Tailwind V3 plugin (`rx.Config(app_name="app", plugins=[rx.plugins.TailwindV3Plugin()])` in `rxconfig.py`).
- **MongoDB** accessed through **Motor 3.7.1** (async `AsyncIOMotorClient`), database name default `agriledger`.
- **FastAPI 0.128.0** + **uvicorn 0.40.0** for the optional REST API layer.
- **reflex-ag-grid 0.0.11** for data tables (AG Grid, theme `ag-theme-alpine`).
- **reportlab 4.5.1** (PDF reports), **openpyxl 3.1.5** (Excel reports).
- **google-genai 2.17.0** (Gemini AI), **bcrypt 4.3.0**, **pydantic 2.12.5**, **python-dotenv 0.21.1**, **httpx 0.28.1**, **pytest 8.3.5**.
- Python 3.11+.

## 1. Design System

- Font: **Lato** (weights 400 and 700) loaded from Google Fonts; every page root uses `font-['Lato']`.
- Palette: warm cream background (`bg-cream-100`), `stone` neutrals (stone-50/100/200/400/500/600/700/800), **emerald** primary accent (`#10b981`, emerald-500 buttons, hover emerald-600).
- Standard card style used everywhere: `bg-white p-5 rounded-2xl shadow-sm border border-stone-100` (or p-6/p-8 variants).
- Standard primary button: `bg-emerald-500 text-white ... rounded-lg font-semibold hover:bg-emerald-600`.
- Standard error banner (used in every form): a flex row with a `triangle-alert` icon (`h-4 w-4 mr-2 flex-shrink-0`), red-600 text, `bg-red-50 border border-red-200 p-3 rounded-lg`.
- Root app theme: `rx.theme(appearance="light", props={"Button": {"radius": "medium"}, "TextField": {"radius": "medium"}})`.
- Charts use `rx.recharts` (line, bar, pie, area). Chart tooltips: `rx.recharts.graphing_tooltip(cursor={"fill": "rgba(231, 229, 228, 0.4)"})`; grids use `vertical=False, stroke_dasharray="3 3"`.
- A reusable pill "segmented control" component: container `flex items-center gap-2 bg-white p-1 rounded-xl border border-stone-200`; active button `bg-emerald-500 text-white`, inactive `bg-white text-stone-600 border hover:bg-stone-50`. Takes options as `(value, label, icon)` triples.
- Money always formatted with the Indian Rupee sign (₹) and comma grouping. Milk quality numbers use "%".
- Responsive breakpoints used per page exactly as listed below (sm/md/lg/xl grids).

## 2. Project Architecture (file layout to reproduce)

```
app/
├── app.py               # rx.App entry: routes, on_load hooks, head components
├── api.py               # FastAPI REST API (register/login/user with bearer auth)
├── config.py            # Centralized, validated config (env vars, Gemini model fallbacks)
├── security.py          # bcrypt hashing + HMAC-SHA256 signed bearer tokens
├── components/
│   ├── layout.py        # landing header, sidebar, mobile drawer/bottom nav, dashboard layout
│   ├── common.py        # install_app_button, segmented_control
│   ├── landing.py       # marketing landing page
│   ├── quick_add.py     # floating quick-add button + dialog
│   ├── dashboard.py     # KPI cards, charts, weather, reminders
│   ├── cattle/          # cattle_list, cattle_profile, cattle_table (AG Grid), cattle_profitability
│   ├── breeding/        # breeding_list, breeding_detail, breeding_table (AG Grid)
│   ├── crops/           # crop_list, crop_profile, farm_insights (weather)
│   ├── transactions/    # wizard + 8 step files + transaction_table (AG Grid)
│   ├── feed/            # feed_page, feed_panels, dialogs
│   ├── milk/            # milk_page (society bills + OCR + rate checker)
│   ├── insights/        # insights_hub, ai_insights (chatbot), milk_quality
│   ├── reports/         # reports_page (PDF/Excel export)
│   └── settings/        # settings_page (profile, farm, language, notifications, integrations)
├── states/              # one Reflex State class per module (see below)
├── database/
│   ├── models.py        # TypedDict schemas for every collection
│   ├── connection.py    # shared async Motor client (get_db())
│   ├── crud.py          # async CRUD + per-farm demo seeding
│   └── indexes.py       # MongoDB index creation (call once at startup)
├── services/            # gemini_service, email_service (stub), sms_service (WhatsApp links), scheduler_service
└── middleware/          # rate_limiter.py (in-memory, FastAPI)
assets/                  # manifest.json, sw.js, PWA icons (icon-192/512, icon-maskable-192/512, apple-touch-icon-180)
tests/                   # pytest suite
requirements.txt / requirements-dev.txt / .env.example / README.md / plan.md / rxconfig.py / pyproject.toml
```

**Data flow:** Reflex states → `app/database/crud.py` (async Motor) → MongoDB. The FastAPI layer shares the same `app.database.connection.get_db()` client.

## 3. Environment Variables & Config (`app/config.py`)

Read env vars via `python-dotenv` (`load_dotenv()`). Behavior: when `APP_ENV=production`, missing **required** vars raise a `RuntimeError`; otherwise log a warning.

| Variable | Default | Purpose |
|---|---|---|
| `MONGODB_URI` | `mongodb://localhost:27017/agriledger_db` | MongoDB connection string |
| `MONGODB_DATABASE` | `agriledger` | DB name |
| `SECRET_KEY` | `dev-secret-change-in-production` (prod: required) | Signs auth tokens |
| `GEMINI_API_KEY` | — | Enables Gemini AI/OCR (optional; rule-based fallback) |
| `GEMINI_MODEL` | `gemini-3.1-flash-lite` | AI/OCR model, tried first |
| `APP_ENV` | `development` | `production` fails fast |
| `DEBUG` | `false` | debug flag |
| `TRUST_PROXY` | `false` | whether to trust `X-Forwarded-For` |
| `CORS_ORIGINS` | `http://localhost:3000,http://localhost:8000` | comma-separated allowed origins |
| `RATE_LIMIT_MAX_REQUESTS` | `60` | API rate limit per window |
| `RATE_LIMIT_WINDOW_SECONDS` | `60` | rate limit window |
| `TOKEN_EXPIRY_SECONDS` | `86400` | auth token lifetime |
| `RESEND_FROM_EMAIL` | `noreply@agriledger.com` | stub email from address |

Gemini fallback model order (constant `GEMINI_MODEL_FALLBACKS`): `("gemini-3.5-flash", "gemini-3.1-flash-lite", "gemini-3-flash-preview")`. `GeminiConfig.model_candidates` returns configured model first, then deduplicated fallbacks. `ResendConfig.is_configured` = bool(api_key); `TwilioConfig.is_configured` = sid AND token AND phone all set.

`.env.example` must contain: `MONGODB_URI`, `GEMINI_API_KEY`, `GEMINI_MODEL=gemini-3.1-flash-lite`, commented `RESEND_API_KEY`/`TWILIO_ACCOUNT_SID`/`TWILIO_AUTH_TOKEN`/`TWILIO_PHONE_NUMBER`, `FRONTEND_URL`, `BACKEND_URL`, `SECRET_KEY`.

## 4. Database Models (`app/database/models.py`) — all TypedDicts

Literal types: `ActivityType` (Planting, Fertilizing, Pesticide Application, Irrigation, Weeding, Harvesting, Expense), `CropStatus` (Planted, Growing, Harvested, Fallow), `BreedingCattleType` (cow, buffalo), `CalfSex` (male, female), `BreedingStatus` (pending_confirmation, pregnant, calved, not_pregnant), `CalvingOutcome` (live_birth, stillbirth, aborted), `CattleHealthStatus` (Healthy, Sick, Under Treatment, Vaccinated), `AnimalType` (cow, bull, buffalo, sheep, goat, hen, cock, chick), `TransactionType` (income, expense), `UserRole` (admin, worker, viewer, user), `Severity` (Normal, Attention Needed, Critical), `FeedCategory` (Concentrate, Home Grown), `FeedUnit` (kg, bundles, bags), `TimeOfDay` (Morning, Evening), `PlanCategory` (Calf, Heifer, Pregnant Cow, Lactating Cow, Dry Cow, Bull).

Models (each is a TypedDict):
- **User**: name, email, password, role, farm_id (optional), phone (optional), is_active.
- **ActivityLog**: id, user_email, action, entity_type, entity_id, details, timestamp, ip_address.
- **MilkProduction**: date, liters, notes.
- **VaccinationRecord**: date, vaccine_name, veterinarian, next_due_date, notes.
- **HealthNote**: date, note, severity.
- **FeedRecord**: date, feed_type, quantity_kg, cost, notes.
- **Cattle**: id, name, animal_type, tag_number, age, breed, purchase_date, purchase_price, image_url, health_status, milk_production[], vaccinations[], health_notes[], feed_records[], is_juvenile, parent_id, mother_id, weight, is_active.
- **CropActivity**: id, date, activity_type, notes, cost. **HarvestRecord**: id, date, quantity, unit, income. **Crop**: id, name, field_name, planting_date, status, image_url, activities[], harvests[].
- **Category**: name, icon. **Transaction**: type, category, amount, date, notes.
- **CoconutSale**: id, date, coconut_count, price_per_coconut, total_amount, buyer, notes.
- **MilkSale**: id, date, animal_id, liters, fat_percentage, snf_percentage, clr, water_ratio, rate_per_liter, total_price, buyer, bill_number, payment_status ("pending"|"paid"), paid_date, notes.
- **MilkSocietyRateSlab**: fat_min, rate. **MilkSocietyRate**: farm_id, society, slabs[].
- **FeedType**: id, name, category, unit, cost_per_unit, is_custom, farm_id. **FeedStock**: id, feed_type_id, feed_name, quantity, unit, purchase_date, supplier, cost, expiry_date, farm_id. **FeedConsumption**: id, date, time_of_day, animal_id, animal_name, feed_type_id, feed_name, quantity, unit, notes, farm_id. **PlanFeedItem**: feed_type_id, feed_name, quantity, unit. **FeedingPlan**: id, category, name, morning[], evening[], minerals, water_reminder, farm_id.
- **FollowUpCheck**: date, notes. **BreedingCycle**: id, cattle_id, cattle_name, cattle_type, hormone_injection_date, insemination_date, pregnancy_confirmed, pregnancy_confirmation_date, expected_calving_date, follow_up_checks[], repeat_breeding_indicator, calf_born, calf_sex, calf_health, birth_outcome, notes, status, created_date.

**CRUD layer** (`crud.py`): one `get_all_*`/`create_*`/`update_*` pair per collection (all farm-scoped with `farm_id`), plus `delete_transactions_by_note(farm_id, note_prefix)` (regex `^{prefix}`), `get_milk_rate_table`, `upsert_milk_rate_table` (filters slabs to fat_min>0 & rate>=0, sorts by fat_min, upserts), `get_feed_sync_markers`/`set_feed_sync_marker`, `log_activity`, and `ensure_farm_seed(collection_name, farm_id, seed_data)` which inserts demo rows only when the farm has zero rows in that collection, re-assigning fresh `uuid4()` ids and the real farm_id (never seeds empty/anon farm_ids; must deep-convert Reflex proxies to plain dicts first).

**Indexes** (`indexes.py`, all created in one `create_indexes(db)` async function): `users.email` unique; `cattle.animal_type/health_status/is_active`; `crops.status/planting_date`; `transactions.type/date/category.name`; `coconut_sales.date/buyer`; `milk_sales.date/animal_id/buyer/payment_status`, `milk_rate_tables.society`; `breeding_cycles.cattle_id/status/insemination_date/expected_calving_date`; `feed_types.farm_id`, `feed_stock.farm_id/feed_type_id`, `feed_consumptions.farm_id/date/animal_id`, `feeding_plans.farm_id/category`, `feed_sync_markers.farm_id`; `activity_logs.user_email/timestamp/entity_type`.

## 5. Authentication & Security

**`app/security.py`**: `hash_password` (bcrypt gensalt), `verify_password` (bcrypt checkpw; malformed hash → False), `create_access_token(email)` = base64url(JSON `{"sub": email, "exp": now+expiry}`) + "." + HMAC-SHA256 signature (base64url), `decode_access_token` validates signature (constant-time compare) and expiry.

**`app/states/auth_state.py`**:
- Fields: `current_user` (User or None), `is_logged_in`, `error_message`, `is_loading`.
- **Register** validation (in order, with these exact messages): name required → "Full name is required."; email required → "Email is required."; email must match `[^@]+@[^@]+\.[^@]+` → "Enter a valid email address (e.g., name@example.com)."; password required → "Password is required."; password < 8 chars → "Password must be at least 8 characters long."; confirm required → "Please confirm your password."; mismatch → "Passwords do not match. Please re-enter them."; duplicate email → "User with this email already exists." New users get `role="viewer"`, fresh `farm_id=uuid4()`, `phone=None`, `is_active=True`. On success set `is_logged_in=True`, `current_user`, redirect `/dashboard`. DB failure → "Failed to create account. Please try again."
- **Login**: email required → "Email is required."; password required → "Password is required."; unknown email → "No account found with this email. Please sign up first."; lockout check → "Too many failed attempts. Try again in a few minutes."; wrong password → "Incorrect password. Please try again." **Lockout: 5 failed attempts within 15 minutes (900s)** per email (in-memory dict of timestamps). Success clears failures and redirects `/dashboard`.
- `logout()` → clears state, redirect `/`. `require_login()` → redirects `/login` if not logged in.
- `farm_id` computed var → `current_user["farm_id"]` or email fallback.

**`app/api.py` (FastAPI)**: CORS with `allow_origins=list(config.cors_origins)`, `allow_credentials=True`; in-memory `RateLimitMiddleware(max_requests=config.rate_limit_max_requests, window_seconds=config.rate_limit_window_seconds)` that returns HTTP 429 JSON `{"detail": "Too many requests. Please try again later.", "retry_after": window}` and sets `X-RateLimit-Limit` / `X-RateLimit-Remaining` headers (IP from `X-Forwarded-For` only when `TRUST_PROXY=true`). Endpoints:
- `POST /users/register` — validates email format (422 "Invalid email format."), rejects duplicates (400 "Email already registered."), stores bcrypt-hashed password with role **"viewer"**, fresh farm_id, phone None, is_active True. Returns name/email/role.
- `POST /auth/token` — validates credentials, 401 "Invalid credentials." otherwise; returns `{"access_token", "token_type": "bearer", "email"}`.
- `GET /users/{email}` — bearer auth via `HTTPBearer(auto_error=False)`; 401 "Authentication required." / "Invalid or expired token."; 403 "Not authorized to view this user." unless caller == requested email; 404 "User not found."
- Pydantic models: `UserCreate(name, email, password)`, `UserOut(name, email, role)`, `LoginRequest(email, password)`.

## 6. Routes (register in `app/app.py`)

| Route | Page | on_load |
|---|---|---|
| `/` | landing (index) | — |
| `/login`, `/register` | auth pages | — |
| `/dashboard` | dashboard | require_login, fetch_cattle_list, fetch_transactions, fetch_crops_list, fetch_weather, fetch_breeding_cycles, fetch_feed_data, auto_sync_homegrown_crops |
| `/add-transaction` | transaction wizard | require_login |
| `/cattle` | animal management | require_login, fetch_cattle_list |
| `/cattle/[id]` | cattle profile | require_login, fetch_cattle_list, load_cattle_profile |
| `/cattle/breeding` | breeding list | require_login, fetch_breeding_cycles, fetch_cattle_list |
| `/cattle/breeding/[id]` | breeding detail | require_login, fetch_breeding_cycles, load_breeding_detail |
| `/crops` | crop management | require_login, fetch_crops_list |
| `/crops/[id]` | crop profile | require_login, fetch_crops_list, load_crop_profile |
| `/feed` | feed module | require_login, fetch_feed_data, fetch_cattle_list, fetch_crops_list, auto_sync_homegrown_crops, fetch_transactions |
| `/insights` | insights hub | require_login, fetch_weather, refresh_insights |
| `/milk` | milk & society bills | require_login, fetch_transactions, fetch_cattle_list |
| `/reports` | reports & exports | require_login |
| `/settings` | settings | require_login |
| `/transactions` | transaction tables | require_login, fetch_transactions |

Legacy redirect routes (empty fragment page, `on_load=[require_login, rx.redirect(target)]`): `/analytics`→`/dashboard`, `/transactions-table`→`/transactions`, `/cattle-table`→`/cattle`, `/breeding-table`→`/cattle/breeding`, `/feed/analytics`→`/feed`, `/ai-assistant`→`/insights`.

**`head_components`** (exact): Google Fonts preconnect ×2 + Lato stylesheet; meta viewport `width=device-width, initial-scale=1, viewport-fit=cover`; meta theme-color `#10b981`; link manifest `/manifest.json`; link icon `/icon-192.png`; apple-touch-icon `/apple-touch-icon-180.png`; meta `apple-mobile-web-app-capable=yes`; meta `apple-mobile-web-app-status-bar-style=default`; a script registering `/sw.js` on load (errors swallowed); a script releasing `document.body.style.overflow=''` when the window crosses into ≥768px; a script capturing `beforeinstallprompt` into `window.__agriledgerDeferredPrompt` (preventDefault) and clearing it on `appinstalled`.

## 7. Layout (`app/components/layout.py`)

- **Landing header**: sticky, `bg-white/80 backdrop-blur-md`, border-b stone-200/50, leaf icon + "AgriLedger" wordmark (hidden on mobile), nav links Features/About/Pricing (hidden below md), "Login" link, gradient "Sign Up" button.
- **Sidebar** (`hidden md:flex`, cream bg, border-r): brand row (leaf + AgriLedger, hidden when collapsed); accordion nav groups — **Farm** (Dashboard→/dashboard, Animals→/cattle, Breeding Cycles→/cattle/breeding, Crops→/crops), **Dairy & Sales** (Milk & Bills→/milk, Transactions→/transactions), **Intelligence** (Feed→/feed, Insights & AI→/insights), **System** (Reports→/reports, Settings→/settings) — each group header collapsible (chevron rotates -90° when closed, `UIState.sidebar_groups` toggles); bottom section with emerald "Add Transaction" link (→/add-transaction) and red "Logout" button. Collapsed state (`UIState.sidebar_collapsed`, w-20) shows icon-only rail of all items. Active item styling: emerald text + `bg-emerald-50`; active logic: exact path or path starts with href+"/" (with special case so `/cattle/*` children belong to Animals but `/cattle/breeding*` belongs to Breeding).
- **Dashboard header**: hamburger (mobile, opens drawer), panel-left collapse toggle (desktop), "My Farm" title; right side: compact Install App button, bell icon button, avatar linking to /settings with `src=https://api.dicebear.com/9.x/initials/svg?seed={user name}` and a 2px emerald border. Height h-16, `border-b bg-white`.
- **Mobile drawer** (`md:hidden`): slide-in from left (w-72, max-w-[85vw], translate-x transition 300ms), black/50 backdrop with blur; groups + Add Transaction + install button + Logout; closes on link click; locks body scroll when open. 
- **Mobile bottom nav** (`md:hidden`, fixed bottom, safe-area padding `pb-[env(safe-area-inset-bottom)]`): Home(/dashboard), Animals(/cattle), Milk(/milk), Feed(/feed), More (menu icon → opens drawer).
- **dashboard_layout(content, page_title)**: sidebar + header + main (`flex-1 bg-stone-50`, px-4 pt-4 pb-24 md:px-6 md:pt-6 md:pb-6, h1 page title `text-2xl md:text-3xl font-bold text-stone-800 mb-4 md:mb-6`) + mobile drawer + bottom nav + quick-add dialog; `on_mount=[UIState.close_mobile_nav, UIState.check_install_status]`; root `flex min-h-screen w-full bg-cream-100 font-['Lato']`.

## 8. UI State (`app/states/ui_state.py`) & PWA install

`UIState`: `sidebar_collapsed`, `sidebar_groups` dict (Farm/Dairy & Sales/Intelligence/System all True), `insights_tab` ("weather"|"ai"), `mobile_nav_open`, `install_prompt_available`. Events: `toggle_sidebar`, `toggle_sidebar_group(group)`, `set_insights_tab(tab)`, `toggle_mobile_nav`, `open_mobile_nav` (sets body overflow hidden via `rx.call_script`), `close_mobile_nav` (restores), `set_install_available(bool)`, `check_install_status` (JS promise that resolves true when a deferred `beforeinstallprompt` exists, false if already installed in standalone mode or after 10s timeout — reuses a single shared promise), `install_app` (calls `window.__agriledgerDeferredPrompt.prompt()` and clears it).

`common.py`: `install_app_button(compact=False)` — shows only when `UIState.install_prompt_available`; compact = icon-only emerald download chip; full = full-width emerald "Install App" button. `segmented_control(...)` as described in §1.

## 9. Landing Page (`app/components/landing.py`)

Sections in order: **hero** (gradient background `linear-gradient(180deg, #fef6e8 0%, #f5f5f4 100%)`, badge pill "Smart Farm Management Platform" with sparkles icon, H1 "Modern Financial Tools for the **Modern Farmer**" (gradient emerald text on the span), subtitle paragraph, "Get Started Free" gradient button + "Watch Demo" white bordered button, dashboard preview image `/dashboard-preview.png` with a long descriptive alt, aspect 16/9, shadow-2xl) → **features** (badge + "Everything Your Farm Needs" + 6 cards: Expense Tracking/receipt, Cattle Management/git-fork, Crop Management/sprout, Smart Analytics/bar-chart-3, Detailed Reports/file-text, AI Insights/brain-circuit; cards `group bg-white p-8 rounded-2xl shadow-md border border-stone-100 hover:shadow-xl hover:-translate-y-2`) → **about** ("Built for the Future of Farming", paragraph, 3 stats: "10,000+ Farmers Served", "99.9% Uptime", "24/7 Support") → **pricing** ("Simple, Transparent Pricing"; Hobby Farmer ₹12/month, Pro Farmer ₹29/month with "Most Popular" gradient badge; cards with check-icon feature lists, CTA buttons, popular card has emerald border-2) → **footer** (brand blurb, Quick Links, Legal, "Sign Up Now" button, social icons twitter/facebook/linkedin, copyright `© {host} 2024 AgriLedger. All rights reserved.`). `index()` wraps `landing_header()` + `landing_page()` in `bg-cream-100 font-['Lato']` with smooth scroll.

**Login/Register pages** (`app/app.py`): centered `min-h-screen bg-cream-100`, white card `max-w-md rounded-2xl shadow-lg`, leaf logo linking to `/`, "Welcome Back" / "Create Your Account", form with the standard inputs (email/password; register adds name + confirm password), red error banner using `flag_triangle_right` icon, emerald submit buttons ("Log In" / "Create Account"), and footer links ("Sign up" / "Log in").

## 10. Dashboard (`app/app.py` + `app/components/dashboard.py` + `app/states/dashboard_state.py`)

**Layout order (top to bottom):**
1. Six-KPI grid `grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 xl:grid-cols-6 gap-6` — 5 `summary_card`s: **Total Lambs** (sheep icon, CattleState.total_lambs), **Total Kids** (goat, total_kids), **Coconuts Sold (Month)** (tree-palm, DashboardState.total_coconuts_sold_month), **Avg Fat % (Week)** (activity, `{avg_fat_percentage_week}%`), **Avg SNF % (Week)** (activity, `{avg_snf_percentage_week}%`).
2. `health_score_card()` + `insights_widget()` — grid lg:grid-cols-2.
3. `expense_pie_chart()` (lg:col-span-2), `breeding_alerts_card()` (lg:col-span-2), `coconut_sales_chart()` (lg:col-span-4) — grid lg:grid-cols-6.
4. `fat_percentage_trend_chart()` + `snf_percentage_trend_chart()` — grid lg:grid-cols-2.
5. `milk_trend_line_chart()` (lg:col-span-3) + `recent_transactions_list()` (lg:col-span-3) — grid lg:grid-cols-6.
6. `weather_card()` (lg:col-span-2) + `reminders_card()` (lg:col-span-2) — grid lg:grid-cols-6.
7. **Milk Quality** section: header row with h2 "Milk Quality" + link "Open Milk & Society Bills →" (→/milk), then `quality_score_card()` + `milk_quality_insights()` — grid lg:grid-cols-2.
8. **Feed Intelligence** section: header row "Feed Intelligence" + link "Open Feed Module →" (→/feed), then `feed_overview_cards()`.

**Summary card** component: title + icon row, value (text-2xl bold), change indicator with arrow-up/down-circle icons colored emerald/red (from `change_type`).

**Charts** (all compute from real data, with demo fallbacks when empty):
- `expense_pie_chart`: donut (inner 60, outer 80, padding 5, stroke white width 2) of top-5 expense categories; center overlay shows "Total" + `₹{total_expenses}` by default, or hovered slice value+name (via `on_pie_mouse_enter`/`on_pie_mouse_leave` → `active_pie_slice_name/value`).
- `breeding_alerts_card`: "Breeding Alerts" with two rows — clipboard-check icon, "N Checks Due" (BreedingState.pregnancy_checks_due.length(), subtitle "Confirm pregnancy for due animals.") and siren icon, "N Calvings Expected" (calvings_due_soon.length(), "Animals expecting to give birth soon.").
- `coconut_sales_chart`: dual-axis bar chart "Coconut Sales (Last 6 Months)" — volume bars (#8884d8, left axis), revenue bars (#82ca9d, right axis), radius [4,4,0,0], height 300.
- `fat_percentage_trend_chart` / `snf_percentage_trend_chart`: line charts "Milk Fat % Trend (30 Days)" stroke #8884d8, "Milk SNF % Trend (30 Days)" stroke #82ca9d, y domain `dataMin-0.5` to `dataMax+0.5`, height 250.
- `milk_trend_line_chart`: "Milk Production Trend", blue #3b82f6 line, no dots, height 300.
- `weather_card`: "Weather Today" + weather icon (yellow-500), big temp, condition, tip line.
- `reminders_card`: "Reminders" list of icon + task + due date.
- `recent_transactions_list`: "Recent Transactions"; empty state = receipt-text icon + "No transactions yet."; else last-5 transactions with category icon chip, name, date, signed amount (emerald +, red -).

**DashboardState** (all computed via `async def` rx.vars pulling other states):
- `summary_metrics`: Total Income (trending-up), Total Expenses (trending-down), Net Profit (indian-rupee, up if ≥0), Milk Supplied (Month) "X L", Milk Income (Month), Coconut Sales (Month) count.
- `total_expenses`: real sum, else demo sum. `expense_data`: top-5 expense categories with the fill palette `["#10b981","#f97316","#3b82f6","#f59e0b","#8b5cf6","#06b6d4","#ef4444","#64748b"]`, else demo data (Feed 400, Medicine 300, Labor 300, Utilities 200, Other 278).
- `milk_production_data`: last 7 days by date from milk_sales, else demo Mon–Sun [180,210,200,225,205,230,215].
- `weather_highlight`: from CropState weather_data (temp rounded °C, condition+icon from WEATHER_CODES, tip "Humidity X% · Wind Y km/h"), else demo "28°C / Sunny / sun / Perfect day for harvesting. Low humidity.".
- `reminders`: `SchedulerService.generate_all_alerts(...)`, top 6, icons mapped (breeding_check→clipboard-check, calving_expected→siren, rebreeding→refresh-ccw, vaccination→syringe, vaccination_overdue→syringe, health→stethoscope); empty → single demo reminder "Add farm data to see smart reminders" (bell).
- `total_coconuts_sold_month`, `coconut_revenue_month` (current calendar month), `avg_fat_percentage_week` / `avg_snf_percentage_week` (last 7 days averages, 2 decimals, 0.0 when empty), `coconut_sales_data` (6 month buckets, volume+revenue), `milk_fat_trend_data` / `milk_snf_trend_data` (last 30 days, day labels "%b %d").

**Demo fallback constants** live at module level (demo summary metrics all ₹0/0 L, demo expense, demo milk, demo weather, demo reminders) — used only while no real data exists.

## 11. Animals (cattle)

**State (`app/states/cattle_state.py`)**: fields incl. `cattle_list`, `show_add_cattle_dialog`, `new_cattle_date`, dialog toggles, `profile_active_tab` (default "Overview"), `current_cattle`, `animal_type_filter` ("all"), `view_mode` ("cards"|"table"), `add_cattle_error`, `dialog_error`.
- `fetch_cattle_list`: `ensure_farm_seed("cattle", farm_id, DEMO_CATTLE_DATA)` then `get_all_cattle`.
- `add_cattle(form_data)` validation (exact messages): "Name is required.", "Tag number is required.", "Please select an animal type.", "Age is mandatory.", "Purchase date is mandatory.", "Age cannot be negative.", "Age must be a valid whole number.", "Weight must be a valid number.", "Purchase price must be a valid number." On success: new animal with `health_status="Healthy"`, empty arrays, `image_url=https://api.dicebear.com/9.x/notionists/svg?seed={name}`, is_juvenile from checkbox, parent_id/mother_id from form; toast "Animal added successfully!"; DB failure → "Failed to save animal to database. Please try again."; catch-all → "Something went wrong while saving. Please check your inputs."
- Computed vars: `total_cattle`, `total_milk_today` (records dated today), `cattle_requiring_attention` (Sick or Under Treatment), `total_cows`, `total_buffaloes`, `total_sheep` (non-juvenile), `total_lambs` (juvenile sheep), `total_goats`, `total_kids` (juvenile goats), `total_poultry` (hen+cock+chick), `total_chicks`, `active_animals`, `filtered_cattle` (all / poultry group / single type), `breedable_females` (cow/buffalo, non-juvenile), `cattle_profitability_data` (per animal: total milk, revenue = milk×₹5.0, cost = purchase price, profit, `profit_positive`; strings formatted "₹{x:,.0f}").
- Profile vars: `days_owned`, `total_milk_produced`, `average_daily_milk`, `milk_production_last_30_days` (sorted, "%b %d" labels). Events: `load_cattle_profile` (reads router param `id`), tab setter, dialog togglers (reset `current_dialog_date` to today), `add_milk_entry` (liters required → "Liters is mandatory.", ≤0 → "Liters must be a positive number.", non-numeric → "Liters must be a valid number."; inserts at front; toast "Milk entry added!"), `add_vaccination_record` (vaccine required → "Vaccine name is required."; sets health_status to "Vaccinated" unless Sick; toast "Vaccination record added!"), `add_health_note` (note required → "Note is required."; toast "Health note added!").
- **DEMO_CATTLE_DATA** (7 animals): Lakshmi (cow, Jersey, A001, age 4, ₹1200, Healthy, 30 days of milk 12.5±0.5, 1 FMD vaccination 2023-10-01, 1 health note, weight 550), Ganga (buffalo, Murrah, B002, age 5, ₹1500, Vaccinated, 8.0L today, weight 680), Shaun (sheep, Dorper, S001, age 3, ₹250, weight 80), Lamby (sheep, Dorper, S002, age 0, juvenile, mother_id s1, weight 15), Billy (goat, Boer, G001, age 2, ₹200, weight 70), Cluck (hen, Leghorn, P001, age 1, ₹20, weight 2.5), Pecky (chick, Leghorn, P002, age 0, juvenile, mother_id p1, weight 0.2). All images from dicebear notionists seeded by name. All farm_id "demo-farm".

**List page** (`cattle_list.py`): 6 summary stat cards (Total Animals/git-fork blue, Cows/dog blue, Buffaloes/trophy gray, "Sheep: X / Y lambs"/wheat green, "Goats: X / Y kids"/trophy orange, "Poultry: N"/bird red) in `grid grid-cols-2 md:grid-cols-3 lg:grid-cols-6 gap-6 mb-6`; filter buttons All/Cows/Buffaloes/Sheep/Goats/Poultry (emerald when selected); segmented Cards/Table toggle; "Add New Animal" button. Card view: image (h-32 rounded-t-2xl), name + juvenile badge (Lamb/Kid/Chick, purple-100), type badge (color map: cow blue, bull indigo, buffalo gray, sheep green, goat orange, hen red, cock red-200, chick yellow), `#{tag}` mono chip; card links to `/cattle/{id}` with hover lift. Table view: AG Grid "All Animals (Table View)" columns Name, Tag, Type, Breed, Age, Weight (kg), Health, Purchase Price (₹ formatter), Active; single row selection, pagination 20, autoHeight, animate rows. Add dialog: form grid 2-col with Name, Tag Number, Animal Type select (Cow/Bull/Buffalo/Sheep/Goat/Hen/Cock/Chick), Breed, Age (years), Weight (kg, step 0.1), Purchase Price (step 0.01), Purchase Date (date), "Is Juvenile?" checkbox; Cancel/Add Animal buttons; errors inline.

**Profile page** (`cattle_profile.py`): loading skeleton; header with round avatar, name, `#{tag}`, health status badge (Healthy emerald / Vaccinated blue / Sick red / Under Treatment yellow), "{breed} {type}" line; action buttons: Add Milk Entry, Record Vaccination, Add Health Note, Edit Details (toast "Edit not yet implemented."). Tabs: Overview, Milk History, Health Records, Feed Records (placeholder text "Feed records will be shown here."), Profitability. Overview: 6 metric cards (Age "{age} years", Purchase Price ₹, Purchase Date, Days Owned, Total Milk "X L", Avg. Daily Milk "X L") + milk production line chart (30d, emerald #10b981) + health timeline (vaccinations with syringe/blue dots; health notes with heart-pulse dots colored by severity Critical red / Attention Needed yellow / Normal emerald). Milk History: table Date/Liters/Notes. Health Records tab: same timeline. Profitability tab: per-animal profitability cards (milk, revenue emerald, cost red, profit colored by sign). Dialogs: Add Milk Entry (date, liters, notes), Record Vaccination (vaccine name, date, veterinarian, next due date, notes), Add Health Note (date, severity select Normal/Attention Needed/Critical, note textarea).

## 12. Breeding

**State (`app/states/breeding_state.py`)**: fields incl. `breeding_cycles`, dialog toggles, `pregnancy_confirmation_outcome` ("pregnant"), `pregnancy_confirmation_date`, `current_breeding_cycle`, `selected_filter` ("all"), `view_mode` ("cards"|"table"), `new_breeding_cattle_id`, `new_hormone_date`, `new_insemination_date`, `add_breeding_error`, `calving_error`.
- `pregnancy_check_due_date_str` = insemination + 30 days. `filtered_breeding_cycles` by status. `pregnancy_checks_due` = not confirmed and insemination ≤ 30 days ago. `calvings_due_soon` = pregnant and expected calving ≤ 7 days.
- `fetch_breeding_cycles`: seed `"breeding_cycles"` with DEMO_BREEDING_DATA (bc1: Lakshmi/cow, hormone -40d, insemination -35d, not confirmed, expected calving +245d, notes "First cycle for this year.", status pending_confirmation; bc2: Ganga/buffalo, hormone -120d, insemination -110d, confirmed, confirmation -80d, expected calving +200d, follow-up check 2024-05-01 "Ultrasound check normal.", notes "Second pregnancy.", status pregnant).
- `add_breeding_cycle(form_data)`: "Please select an animal.", "Selected animal not found.", "Insemination date is mandatory.", "Hormone injection date is mandatory.", "Insemination date is invalid.", "Hormone injection date is invalid."; **gestation = 310 days buffalo, else 280 days**; new cycle status pending_confirmation, pregnancy_confirmed False, empty follow-ups, created today; toast "Breeding cycle started successfully!"; failure "Failed to start breeding cycle. Please try again."
- `update_pregnancy_status(cycle_id, confirmed, date)`: sets status "pregnant"/"not_pregnant" + fields; toast **info** "Pregnancy status updated."
- `record_calving(cycle_id, form_data)`: birth outcome required → "Please select a birth outcome."; sets calf_born True, calf_sex/health/birth_outcome/notes, status "calved"; toast "Calving recorded successfully!".
- `add_follow_up_check` appends `{"date", "notes"}`; toast info "Follow-up check added.".
- `CalvingRecordDialogState`: `birth_outcome` default "live_birth"; options (live_birth "Live Birth", stillbirth "Stillbirth", aborted "Aborted").

**List page** (`breeding_list.py`): alerts section with two cards (Pregnancy Checks Due with clipboard-check yellow + subtitle; Calvings Expected with siren red); filter tabs (All, Pending Confirmation, Pregnant, Calved, Not Pregnant); segmented Cards/Table toggle; "New Breeding Cycle" button; cards grid (`md:grid-cols-2 lg:grid-cols-3`) OR AG Grid "All Breeding Cycles (Table View)" (columns Animal, Type, Insemination Date, Status, Pregnancy Confirmed, Confirmation Date, Expected Calving, Calf Born, Calf Sex, Notes; pagination 15). Add dialog: animal select (breedable females), hormone injection date, insemination date, notes; Cancel/Start buttons; error banner; auto-calculated expected calving date shown.

**Detail page** (`breeding_detail.py`): **timeline visual** — Hormone (syringe, complete) → connector → Insemination (atom, complete) → connector → Pregnancy Check (clipboard-check; green if confirmed, blue ring if pending_confirmation, gray otherwise; date shown or "Due by {date}") → connector → Expected Calving (baby; green if calved, blue if pregnant). Actions section: Confirm Pregnancy (blue, only when pending_confirmation), Record Calving (emerald, only when pregnant), Add Follow-up Note (stone, toast "Follow-up notes not implemented yet."). Follow-up Checks list. Confirm Pregnancy dialog (outcome select Pregnant/Not Pregnant, confirmation date, Save Result blue). Calving dialog (Birth Outcome select; when live_birth show Calf Sex Male/Female + Calf Health inputs; Notes textarea; Save Record emerald; error banner). Page shows "Loading breeding cycle details..." when no cycle.

## 13. Transactions

**State (`app/states/transaction_state.py`)** — core fields: `current_step` (1), `transaction_type`, `selected_category`, `amount_str` ("0"), `date` (today), `notes`, `transactions`, `coconut_sales`, `milk_sales`, `coconut_count`, `price_per_coconut`, `liters`, `fat_percentage`, `snf_percentage`, `clr`, `water_ratio`, `rate_per_liter`, `animal_id`, `buyer` ("Aavin"), `bill_number`, `payment_status` ("pending"), `show_quick_add`, `active_table_tab` ("all").

**Categories (exact names + icons)**:
- Expense (16): Cattle Feed/wheat, Medicine/syringe, Vaccination/shield-check, Purchase of Animal/git-fork, Shed/Shelter/home, Machinery/tractor, Ploughing/tractor, Fencing/fence, Irrigation/shower-head, Seeds/sprout, Fertilizers/package, Pesticides/bug, Electricity/zap, Transport/truck, Labor Wages/users, Miscellaneous/ellipsis.
- Income (5): Milk Sale/droplets, Selling Sheep/indian-rupee, Selling Cattle/indian-rupee, Coconut Sales/tree-palm, Other Income/archive.

**Wizard behavior**:
- `wizard_steps` = ["Type","Category","Amount","Date","Notes","Review"] plus "Coconut Details" appended when category == Coconut Sales, "Milk Details" when Milk Sale.
- `next_step` (max 8), `prev_step` (from 7/8 → step 2, else decrement), `go_to_step`.
- `set_transaction_type` sets type then next_step. `set_category` — Coconut Sales → go_to_step(7); Milk Sale → go_to_step(8); else next_step.
- `handle_keypad(key)`: "del" removes last char (min "0"), "." adds only if absent, leading "0" replaced by digit, else append.
- `amount` var = float(amount_str). `coconut_total_amount` = count × price. `milk_total_price` = liters × rate.
- Field setters parse defensively (strings→floats, never crash, min 0); `set_bill_number` truncates to 60 chars; `set_payment_status` accepts only "pending"/"paid".
- `submit_transaction`: toast errors — type/category → "Type and category are required."; coconut: "Coconut count and price must be positive."; milk: "Liters and rate must be positive.", "Fat percentage must be between 0 and 10.", "SNF percentage must be between 6 and 12."; else "Amount must be positive." Creates coconut sale (`id` = `str(now.timestamp())`) + a Transaction with notes `"Sold {n} coconuts"`; or milk sale + Transaction `"Sold {x}L of milk"` (paid_date set when paid); or plain transaction. On success: reset wizard + toast "Transaction added successfully!".
- `reset_wizard` resets everything (buyer back to "Aavin").
- **Quick add** (`toggle_quick_add`, `reset_quick_add_form`, `quick_add_transaction`): uses `quick_add_set_type`/`quick_add_set_category` (never touches wizard step); creates transaction dated today with notes "Quick Add"; toast "Quick transaction added!" / error "Type, category, and amount are required." / "Failed to save transaction."
- `fetch_transactions` loads all three lists for the farm.
- `recent_transactions` = last 5 reversed. `transactions_grid_data` flatten for AG Grid.

**Wizard UI** (`wizard.py`): progress bar (numbered circles, completed = emerald with check icon, labels hidden on mobile, connector lines emerald when passed); card `bg-white p-5 md:p-8 rounded-2xl shadow-sm border border-stone-100 w-full max-w-2xl mx-auto min-h-[400px]`; nav bar (Back disabled on step 1; "Next" disabled unless step 1 has type, step 2 has category, step 3 has amount>0; from step 6 shows "Submit Transaction" emerald); `on_mount=reset_wizard`.

**Steps**:
1. **Type** — two cards (Income/trending-up "Money earned", Expense/trending-down "Money spent"); selected = emerald border/bg + scale-105.
2. **Category** — grid of category buttons with icons.
3. **Amount** — big ₹ display + quick buttons (+100/+500/+1000/−100/−500) + 3×4 keypad (1-9, ".", 0, red delete icon).
4. **Date** — date input.
5. **Notes** — text input/textarea.
6. **Review** — rows: Type, Category (with its icon), Amount (₹), Date, Notes (or "−").
7. **Coconut Details** — number of coconuts, price per coconut, buyer (optional), date, big auto-total "₹{coconut_total_amount}".
8. **Milk Details** — animal select (breedable females), litres, rate/L, fat %, SNF %, CLR (optional), Water Ratio (optional), Milk Society select (DEFAULT_SOCIETIES: Aavin, Hatsun Agro, Heritage, Dodla, Arokya, Private Customer, Other), bill number, payment status, date, big auto-total "₹{milk_total_price}".

**Quick-add dialog** (`quick_add.py`): fixed FAB (bottom-24 right-4 md:bottom-6 md:right-6, emerald, plus icon, scale-105 hover) → modal bottom sheet on mobile / centered on desktop (max-w-sm): Income/Expense toggle, big ₹ amount display, 3×4 keypad, "Category" chips (first 5 of current categories, emerald highlight when selected), "Add Transaction" button.

**Transactions page** (`transaction_table.py`): segmented tabs All Transactions/Milk Sales/Coconut Sales + "Add Transaction" link; AG Grids:
- All: Date (agDateColumnFilter), Type (bold), Category, Amount (bold right, `'₹' + value`), Notes (flex); pagination 20.
- Milk Sales: Date, Liters, Fat %, SNF %, Rate/L (₹), Total (bold ₹), Buyer (flex); pagination 15.
- Coconut Sales: Date, Count, Price/Each (₹), Total (bold ₹), Buyer; pagination 15.
All grids: single row selection, autoHeight, animateRows, header bg #f5f5f4 color #44403c bold, row hover #f0fdf4.

## 14. Crops

**State (`app/states/crop_state.py`)**: `crops_list`, `current_crop`, `profile_loading`, `profile_active_tab`, `current_dialog_date`, dialog toggles, `add_crop_error`, `dialog_error`, `weather_data`, `weather_loading`, `activity_types` = [Planting, Fertilizing, Pesticide Application, Irrigation, Weeding, Harvesting, Expense].
- **DEMO_CROPS_DATA**: Corn (Field A, planted 2024-04-15, Growing, activities: Planting "Planted 10 acres of corn." ₹500 + Fertilizing "Applied nitrogen fertilizer." ₹350), Wheat (Field B, planted 2023-10-01, Harvested, activity Planting "Planted 20 acres of wheat." ₹800, harvest 2024-03-10 quantity 1000 unit bushels income ₹7000).
- `fetch_crops_list` seeds `"crops"`. `add_crop`: name/field/planting date required ("Crop name is required.", "Field name is required.", "Planting date is mandatory.", "Initial cost must be a valid number."); creates status "Planted", image `https://api.dicebear.com/9.x/shapes/svg?seed={name}`, an initial Planting activity with the cost and notes "Initial planting."; toast `"'{name}' has been added."`; failure "Failed to save crop. Please try again."
- `add_activity`: "Date is mandatory.", "Please select an activity type.", "Cost must be a valid number."; inserts at front; toast `"Activity '{type}' added."`.
- `add_harvest`: "Date is mandatory.", "Quantity is mandatory.", "Quantity must be a valid number.", "Income must be a valid number."; sets status "Harvested"; toast "Harvest record added."
- Vars: `days_since_planting`, `total_investment` (sum of Planting costs across all crops), `total_expenses`, `total_harvest_income`, `profitability`, `expense_breakdown` (with color map Planting #10b981, Fertilizing #3b82f6, Pesticide Application #f97316, Irrigation #06b6d4, Weeding #f59e0b, Harvesting #8b5cf6, Expense #64748b).

**Weather (Open-Meteo, no API key)** — `fetch_weather` is a background event hitting `https://api.open-meteo.com/v1/forecast` with fixed lat/lon (28.6139, 77.209), params: current `temperature_2m,relative_humidity_2m,precipitation,weather_code,wind_speed_10m`, daily `weather_code,temperature_2m_max,temperature_2m_min,precipitation_sum,precipitation_probability_max`, timezone auto. `WEATHER_CODES` dict maps WMO codes to (label, icon) — 0 Clear sky/sun, 1 Mainly clear/sun, 2 Partly cloudy/cloud-sun, 3 Overcast/cloud, 45 Fog/cloudy, 48 Depositing rime fog/cloudy, 51/53/55 Light/Moderate/Dense drizzle/cloud-drizzle, 56/57 freezing drizzle variants, 61/63/65 rain/cloud-rain(+heavy), 66/67 freezing rain, 71/73/75/77 snow/cloud-snow, 80/81/82 showers/cloud-lightning-rain, 85/86 snow showers, 95 thunderstorm/cloud-lightning, 96/99 hail/cloud-hail, else "Unknown"/cloud-question. Vars: `current_weather_info`, `farming_suggestions` (Rain Expected "High chance of rain tomorrow (X%). Consider postponing pesticide application or irrigation." blue/cloud-rain when precip prob >50, else "Good Weather for Field Work" yellow/sun; "High Temperatures" orange/thermometer-sun when max temp >35), `daily_forecast_data` (7 days: day %a, icon, max/min rounded, precip prob).

**List page** (`crop_list.py`): 3 summary cards (Total Crops/sprout emerald, Active Fields/tractor blue, Total Investment `₹{total_investment}` yellow) `grid md:grid-cols-3`; header with static "All" button + "Add New Crop"; crop cards (image h-32, name, field name mono chip, status badge Growing emerald/Harvested blue/Planted yellow/Fallow stone); `grid sm:grid-cols-2 md:grid-cols-3 lg:grid-cols-4 gap-6`; Add dialog (name, field, planting date, initial cost; Cancel/Add Crop).

**Profile page** (`crop_profile.py`): avatar (h-24 rounded-lg), name + status badge, "Field: {name}"; buttons Add Activity, Add Harvest, Edit Details (toast "Edit not yet implemented."). Tabs: Overview, Activity History, Harvest Records. Overview: 5 metric cards (Days Since Planting, Total Activities, Total Expenses ₹, Harvest Income ₹, Profitability ₹) + Expense Breakdown donut + legend. Activity History: table Date/Activity/Cost/Notes. Harvest Records: table Date/Quantity+unit/Income. Dialogs: Add Crop Activity (date, type select, cost, notes), Record Harvest (date, quantity, unit, income).

## 15. Feed Module (`/feed`)

**State (`app/states/feed_state.py`)** — two views: **Operations** (default) and **Analytics**, each with sticky quick-nav pills (`#feed-overview`, `#feed-feeding`, `#feed-inventory`, `#feed-plans`, `#feed-ration`, `#feed-advisor`, `#feed-simulator`, `#feed-reports` / analytics: `#feed-stats`, `#feed-trends`, `#feed-milkfeed`, `#feed-efficiency`, `#feed-planner`, `#feed-alerts`). Pills: active = emerald-500 white, inactive = stone-100. Top tabs: Operations (clipboard-list icon) / Analytics (chart-column icon). Section shell: white card with icon + title + subtitle + anchor id, `scroll-mt-24`.

**Default feed types** (seeded via `ensure_farm_seed("feed_types", ...)`, `is_custom=False`): Rice Bran (Concentrate, kg, ₹28), Pelleted Feed (Theevanam) (Concentrate, kg, ₹35), Cotton Seeds (Concentrate, kg, ₹40), Groundnut Oil Cake (Concentrate, kg, ₹52), Cholam (Fresh Green Fodder) (Home Grown, bundles, ₹15), Cholam Dry Fodder (Home Grown, bundles, ₹20), Rice Straw (Home Grown, bundles, ₹25).

**Constants**: `PLAN_CATEGORIES = ["Calf","Heifer","Pregnant Cow","Lactating Cow","Dry Cow","Bull"]`, `MILK_PRICE_PER_LITER = 40.0`, `FODDER_KEYWORDS` (cholam, sorghum, jowar, fodder, grass, straw, hay, silage, maize, corn, ragi, bajra, millet, cowpea, horse gram, napier, guinea grass), `FEED_UNITS = ("kg","bundles","bags")`, `RATION_REQUIREMENTS = {Calf:4, Heifer:6, Pregnant Cow:8, Lactating Cow:12, Dry Cow:7, Bull:8}`, `NUTRIENT_SCORES` (groundnut oil cake 1.0, cotton seed 0.9, pelleted 0.9, rice bran 0.85, cholam dry 0.45, cholam 0.5, rice straw 0.3), `MAX_FEED_SHARE = 0.7`, `SIM_CHANGE_OPTIONS = ["+5","+10","+20","+50","-10","-20"]`.

**Operations panels**:
- **Overview cards** (`dashboard_cards` var — compute totals for current stock value, monthly feed spend, stock-outs count, today's consumption kg, feed cost/liter, pending restock items; render 6 `feed_card`s with emoji icon + colored chip + title + value + sub).
- **Daily Feeding**: animal chips (round avatar images with emerald border when selected, w-24), feed type chips ("{unit} · ₹{cost}"), Time of Day big buttons (🌅 Morning amber-500 / 🌇 Evening indigo-500 when selected), huge quantity display (text-5xl emerald), quick-add chips +0.5/+1/+2/+5, 3×4 keypad (1-9, 0, ".", delete), notes input, success banner (green, `✓ {animal} · {qty} {unit} {feed}`), "Record Feeding" big emerald button. `record_feeding` validates animal+feed selected ("Select animal and feed type first."), qty>0 ("Quantity must be positive."), unknown feed ("Unknown feed type."); creates consumption, **deducts stock FIFO by expiry date then purchase date**; toast "Feeding recorded.".
- **Inventory & Types**: feed type cards (name, Concentrate 🧪 blue pill / Home Grown 🌾 green pill, "₹X / unit"), "Add Feed Type" link; Current Stock cards (name, status badge 🔴 Out of Stock / 🟡 Low Stock (<10) / 🟢 Sufficient, big quantity, "From {supplier}", "Expires {date}" orange) + "Add Stock"; **Home-Grown Crops → Feed Stock** section: rows per fodder crop (harvested X unit · Y unit in stock, "✓ In stock" emerald or "⏳ Pending sync" amber, "{delta} {unit} new — will move automatically on next page load." orange) with "Sync Now" button; `auto_sync_homegrown_crops` moves new harvests into stock on page load (idempotent via persisted `crop_sync_markers`; creates feed type "{crop} (Harvested)" if no match; batches into stock entries with supplier "Harvest"; toast "Auto-synced N fodder crop(s) into feed stock." when >0).
- **Feeding Plans**: plan cards (name, water reminder pill 💧, 🌅 Morning items, 🌇 Evening items, minerals pill, "Feed All {category} Now" button → `bulk_feed_plan`), "Create Feeding Plan" button.
- **Ration Optimizer**: animal group select, cheapest ration output (items with name + "✓ in stock" + "{qty} {unit} · ₹{cost}", total "Est. cost / day ₹X"), disclaimer "Estimate based on nutrient density. Confirm with your veterinarian before changing rations." Greedy algorithm: sort by cost/nutrient-score, cap each feed at 70% of requirement, top-up with cheapest.
- **AI Nutrition Advisor**: rule-based per-animal recommendation cards (📈 "Increase {feed}" — if milk ≥15L and concentrate share <40%, boost 0.5/0.8 kg; ⚠️ "Reduce concentrate" when share >60%; 🌱 "Increase green fodder" when <20%; 💰 "Balance protein & energy" when milk revenue/feed cost <1.2), max 6, colored headers.
- **Feed Simulator**: feed select, animal select (or all), change % quick buttons, results (feed name, "{current} → {new} {unit} / day", verdict 💰 Profitable / ⚖️ Break-even / ⚠️ Not profitable, Milk change ±L/day, Feed cost ±₹/day, Profit ±₹/day @ ₹40/L), footnote "Rough rule: +1 kg concentrate ≈ +0.8 L milk/day; +1 kg fodder ≈ +0.3 L/day. Estimate only."
- **Feed Reports**: 6 report cards (Daily Feed Report, Monthly Feed Cost, Milk vs Feed Report, Feed Purchase Report, Feed Waste Report, Animal Nutrition Report), each with a "PDF" download button → `generate_feed_report`.

**Analytics panels**:
- **Consumption & Cost** tiles: Today kg, This Week kg, This Month kg, Monthly Feed Cost ₹ (consumption cost + "Cattle Feed" expense transactions this month), Feed Cost / Liter ₹.
- **Trends & Breakdown**: area chart "Feed Cost Trend (6 months)" (emerald #10b981 / fill #a7f3d0); "Consumption by Feed (30 days)" horizontal percentage bars (qty kg · ₹cost).
- **Milk vs Feed**: grouped bar chart (milk blue #3b82f6, feed orange #f59e0b, L/day vs kg/day 7-day averages) + insight cards (📈 milk up ≥8%, 📉 down ≥8% with tailored advice, 🏆 best milk-per-₹ feed, ⚠️ high intake low milk <0.3 L/kg).
- **Efficiency**: bar chart "Efficiency Score (0–100)" (purple #8b5cf6, domain 0-100) + ranked rows (avatar, name, "{milk_per_kg} L/kg · ₹{milk_per_rupee} milk per ₹ feed", score bar + number, rank badge Excellent emerald ≥70 / Good blue ≥55 / Average amber ≥40 / Needs Attention red). Score = clamp(milk_per_kg × 45, 0, 100).
- **Purchase Planner**: suggestion rows ("{name} will last ~X days. Buy {qty} {unit} next week." + "Buy X {unit}" pill) when days-left ≤14, sorted by days left, max 6.
- **Smart Alerts**: ⛔ Out of stock, ⚠️ Low stock, ⏰ Expiring soon (≤7 days), 🔥 Consumption spike (>30% vs prev week); empty state "All clear! No feed alerts right now." (shield-check).

**Feed dialogs** (`dialogs.py`): standard modal shell (`bg-black/50` backdrop + `max-w-lg` white card, scrollable). Add Feed Type (name, category Concentrate/Home Grown, unit kg/bundles/bags, cost per unit; toast "Added feed type '{name}'." / "Failed to save feed type."). Add Stock (feed type select, quantity, unit, purchase date, expiry date, supplier, total cost; toast "Stock added." / "Failed to save stock."). Create Feeding Plan (animal group, morning feed + qty, evening feed + qty, mineral supplements, water reminder Yes/No toggle; toast "Feeding plan created." / "Failed to save plan.").

## 16. Milk & Society Bills (`/milk`)

**State (`app/states/milk_state.py`)**: `DEFAULT_SOCIETIES = ["Aavin","Hatsun Agro","Heritage","Dodla","Arokya","Private Customer","Other"]`. Form fields: date, society (default Aavin), liters, fat_percentage, snf_percentage, clr, rate_per_liter, amount, bill_number, payment_status, animal_id, notes. Setters clamp defensively: liters ≤100000, fat 0–10, snf 6–12, clr 0–40, rate ≤10000, amount ≤10M, bill_number ≤60 chars.
- Vars: `milk_sales` (sorted desc by date), `societies` (defaults + custom buyers sorted, deduped), `month_litres`, `month_income`, `pending_amount` (unpaid this month), `avg_fat_month`, `avg_snf_month` (current calendar month), `society_stats` (per society: litres, income, avg fat/snf, bills, pending; sorted by income desc), `suggested_rate` (from stored slab table: highest slab with fat_min ≤ fat), `expected_amount` (liters × rate), `amount_mismatch` (amount>0 and rate>0 and |amount − expected| > max(1, expected×2%)).
- `add_bill`: errors — "Litres must be greater than 0.", "Fat % must be between 0 and 10.", "SNF % must be between 6 and 12.", "Enter the rate per litre (or the total amount from the bill)."; derives rate from amount/liters if needed; total = amount if set else liters×rate; creates a **MilkSale** AND a linked **income Transaction** with category Milk Sale and notes `"[{sale_id}] Sold {x}L milk to {society}"`; toast "Bill saved successfully!" / "Could not save the bill. Please try again."
- `toggle_payment(sale_id)`: flips pending↔paid, sets paid_date when paid; toasts "Bill marked as paid. 🎉" / "Bill marked as pending." / "Could not update payment status." / "Bill not found."
- `delete_bill`: deletes the milk sale + the linked transaction (by note prefix); toast "Bill deleted."
- `handle_bill_upload` (OCR via Gemini vision): reads first file (≤10 MB), builds an OCR prompt asking for strict JSON `{"date","society","litres","fat_percentage","snf_percentage","clr","rate_per_liter","total_amount","bill_number"}` with rules (numbers without units; compute rate when only amount+litres; prefer printed date; ignore member IDs), calls `retry_across_models` with `response_mime_type="application/json"`, applies sanitized results (date only if within last year), sets `scan_message` ("Bill scanned! Please check the fields and press Save Bill." / fallback messages). `scanning` flag shows spinner "Reading the bill…".

**Page** (`milk_page.py`): 5 stat cards (Litres Supplied (Month)/droplets sky, Milk Income (Month)/indian-rupee emerald, Avg Fat % (Month)/beef orange "target 3.5–4.5%", Avg SNF % (Month)/test-tube blue "target 8.0–9.0%", Pending Payment/hourglass amber) in `grid grid-cols-2 md:grid-cols-3 xl:grid-cols-5 gap-6`. Main grid lg:grid-cols-3: left (col-span-2) = **Scan Society Bill** card (📷 title, dashed emerald dropzone, "Click to select or drag the bill photo here", JPG/PNG/WebP, max 1 file, spinner while scanning, success message banner) + **Enter Bill Slip** form (Milk Society select, Date, Litres, Fat %, SNF %, CLR optional, suggested-rate amber banner with "Use this rate" button when suggested_rate>0, Rate per Litre ₹, Amount from Bill ₹, Bill Number, mismatch red warning "Bill amount (₹X) doesn't match Y L × ₹Z = ₹W. Double-check the slip before saving.", Payment Status select, Animal optional select, Notes, Save Bill emerald + Clear) ; right = **Rate Checker** (society select + Load, editable slabs "Fat % at least" + "Rate (₹/L)" rows with delete, Add Slab, Save Rate Table, "Saved ✓"). Then **Society Performance** cards (bills chip, Litres, Income, Avg Fat/SNF, Pending; empty state text). Then **Bill History** (rows: date + bill number, society with landmark icon, "X L" + "Fat X% · SNF Y%", "₹total" + "@ ₹rate/L", Paid/Pending pill, Mark Paid/Mark Pending button, trash → "Confirm?" red delete). Page title "Milk & Society Bills".

## 17. Insights & AI (`/insights`)

**Hub** (`insights_hub.py`): segmented control tabs **Farm Insights** (cloud-sun) / **AI Assistant** (bot). Switching to AI tab also triggers `AIInsightsState.refresh_insights`. Page title "Insights & AI".

**Farm Insights tab** (`farm_insights.py`): Current Weather card (big temp °C, condition, wind km/h, humidity %, precipitation mm, weather icon yellow-500) + 7-Day Forecast card (day, icon, "max° / min°", precip % with umbrella) in `grid lg:grid-cols-3`; **Farming Suggestions** section (rain or fieldwork + heat advisories); loading skeletons (`animate-pulse h-48`); `on_mount=fetch_weather`.

**AI Assistant tab** (`ai_insights.py`):
- **health_score_card**: "Farm Health Score", refresh button (spins while loading), big score + "/100", progress bar (`width: {score}%`), caption depending on score (≥80 "Your farm is performing well above average.", ≥60 "Your farm is doing okay. Check recommendations for improvements.", else "Your farm needs attention. Review the recommendations below.").
- **insights_widget**: "AI Recommendations" cards (icon by type: optimization trending-up blue, warning alert-triangle red, opportunity lightbulb yellow, info stone; loading = 3 pulsing skeletons) + "Seasonal Tips" checklist.
- **ai_chatbot_section**: "Ask AgriLedger AI" header (brain-circuit), message area (empty state: "Ask me anything about your farm!" + 4 suggestion chips: "Why did milk production drop?", "How can I reduce feed costs?", "What crops should I plant next?", "How is my breeding success rate?"), chat bubbles (user = emerald-500 right-aligned with user avatar, bot = stone-100 left with blue bot avatar, max-w-md rounded-2xl), input + send button; Enter key sends.

**State (`ai_insights_state.py`)**:
- Defaults: `health_score=85`, sample recommendations/tips, `chat_messages=[]`, `chat_input`, `chat_loading`.
- `refresh_insights` (background): score starts 100; deductions — if income>0: expense ratio >0.9 → −25, >0.7 → −15, >0.5 → −5; elif expenses>0 → −30; else −10. Sick animals: >20% → −30, >10% → −20, >0 → −10. No active crops but crops exist → −10. Clamp 0–100. If Gemini configured, prompt for 3 recommendations (JSON keys `recommendations` [{title, desc, type}], `seasonal_tips` [strings]; type must be optimization/warning/opportunity/info; <15 words; use ₹) via `retry_across_models`; sanitize nested values. Rule fallback: "Cost Control Needed" (warning) when expenses>income; "Healthy Profit Margin" (opportunity) when income > 1.5×expenses; "Sick Animals Alert" (warning) / "Herd Health" (info); "Active Growth" (optimization) when growing crops; else "Data Needed" (info). Seasonal tips by month: Mar–May ["Prepare soil for planting.","Inspect irrigation systems."]; Jun–Aug ["Ensure water availability for livestock.","Monitor crops for pests."]; Sep–Nov ["Plan harvest logistics.","Prepare barns for winter."]; else ["Protect animals from cold.","Maintain machinery."].
- `send_chat_message` (background): appends user message, builds farm context (income, expense, net, animals, sick, active crops, milk/coconut counts, current month), Gemini chat with system instruction ("You are AgriLedger AI, a helpful farm management assistant. Answer questions about the farmer's data concisely and practically. Give specific, actionable advice. Keep responses under 100 words. Context: {context}") via `retry_across_models`; fallback `_rule_based_response` answering milk-drop / feed-cost / crop-planting / profit / health / breeding questions with the exact canned strings in the source.
- `ask_question(q)` fills chat_input and sends. `handle_chat_key` sends on Enter.

## 18. Reports & Exports (`/reports`)

**State (`reports_state.py`)**: `date_range` ("Last 30 Days"), `custom_start_date` (−30d), `custom_end_date` (today), `generated_file_url`, `show_download_link`. `set_date_range` sets bounds for "Last 30 Days", "Last Month", "This Year". Vars computed from in-range transactions: `total_income`, `total_expenses`, `net_profit`, `expense_by_category` (top 5, fills ["#10b981","#f97316","#3b82f6","#f59e0b","#8b5cf6"]).
- `generate_pdf_report`: reportlab letter page "AgriLedger Farm Report", "Date Range: {start} to {end}", "Financial Summary", "Total Income: ₹{...}", "Total Expenses: ₹{...}", "Net Profit: ₹{...}"; saves to `rx.get_upload_dir()` as `report_{timestamp}.pdf`; returns `rx.download(url="/_upload/{filename}")`; error → toast `"Error generating PDF: {str(e)}"`.
- `generate_excel_report`: openpyxl workbook "Financial Summary" with title row, date range, Metric/Value table; `report_{timestamp}.xlsx`; error toast similar.

**Page** (`reports_page.py`): Date Range selector (3 pill buttons), Financial Summary (3 cards: Total Income trending-up emerald, Total Expenses trending-down red, Net Profit wallet blue), Expense Breakdown (donut pie inner 60 outer 100 padding 3 + list rows name/₹value), Export Reports ("Generate PDF Report" red button, "Generate Excel Report" emerald button). Page title "Reports & Exports".

## 19. Settings (`/settings`)

Sections (stacked, `max-w-4xl mx-auto`):
1. **Profile Settings** — Full Name (default = current user name), Email (disabled, `bg-stone-50`), "Update Profile" (validates name required → "Full name is required.", toast "Profile updated successfully!").
2. **Farm Details** — Farm Name ("My Green Farm"), Location ("Springfield"), Farm Size ("50 Acres"); validates name+location ("Farm name is required." / "Farm location is required."), toast "Farm details updated successfully!".
3. **Language / மொழி / भाषा** — three pill buttons English / தமிழ் (Tamil) / हिन्दी (Hindi), emerald when active.
4. **Notification Preferences** — toggle rows: Email Notifications ("Receive alerts and reports via email."), SMS Alerts ("Receive critical alerts (breeding, weather) via SMS."), In-App Notifications ("Show alerts within the dashboard."); then "Upcoming Reminders" list from `NotificationState` ("No pending notifications." when empty).
5. **Preferences** — Dark Mode toggle; "Backup All Data" (dark stone-800 button, toast "Data backup initiated. You will receive an email shortly.").
6. **Install App** (only when `install_prompt_available`) — description + install button + iOS tip "Tip: on iOS, use your browser's Share → Add to Home Screen."
7. **Integrations** — rows: Gemini (AI + Bill Scanning) — badge "Active · {model}" emerald if configured else yellow "Set GEMINI_API_KEY in .env & restart"; Resend (Email) — yellow "Configure via RESEND_API_KEY"; Twilio (SMS/WhatsApp) — yellow "Configure via TWILIO_*"; OpenWeatherMap — emerald "Active (Open-Meteo)" with note that weather uses the free Open-Meteo API.

**NotificationState** (`notification_state.py`): `notifications`, `show_notifications`, `unread_count`; `add_notification`, `mark_all_read`, `clear_notifications`, `dismiss_notification`.

**I18n** (`i18n_state.py`): `TRANSLATIONS` dict with full key sets for English, Tamil, Hindi (nav, dashboard, common, animals, tx, reports, settings, landing keys — reproduce the exact translation strings from the file). `I18nState.language` default "English", `t` computed var returns current dict, `translate(key)` falls back to English.

## 20. Services

- **`gemini_service.py`**: `extract_json(text)` — strips markdown fences, tries `json.loads`, then finds the first balanced `{...}` block (brace-depth scanner respecting strings/escapes); returns None on failure. `retry_across_models(operation, models=None)` — tries each model candidate (default `config.gemini.model_candidates`), returns first non-None result, else None; logs debug per-failure, warning only when all fail.
- **`email_service.py`**: `EmailService` stub — `is_configured` always True; `send_email`, `send_monthly_report`, `send_breeding_alert`, `send_weather_alert` just log `Stub ... request` and return True. Global `email_service`.
- **`sms_service.py`**: `SMSService` — `is_configured` True; `_generate_wa_link(to, body)` builds `https://wa.me/{number}?text={quoted}` and defaults to +91 country code; `send_sms`/`send_whatsapp`/`send_breeding_reminder` (🐄 header)/`send_vaccination_reminder` (💉)/`send_weather_alert` (⛈️)/`send_payment_reminder` (💰)/`send_calving_alert` (🍼) with the exact emoji-formatted bodies from the source; log + return True. Global `sms_service`.
- **`scheduler_service.py`**: `check_breeding_reminders` (pregnancy check due ≥30 days post-insemination unconfirmed → "breeding_check" high; calving within 7 days & confirmed → "calving_expected" medium; pending_confirmation >45 days → "rebreeding" medium), `check_vaccination_reminders` (due ≤14 days → "vaccination"; overdue → "vaccination_overdue" high), `check_health_reminders` (Sick/Under Treatment → "health" high), `generate_all_alerts` combines all.

## 21. PWA Assets (`assets/`)

- **manifest.json**: name "AgriLedger - Smart Farm Management", short_name "AgriLedger", description, start_url "/dashboard", scope "/", display standalone, orientation portrait, background_color "#f5f5f4", theme_color "#10b981", categories [agriculture, business, finance], icons: icon-192.png + icon-512.png (any) and icon-maskable-192.png + icon-maskable-512.png (maskable).
- **sw.js**: minimal — VERSION "1.0.0", install → skipWaiting, activate → clients.claim, fetch → intentionally empty pass-through (comment explaining it exists only to qualify for installability).
- Icons: PNG files `apple-touch-icon-180.png`, `icon-192.png`, `icon-512.png`, `icon-maskable-192.png`, `icon-maskable-512.png`.
- `index()` (root landing) also sets `bg-cream-100 font-['Lato']` and smooth scroll.

## 22. Demo Seed Data Summary (per-farm, only when a farm has no rows)

- **cattle**: 7 animals as in §11. **crops**: Corn + Wheat as in §14. **breeding_cycles**: bc1 (Lakshmi, pending confirmation) + bc2 (Ganga, pregnant) as in §12. **feed_types**: the 7 defaults in §15. All seeded rows get fresh uuid4 ids and the farm's real farm_id (the in-state DEMO lists keep the fixed ids c1/c2/s1/s2/g1/p1/p2, crop1/crop2, bc1/bc2 for reference).

## 23. Dashboard/Pages demo fallback data

Module-level `_DEMO_*` in `dashboard_state.py`: summary metrics (all ₹0 / 0 L), expense data (Feed 400 #10b981, Medicine 300 #f97316, Labor 300 #3b82f6, Utilities 200 #f59e0b, Other 278 #8b5cf6), milk data (Mon 180 … Sun 215), weather highlight (28°C Sunny sun "Perfect day for harvesting. Low humidity."), reminders (["Add farm data to see smart reminders"]).

## 24. Tests

Create a pytest suite covering: password hashing/verification, config loading + production fail-fast, token create/decode (expiry, tamper), i18n translations, rate limiter, service stubs, transaction keypad logic, quick-add, milk-bill OCR parsing helpers, suggested-rate slab lookup, breeding gestation calc (280/310), DashboardState aggregations (with seeded states), feed state helpers (fodder detection, unit normalization, efficiency ranking, cheapest ration), reports filtering. No test may require a live MongoDB connection (mock/fake the DB layer).

## 25. Final Checks

- Every page title must match: "Dashboard Overview", "Add New Transaction", "Animal Management", "Cattle Profile", "Breeding Cycles", "Breeding Cycle Details", "Crop Management", "Crop Profile", "Feed Intelligence" (page header "Feed Intelligence" — the in-page title shown is the h1 "Feed Intelligence"), "Insights & AI", "Milk & Society Bills", "Reports & Exports", "Settings", "Transactions".
- Every toast message and validation string must match the exact copy given above.
- Currency is always ₹ with comma grouping; dates are ISO `YYYY-MM-DD` in data and shown raw; milk litres one decimal where formatted.
- The app must run with `reflex run` (UI on :3000) and `uvicorn app.api:app` (API on :8000) using only the listed dependencies, and must work with zero paid API keys (all external services fall back to stubs/rule-based logic).
- Preserve accessibility touches present in the source: aria-labels, skip-link, sr-only texts, focus rings (focus:ring-emerald-400/300), role attributes.

Build the complete project now. Do not omit, rename, or "improve" any feature, string, color, formula, or behavior described above — reproduce it exactly.
