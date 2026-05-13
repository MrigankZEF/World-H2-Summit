"""
Google Sheets integration via an Apps Script Web App webhook.

Setup (one-time):
  1. Open the Google Sheet you want to store submissions in.
  2. Extensions → Apps Script. Paste contents of apps_script.gs, save.
  3. Deploy → New deployment → Type: Web app
        Execute as: Me
        Who has access: Anyone
     Copy the /exec URL it gives you.
  4. Put that URL in .env as APPS_SCRIPT_URL.
"""
from __future__ import annotations

import json
import os
import time
from typing import Any

import requests


def _url() -> str | None:
    return os.getenv("APPS_SCRIPT_URL") or None


def is_demo_mode() -> bool:
    if os.getenv("POLL_STORAGE_MODE", "").lower() == "demo":
        return True
    return not _url()


# ── In-memory cache for the aggregate (5s) so /api/results stays cheap ──
_cache: dict[str, Any] = {"at": 0.0, "data": None}
_CACHE_TTL = 5.0


def write_submission(payload: dict[str, Any]) -> dict[str, Any]:
    """POST a submission row to the sheet. Returns {ok: bool, ...}."""
    if is_demo_mode():
        return {"ok": True, "mode": "demo"}

    try:
        resp = requests.post(
            _url(),
            data=json.dumps(payload),
            headers={"Content-Type": "application/json"},
            timeout=15,
            allow_redirects=True,
        )
        resp.raise_for_status()
        # Bust aggregate cache so the next /api/results reflects this row.
        _cache["at"] = 0.0
        try:
            return {"ok": True, "mode": "sheet", **resp.json()}
        except ValueError:
            return {"ok": True, "mode": "sheet"}
    except Exception as err:  # noqa: BLE001
        return {"ok": False, "mode": "sheet", "error": str(err)}


def fetch_aggregate() -> dict[str, Any] | None:
    """GET live aggregate counts from the sheet. Returns None on any error."""
    if is_demo_mode():
        return None

    now = time.time()
    if _cache["data"] is not None and now - _cache["at"] < _CACHE_TTL:
        return _cache["data"]

    try:
        resp = requests.get(_url(), timeout=10)
        resp.raise_for_status()
        data = resp.json()
        _cache["at"] = now
        _cache["data"] = data
        return data
    except Exception:
        return None
