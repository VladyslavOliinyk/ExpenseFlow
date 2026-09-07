# ExpenseFlow

Internal expense reimbursement approval service for organizations. Employees submit expense claims; claims are automatically routed to the appropriate approver based on category. An AI component provides advisory analysis for approvers — never decision-making, never blocking.

## Tech stack

| Layer | Technology |
|-------|-----------|
| Backend | FastAPI, Python 3.12 |
| Database | PostgreSQL 16, SQLAlchemy + Alembic |
| Frontend | React 19, TypeScript, Vite |
| Styling | Tailwind CSS 4, shadcn/ui (Radix UI) |
| State / fetching | Zustand (auth), TanStack Query (server state) |
| AI | Claude Haiku (`claude-haiku-4-5-20251001`) → Gemini Flash (model name configurable via `GOOGLE_AI_MODEL`, see env table) fallback; Mock provider for local dev |
| Infrastructure | Docker Compose (PostgreSQL only; backend/frontend run locally) |

## Features

### Per spec

| Requirement | Implementation |
|-------------|---------------|
| Two roles: employee + approver, same person can hold both | Users have a `managed_category_ids` list; non-empty = approver for those categories |
| Claim: amount (USD), category, description, expense date, payment details | `POST /claims`; all five fields required, with frontend field-level validation |
| Category → approver routing | Each `Category` has an `approver_id`; `GET /claims/queue` returns only claims in the manager's categories |
| Statuses: pending / approved / rejected / withdrawn | `ClaimStatus` enum; `POST /claims/{id}/withdraw` only allowed while `pending` |
| Approve or reject; reject requires comment | `POST /claims/{id}/approve`, `POST /claims/{id}/reject` with mandatory comment |
| Data isolation | `GET /claims/mine` (own claims) vs `GET /claims/queue` (own queue), both scoped to current user |
| AI: short summary + mismatch flag when approver opens a claim | `AiInsightBlock` on claim detail page; flags category/description/amount inconsistency (e.g. Office claim with flight receipt description) |
| AI is advisory only; never blocks on failure | Explicit `ai_status` state machine; approver can act regardless of AI result |

### Beyond spec

| Feature | Notes |
|---------|-------|
| AI category suggestion while typing | Debounced `POST /claims/suggest-category`; suggests category with confidence level as user types description |
| "Use AI's reason" button in reject modal | AI's `mismatch_reason` pre-fills reject comment on explicit click — not silent autofill, preserving approver transparency |
| Duplicate detection | Deterministic SQL-based: same requester, amount ±5%, date ±3 days, description similarity >60% — separate from AI, shown as a distinct warning badge |
| AI Metrics dashboard | `GET /admin/ai-metrics` → `/metrics` page: analyzed count, mismatch rate, avg latency, provider breakdown |
| Demo "Sign in as…" switcher | `/login` lists all seed users for instant role switching without passwords |
| Multi-language input | AI prompt explicitly instructs: evaluate content, never flag based on language; tested with Russian/Ukrainian descriptions |

## AI architecture

**Provider-agnostic design.** All providers implement an `AIProvider` abstract base class. Runtime chain (when `AI_MODE=auto`): Claude Haiku (primary) → Gemini Flash (fallback) → `None`.

**Explicit `ai_status` state machine** (`pending → processing → completed | failed`). A previous implicit approach inferred AI loading state from timestamps, which caused race conditions where the UI could incorrectly show "loading" or "done". An explicit status field propagated via API lets the frontend poll precisely while `pending|processing` and stop immediately on a terminal state. When re-analysis fails but a prior result exists, status reverts to `completed` — old data is preserved, never overwritten.

**Prompt design** (`PROMPT_VERSION = "3"`)
- Three independent evaluation rules: category mismatch, vague/evasive description, implausible amount
- Explicitly language-neutral: AI evaluates content only, ignores input language
- `content_hash` deduplication: identical claim content reuses the cached analysis result — no redundant API calls

**Graceful degradation.** If all providers are unavailable, the claim shows "AI insight unavailable" and remains fully actionable. Approve/reject are never blocked by AI state.

## Known limitations

