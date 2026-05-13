from __future__ import annotations

import json
import os
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

from fastapi import FastAPI, HTTPException, Request
from fastapi.responses import HTMLResponse, JSONResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from pydantic import BaseModel, EmailStr, Field

import config
import sheets


BASE_DIR = Path(__file__).resolve().parent


def load_env_files() -> None:
    for filename in (".env", ".env.local"):
        path = BASE_DIR / filename
        if not path.exists():
            continue
        for raw in path.read_text(encoding="utf-8").splitlines():
            line = raw.strip()
            if not line or line.startswith("#") or "=" not in line:
                continue
            k, v = line.split("=", 1)
            os.environ.setdefault(k.strip(), v.strip())


load_env_files()


# ─────────────────────────────────────────────────────────────────────────────
# Models
# ─────────────────────────────────────────────────────────────────────────────
class PollSubmission(BaseModel):
    sessionId: str = Field(min_length=1, max_length=64)
    submittedAt: str | None = None
    source: str | None = None
    # Values may be str (single-select) or list[str] (multi-select).
    answers: dict[str, Any]


class LeadSubmission(BaseModel):
    sessionId: str = Field(min_length=1, max_length=64)
    email: EmailStr
    role: str | None = None
    consent: bool = True
    submittedAt: str | None = None


# ─────────────────────────────────────────────────────────────────────────────
# Helpers
# ─────────────────────────────────────────────────────────────────────────────
def now_iso() -> str:
    return datetime.now(timezone.utc).isoformat()


def valid_values(qid: str) -> set[str]:
    for q in config.POLL_QUESTIONS:
        if q["id"] == qid:
            return {o["value"] for o in q["options"]}
    return set()


def validate_answers(answers: dict[str, Any]) -> dict[str, Any]:
    """Validate poll payload. Single-select fields become str; multi become list[str]."""
    cleaned: dict[str, Any] = {}
    for q in config.POLL_QUESTIONS:
        qid = q["id"]
        valid = valid_values(qid)
        v = answers.get(qid)

        if q.get("multi"):
            if not isinstance(v, list) or not v:
                raise HTTPException(status_code=400, detail=f"Missing answer for {qid}.")
            max_sel = int(q.get("max_select") or len(q["options"]))
            if len(v) > max_sel:
                raise HTTPException(
                    status_code=400,
                    detail=f"Too many selections for {qid} (max {max_sel}).",
                )
            seen: set[str] = set()
            ordered: list[str] = []
            for item in v:
                if not isinstance(item, str) or item not in valid:
                    raise HTTPException(
                        status_code=400,
                        detail=f"Invalid value '{item}' for {qid}.",
                    )
                if item not in seen:
                    seen.add(item)
                    ordered.append(item)
            cleaned[qid] = ordered
        else:
            if not isinstance(v, str) or v not in valid:
                raise HTTPException(
                    status_code=400,
                    detail=f"Missing or invalid answer for {qid}.",
                )
            cleaned[qid] = v
    return cleaned


def valid_role_values() -> set[str]:
    return {r["value"] for r in config.LEAD_ROLES}


def build_aggregate() -> dict[str, Any]:
    """Return the aggregate to feed the reveal chart.

    Live sheet data → cached.  Anything missing → fallback.
    Always returns a shape with every question & every option key set.
    """
    live = sheets.fetch_aggregate()
    base: dict[str, Any] = {"total": 0, "updatedAt": now_iso()}
    for q in config.POLL_QUESTIONS:
        base[q["id"]] = {o["value"]: 0.0 for o in q["options"]}

    live_total = live.get("total", 0) if live else 0
    use_live = bool(live) and live_total >= config.LIVE_THRESHOLD
    src = live if use_live else config.FALLBACK_AGGREGATE
    base["total"] = live_total  # always the real sheet count, never the fallback's 250
    base["threshold"] = config.LIVE_THRESHOLD
    for q in config.POLL_QUESTIONS:
        for opt in q["options"]:
            base[q["id"]][opt["value"]] = float(src.get(q["id"], {}).get(opt["value"], 0))
    base["source"] = "sheet" if use_live else "demo"
    return base


