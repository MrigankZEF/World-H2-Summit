# ZEF Poll · World Hydrogen Summit 2026

Mobile-first interactive poll microsite. Phone-shaped on desktop, full-bleed on phones and iPads. Submissions and live aggregates are stored in a Google Sheet via an Apps Script Web App.

## Stack

- FastAPI + Jinja2 + vanilla JS (no build step).
- Storage: Google Sheet, accessed through a Google Apps Script Web App (`apps_script.gs`).
- Design system: Space Grotesk + Inter, ZEF red `#E4002B`, warm off-white `#F5F2EE`, deep charcoal `#1A1A1A`.

## What's in it

Six questions, mix of single-select and one multi-select:

| # | Question | Type |
|---|---|---|
| Q1 | Green H₂ price by 2030 | Single (price band) |
| Q2 | What drives the cost of green H₂? | **Multi-select, up to 3** |
| Q3 | GW operational by 2035 | Single (range) |
| Q4 | End-use of green H₂ | Single |
| Q5 | Continent of production in 2035 | Single |
| Q6 | Adoption price | Single (price band) |

The reveal screen shows Q1's distribution + a "ZEF target · <€3/kg by 2030" marker (framed as a goal, not a claim). Expand "See all 6 charts" for Q2–Q6.

## Run locally (VS Code PowerShell terminal)

```powershell
py -m venv .venv
.venv\Scripts\activate
py -m pip install -r requirements.txt
copy .env.example .env.local
py -m uvicorn main:app --reload
```

Open <http://127.0.0.1:8000>.

`.env.local` defaults to `POLL_STORAGE_MODE=demo` so the app runs without any Google setup — submissions are accepted but discarded, and the reveal chart shows demo aggregates from `config.FALLBACK_AGGREGATE`.

Want to see just the design without running anything? Open [`preview.html`](preview.html) directly in a browser — fully self-contained, no server needed.

## Connect a Google Sheet (5 minutes)

1. Create or open the Google Sheet you want to receive submissions.
2. **Extensions → Apps Script**. Delete `Code.gs` contents and paste everything from `apps_script.gs`. Save.
3. **Deploy → New deployment → Web app**.
   - *Execute as*: **Me**.
   - *Who has access*: **Anyone**.
   - Authorize the script when prompted.
4. Copy the **/exec** URL it gives you.
5. In `.env.local`:
   ```env
   POLL_STORAGE_MODE=live
   APPS_SCRIPT_URL=https://script.google.com/macros/s/AKfyc…/exec
   ```
6. Restart the server. Submissions now append rows to the `Submissions` tab, and `/api/results` aggregates live counts from that tab.

The first poll submission creates the `Submissions` tab with headers automatically.

### Sheet schema

| Column | Notes |
|---|---|
| Timestamp, Type, SessionId, Email, Role | metadata |
| q1 | single value e.g. `2to3` |
| **q2** | **comma-separated** e.g. `power,electrolyzers,epc` |
| q3, q4, q5, q6 | single value |
| Source, Consent, UserAgent | metadata |

Each respondent produces **one `poll` row** (when they finish Q6) and optionally **one `lead` row** (if they submit an email). Both rows share a `SessionId` so you can link them.

## Edit questions

All copy and questions live in [`config.py`](config.py):

- `POLL_QUESTIONS` — id, eyebrow number, headline (HTML allowed for `<sub>`, `<b>`, etc.), supporting copy, option list, short labels for the reveal chart. Mark a question as multi-select with `"multi": True, "max_select": N`.
- `HOOK_HEADLINES` — rotating hook lines. Switch by URL: `?hook=A|B|C|D`.
- `BENCHMARK` — the dark target marker on the reveal chart. Point it at any question via `question_id`, or set to `None` to hide.
- `LEAD_*` — copy for the email-capture screen.
- `LIVE_THRESHOLD` — how many real submissions before the reveal flips from fallback to live data (default 5).

### When you change questions, ALSO update Apps Script

If you add, remove, or rename a question `id`, **OR** change which questions are multi-select:

1. Update `QUESTION_IDS` and `MULTI_QUESTION_IDS` at the top of [`apps_script.gs`](apps_script.gs).
2. In the Apps Script editor: **Deploy → Manage deployments → ✏️ on the active deployment → Version: New version → Deploy**.
3. (Optional but recommended) Clear the `Submissions` tab so old rows don't pollute the aggregate — the schema may not match anymore.

The `/exec` URL stays the same across redeployments, so you don't need to update `APPS_SCRIPT_URL`.

## Mobile & iPad

- Viewport is `width=device-width, initial-scale=1, viewport-fit=cover` with safe-area padding on the dark stage backdrop, so notched iPhones and iPads in any orientation render cleanly.
- The phone-shape (max 420 × 880) is preserved on tablets so the design composition stays intentional. On screens narrower than 500px the frame removes its bezel and goes full-bleed.
- All tap targets are ≥ 44 px; single-select questions lock-and-advance, multi-select shows a Continue button.

## API

All responses include `Cache-Control: no-store`.

| Method | Path | Body / response |
|---|---|---|
| `GET` | `/` | The microsite. Accepts `?hook=A|B|C|D`. |
| `GET` | `/api/results` | `{ total, q1: { value: share, … }, q2: …, …, source, updatedAt }`. |
| `POST` | `/api/poll` | `{ sessionId, submittedAt?, source?, answers: { q1, q2: [...], q3, q4, q5, q6 } }`. |
| `POST` | `/api/lead` | `{ sessionId, email, role?, consent, submittedAt? }`. |
| `GET` | `/api/healthz` | `{ ok, mode, questions }`. |

## Deploy

The app is currently deployed on Railway at `world-h2-summit-zef.up.railway.app`. Push to the `main` branch and Railway auto-rebuilds in ~60s.

To deploy elsewhere: anything that runs `uvicorn main:app` works — Render, Fly.io, a small VM. Set the environment variables (`POLL_STORAGE_MODE=live`, `APPS_SCRIPT_URL=…`) in the host's dashboard.

## Demo hotkeys (desktop only)

- `d` — jump to REVEAL with placeholder answers (Q2 picks 2 options).
- `h` — return to the hook (clears answers).
- `←` / `→` — step through scenes.