- **Self-approval deadlock** — if the sole approver for a category submits a claim in that same category, nobody can approve it (self-approval guard blocks; no backup approver). Production fix: backup approver per category or admin escalation path.
- **Gemini reliability** — Gemini free tier showed variable latency and occasional 5xx under sustained load during development. Claude was the primary reliable path; Gemini fallback is functional but not the recommended demo path.
- **Gemini coverage for newer AI features** — the core `analyze_claim` flow (summary + mismatch detection) was verified live on both Claude and Gemini, including real fallback scenarios. The newer `suggest-category` endpoint uses the same provider-agnostic abstraction and fallback chain, but was not independently verified against a live Gemini call — free-tier daily quota was exhausted during testing (RPD limit reached) before this specific path could be confirmed end-to-end. It follows the same code path as the verified `analyze_claim` flow, so it is expected to work identically, but this is a documented gap rather than a confirmed result.
- **Demo auth** — login is `POST /auth/login-as/{user_id}` with no password. Intentional for reviewer convenience; not production-ready.
- **Payment details stored as plain text** — production version should mask, encrypt, or integrate with a payment provider.

## Setup & run

**Prerequisites:** Docker, Python 3.12+, Node.js 20+

### 1. Database

```bash
docker-compose up -d
```

Starts PostgreSQL 16 on **port 5433** (host), database `expenseflow`, user/password `expenseflow`.

### 2. Backend

```bash
cd backend
cp .env.example .env       # defaults work with the docker-compose postgres as-is
pip install -e ".[dev]"
alembic upgrade head
python -m app.seed         # creates 5 users, 5 categories, sample claims
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

**Key environment variables** (`backend/.env.example`):

| Variable | Default | Notes |
|----------|---------|-------|
| `DATABASE_URL` | `postgresql://expenseflow:expenseflow@localhost:5433/expenseflow` | Must match docker-compose config |
| `SECRET_KEY` | (set in .env.example) | Change for production |
| `AI_MODE` | `mock` | `mock` = no API keys needed; `auto` = live providers |
| `ANTHROPIC_API_KEY` | — | Required only when `AI_MODE=auto` |
| `GOOGLE_AI_API_KEY` | — | Required only when `AI_MODE=auto` (Gemini fallback) |
| `GOOGLE_AI_MODEL` | `gemini-3.6-flash` | Gemini model name; Google has renamed Gemini models repeatedly — verify the current value in `.env` if using `auto` mode |
| `AI_TIMEOUT_SECONDS` | `10` | Per-provider call timeout (seconds) |

`AI_MODE=mock` uses deterministic fixture responses — works fully offline with no API keys.

### 3. Frontend

```bash
cd frontend
cp .env.example .env       # VITE_API_URL=http://localhost:8000
npm install
npm run dev                # http://localhost:5173
```

### Demo accounts (after seed)

| User | Approver for |
|------|-------------|
| Alice Johnson | Office, Software/Subscriptions |
| Bob Smith | Travel |
| Carol Davis | Client Entertainment |
| Dan Lee | Other |
| Eve Martinez | — (employee only) |

## Testing

```bash
cd backend
pytest          # or pytest -v
```

- `tests/test_ai_router.py` — AI provider fallback chain, timeout handling, content-hash deduplication, invalid JSON recovery
- `tests/test_duplicate_detection.py` — boundary conditions for duplicate matching (amount tolerance, date window, description similarity threshold)

## Possible future improvements

- OCR receipt attachment parsing
- Multi-level approval thresholds (e.g. >$500 requires a second approver)
- Email / Slack notifications on status change
- Backup approver per category (resolves self-approval deadlock)
- Currency conversion (USD only by design in MVP)
- Admin UI for category → manager reassignment
- Rate limiting and production auth (OAuth / SSO)
- CI pipeline (GitHub Actions) running the existing test suite on every PR
- Additional LLM providers (e.g. OpenAI) — the `AIProvider` abstraction already supports adding a new provider without touching the rest of the codebase
- WebSocket-based status updates for true real-time sync (current polling via TanStack Query satisfies the "real-time status" requirement functionally, but a   push-based approach would remove polling latency)
- Duplicate detection currently links to a single matching claim (`duplicate_of_claim_id`); could be extended to reference all matching candidates when multiple exist
