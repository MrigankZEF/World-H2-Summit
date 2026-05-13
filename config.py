"""
ZEF Poll configuration — the single place to edit questions, copy, and branding.

Edit POLL_QUESTIONS to change questions, options, hints, or chart labels.
Edit HOOK_HEADLINES to change rotating hook lines.
Edit BENCHMARK to change the ZEF target marker shown on the reveal chart.

Inline HTML is allowed in `headline` / `sub` (for H<sub>2</sub>, bold, etc.).

A question can be marked multi-select with `"multi": True` and `"max_select": N`.
"""
from __future__ import annotations

from typing import TypedDict


class Option(TypedDict):
    value: str
    label: str
    hint: str


class Question(TypedDict, total=False):
    id: str
    number: str
    headline: str
    sub: str
    chart_title: str
    options: list[Option]
    short_labels: dict[str, str]
    multi: bool
    max_select: int


# ─────────────────────────────────────────────────────────────────────────────
# Questions
# ─────────────────────────────────────────────────────────────────────────────
POLL_QUESTIONS: list[Question] = [
    {
        "id": "q1",
        "number": "01",
        "headline": 'Where will green H<span style="vertical-align:sub;font-size:.6em">2</span> land by 2030?',
        "sub": "<b>&euro; / kg</b> &middot; best guess",
        "chart_title": "Q1 &middot; &euro;/kg by 2030",
        "options": [
            {"value": "lt2",  "label": "Under €2",  "hint": "Aggressive"},
            {"value": "2to3", "label": "€2 – €3",   "hint": "The consensus"},
            {"value": "3to5", "label": "€3 – €5",   "hint": "Cautious"},
            {"value": "5to8", "label": "€5 – €8",   "hint": "Skeptical"},
            {"value": "gt8",  "label": "Over €8",   "hint": "Very skeptical"},
        ],
        "short_labels": {
            "lt2": "< €2",
            "2to3": "€2–3",
            "3to5": "€3–5",
            "5to8": "€5–8",
            "gt8": "> €8",
        },
    },
    {
        "id": "q2",
        "number": "02",
        "headline": 'What drives the cost of green H<span style="vertical-align:sub;font-size:.6em">2</span>?',
        "sub": "<b>Pick up to 3</b> &middot; multiple choice",
        "chart_title": "Q2 &middot; Top cost drivers",
        "multi": True,
        "max_select": 3,
        "options": [
            {"value": "power",         "label": "Power",         "hint": "Electricity price"},
            {"value": "electrolyzers", "label": "Electrolyzers", "hint": "CAPEX, supply"},
            {"value": "epc",           "label": "EPC costs",     "hint": "Build & integration"},
            {"value": "certification", "label": "Certification", "hint": "Standards, audits"},
            {"value": "cost",          "label": "Capital cost",  "hint": "Financing, WACC"},
            {"value": "demand",        "label": "Demand",        "hint": "Offtake uncertainty"},
        ],
        "short_labels": {
            "power": "Power",
            "electrolyzers": "Electrolyzers",
            "epc": "EPC",
            "certification": "Certification",
            "cost": "Capital",
            "demand": "Demand",
        },
    },
    {
        "id": "q3",
        "number": "03",
        "headline": 'How many GW of green H<span style="vertical-align:sub;font-size:.6em">2</span> by 2035?',
        "sub": "Operational gigawatts &middot; global",
        "chart_title": "Q3 &middot; GW operational by 2035",
        "options": [
            {"value": "lt20",     "label": "Under 20 GW", "hint": "Stalled"},
            {"value": "20to100",  "label": "20 – 100 GW", "hint": "Slow build"},
            {"value": "100to250", "label": "100 – 250 GW", "hint": "On pace"},
            {"value": "250to500", "label": "250 – 500 GW", "hint": "Acceleration"},
            {"value": "gt500",    "label": "Over 500 GW", "hint": "Boom"},
        ],
        "short_labels": {
            "lt20": "< 20",
            "20to100": "20–100",
            "100to250": "100–250",
            "250to500": "250–500",
            "gt500": "> 500",
        },
    },
    {
        "id": "q4",
        "number": "04",
        "headline": 'Where will green H<span style="vertical-align:sub;font-size:.6em">2</span> actually be used?',
        "sub": "Pick the biggest use case",
        "chart_title": "Q4 &middot; End-use",
        "options": [
            {"value": "methanol",  "label": "Methanol",                "hint": "Feedstock"},
            {"value": "ammonia",   "label": "Ammonia",                 "hint": "Fertilizer + carrier"},
            {"value": "refinery",  "label": "Refinery",                "hint": "Hydrocrackers"},
            {"value": "transport", "label": "H₂ as transport fuel",    "hint": "Trucks, buses"},
            {"value": "emethane",  "label": "e-Methane",               "hint": "Gas grid"},
            {"value": "esaf",      "label": "eSAF / jet fuel",         "hint": "Aviation"},
        ],
        "short_labels": {
            "methanol": "Methanol",
            "ammonia": "Ammonia",
            "refinery": "Refinery",
            "transport": "Transport",
            "emethane": "e-Methane",
            "esaf": "eSAF",
        },
    },
    {
        "id": "q5",
        "number": "05",
        "headline": 'Where will most green H<span style="vertical-align:sub;font-size:.6em">2</span> be produced in 2035?',
        "sub": "Pick the continent",
        "chart_title": "Q5 &middot; Production continent",
        "options": [
            {"value": "africa",  "label": "Africa",        "hint": "Solar abundance"},
            {"value": "eu",      "label": "Europe",        "hint": "Policy push"},
            {"value": "asia",    "label": "Asia",          "hint": "Demand pull"},
            {"value": "anz",     "label": "Australia",     "hint": "Export plays"},
            {"value": "northam", "label": "North America", "hint": "IRA, scale"},
            {"value": "southam", "label": "South America", "hint": "Hydro + wind"},
        ],
        "short_labels": {
            "africa": "Africa",
            "eu": "Europe",
            "asia": "Asia",
            "anz": "Australia",
            "northam": "N. America",
            "southam": "S. America",
        },
    },
    {
        "id": "q6",
        "number": "06",
        "headline": "You'd seriously adopt at…",
        "sub": '<b>&euro; / kg</b> H<span style="vertical-align:sub;font-size:.8em">2</span>',
        "chart_title": "Q6 &middot; You'd adopt at…",
        "options": [
            {"value": "lt2",    "label": "Under €2",  "hint": "Instant yes"},
            {"value": "2to3",   "label": "€2 – €3",   "hint": "Likely"},
            {"value": "3to5",   "label": "€3 – €5",   "hint": "Niche use"},
            {"value": "5to8",   "label": "€5 – €8",   "hint": "Only with policy"},
            {"value": "gt8",    "label": "Over €8",   "hint": "Only mandated"},
            {"value": "not_us", "label": "Not us",         "hint": "Different molecule"},
        ],
        "short_labels": {
            "lt2": "< €2",
            "2to3": "€2–3",
            "3to5": "€3–5",
            "5to8": "€5–8",
            "gt8": "> €8",
            "not_us": "Not us",
        },
    },
]