# ─────────────────────────────────────────────────────────────────────────────
# App
# ─────────────────────────────────────────────────────────────────────────────
app = FastAPI(title="ZEF Poll · World Hydrogen Summit 2026")
templates = Jinja2Templates(directory=str(BASE_DIR / "templates"))
app.mount("/static", StaticFiles(directory=str(BASE_DIR / "static")), name="static")


@app.get("/", response_class=HTMLResponse)
async def index(request: Request) -> HTMLResponse:
    hook = request.query_params.get("hook", config.DEFAULT_HOOK)
    if hook not in config.HOOK_HEADLINES:
        hook = config.DEFAULT_HOOK
    return templates.TemplateResponse(
        request,
        "index.html",
        {
            "site_title": config.SITE_TITLE,
            "wordmark": config.WORDMARK,
            "hook_eyebrow": config.HOOK_EYEBROW,
            "hook_sub": config.HOOK_SUB,
            "hook_cta": config.HOOK_CTA,
            "hook_cta_hint": config.HOOK_CTA_HINT,
            "hook_sig_left": config.HOOK_SIG_LEFT,
            "hook_sig_right": config.HOOK_SIG_RIGHT,
            "lead_kicker": config.LEAD_KICKER,
            "lead_headline": config.LEAD_HEADLINE,
            "lead_sub": config.LEAD_SUB,
            "lead_submit": config.LEAD_SUBMIT,
            "lead_success_title": config.LEAD_SUCCESS_TITLE,
            "lead_success_sub": config.LEAD_SUCCESS_SUB,
            "lead_sig_left": config.LEAD_SIG_LEFT,
            "lead_sig_right": config.LEAD_SIG_RIGHT,
            "lead_roles": config.LEAD_ROLES,
            "questions": config.POLL_QUESTIONS,
            "default_hook": hook,
            # JSON blobs for the frontend bootstrap
            "questions_json": json.dumps(config.POLL_QUESTIONS, ensure_ascii=False),
            "hooks_json": json.dumps(config.HOOK_HEADLINES, ensure_ascii=False),
            "benchmark_json": json.dumps(config.BENCHMARK, ensure_ascii=False),
            "initial_aggregate_json": json.dumps(build_aggregate(), ensure_ascii=False),
        },
    )


@app.get("/api/results")
async def api_results() -> JSONResponse:
    return JSONResponse(
        build_aggregate(),
        headers={"Cache-Control": "no-store, max-age=0"},
    )


@app.post("/api/poll")
async def api_poll(payload: PollSubmission, request: Request) -> JSONResponse:
    answers = validate_answers(payload.answers)
    row: dict[str, Any] = {
        "type": "poll",
        "timestamp": payload.submittedAt or now_iso(),
        "sessionId": payload.sessionId,
        "source": payload.source or "",
        "userAgent": request.headers.get("user-agent", "")[:200],
        **answers,
    }
    result = sheets.write_submission(row)
    if not result.get("ok"):
        raise HTTPException(status_code=502, detail=result.get("error", "Sheet write failed"))
    return JSONResponse(result, headers={"Cache-Control": "no-store"})


@app.post("/api/lead")
async def api_lead(payload: LeadSubmission, request: Request) -> JSONResponse:
    role = payload.role or ""
    if role and role not in valid_role_values():
        raise HTTPException(status_code=400, detail="Invalid role")

    row = {
        "type": "lead",
        "timestamp": payload.submittedAt or now_iso(),
        "sessionId": payload.sessionId,
        "email": payload.email.strip().lower(),
        "role": role,
        "consent": payload.consent,
        "userAgent": request.headers.get("user-agent", "")[:200],
    }
    result = sheets.write_submission(row)
    if not result.get("ok"):
        raise HTTPException(status_code=502, detail=result.get("error", "Sheet write failed"))
    return JSONResponse(result, headers={"Cache-Control": "no-store"})


@app.get("/api/healthz")
async def healthz() -> JSONResponse:
    return JSONResponse({
        "ok": True,
        "mode": "demo" if sheets.is_demo_mode() else "sheet",
        "questions": [q["id"] for q in config.POLL_QUESTIONS],
    })