# ─────────────────────────────────────────────────────────────────────────────
# Hook headlines — quirky reality-check framing, no ZEF claims.
# Rotate by URL: ?hook=A|B|C|D. Each `num` chunk renders in red.
# ─────────────────────────────────────────────────────────────────────────────
HOOK_HEADLINES: dict[str, list] = {
    "A": ["Hype", "or", "reality?", "Pick", "a", "side."],
    "B": ["Most", "predictions", "about", "green", "H₂", "are", "wrong.", "Yours", "included."],
    "C": [{"num": "Six"}, "questions.", "One", "chart.", "Where", "does", "the", "room", "actually", "stand?"],
    "D": ["Will", "green", "H₂", "cost", {"num": "€2"}, "or", {"num": "€10"}, "by", "2030?"],
}
DEFAULT_HOOK = "C"


# ─────────────────────────────────────────────────────────────────────────────
# ZEF target marker on the Q1 reveal chart. Framed as a goal, not a claim.
# Set to None to hide it.
# ─────────────────────────────────────────────────────────────────────────────
BENCHMARK = {
    "question_id": "q1",
    "kicker": "ZEF target",
    "value": "< €3",
    "unit": "/kg by 2030",
    "pill": "TARGET",
    "bucket": "2to3",
    "bucket_offset": 1.0,  # right edge of €2–3 bucket
}


# ─────────────────────────────────────────────────────────────────────────────
# Top / bottom copy
# ─────────────────────────────────────────────────────────────────────────────
SITE_TITLE = "ZEF — Hydrogen Reality Check"
WORDMARK = "ZEF"
HOOK_EYEBROW = "World Hydrogen Summit · Rotterdam · May 2026"
HOOK_SUB = "<b>Six questions.</b> One chart. See where you stand against the room."
HOOK_CTA = "Start the reality check"
HOOK_CTA_HINT = "60 sec →"
HOOK_SIG_LEFT = "Zero Emission Fuels"
HOOK_SIG_RIGHT = "SOLAR CHEMICALS · SIMPLIFIED"

LEAD_KICKER = "After the summit"
LEAD_HEADLINE = "Want the full benchmark after the summit?"
LEAD_SUB = "We'll send you the anonymized results once the poll closes."
LEAD_SUBMIT = "Send it to me"
LEAD_SUCCESS_TITLE = "On the list. See you in the inbox."
LEAD_SUCCESS_SUB = "We'll send the anonymized WHS 2026 results within 72h of the summit close."
LEAD_SIG_LEFT = "ZEF · Delft"
LEAD_SIG_RIGHT = "NO SPAM · UNSUBSCRIBE ANY TIME"

LEAD_ROLES = [
    {"value": "investor",  "label": "Investor"},
    {"value": "developer", "label": "Developer"},
    {"value": "offtaker",  "label": "Offtaker"},
    {"value": "policy",    "label": "Policy"},
    {"value": "other",     "label": "Other"},
]


# Show the fallback aggregate until the sheet has at least this many real submissions.
LIVE_THRESHOLD = 5


# Fallback aggregates shown until LIVE_THRESHOLD real submissions exist
# (also used if the sheet is unreachable). Values are shares (0..1) per option `value`.
# For multi-select q2, shares can sum to >1 because each respondent picks up to 3.
FALLBACK_AGGREGATE = {
    "total": 250,
    "q1": {"lt2": 0.05, "2to3": 0.20, "3to5": 0.40, "5to8": 0.25, "gt8": 0.10},
    "q2": {
        "power": 0.55,
        "electrolyzers": 0.50,
        "epc": 0.35,
        "certification": 0.30,
        "cost": 0.20,
        "demand": 0.20,
    },
    "q3": {"lt20": 0.15, "20to100": 0.30, "100to250": 0.30, "250to500": 0.15, "gt500": 0.10},
    "q4": {
        "methanol": 0.10,
        "ammonia": 0.30,
        "refinery": 0.15,
        "transport": 0.10,
        "emethane": 0.10,
        "esaf": 0.25,
    },
    "q5": {
        "africa": 0.18,
        "eu": 0.20,
        "asia": 0.30,
        "anz": 0.10,
        "northam": 0.14,
        "southam": 0.08,
    },
    "q6": {"lt2": 0.35, "2to3": 0.30, "3to5": 0.15, "5to8": 0.05, "gt8": 0.02, "not_us": 0.13},
}
