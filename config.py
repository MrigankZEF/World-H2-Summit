"""
ZEF Poll configuration — the single place to edit questions, copy, and branding.

Edit POLL_QUESTIONS to change questions, options, hints, or chart labels.
Edit HOOK_HEADLINES to change rotating hook lines.
Edit BENCHMARK to change the ZEF marker shown on the reveal chart.

Inline HTML is allowed in `headline` / `sub` (for H<sub>2</sub>, bold, etc.).
"""
from __future__ import annotations

from typing import TypedDict


class Option(TypedDict):
    value: str
    label: str
    hint: str


class ShortLabels(TypedDict, total=False):
    pass  # arbitrary value -> short label mapping per question


class Question(TypedDict, total=False):
    id: str              # stable key, used in URLs / sheet columns (e.g. "q1")
    number: str          # eyebrow display, e.g. "01"
    headline: str        # main question (inline HTML allowed)
    sub: str             # supporting copy (inline HTML allowed)
    chart_title: str     # short label for the reveal chart header
    options: list[Option]
    short_labels: dict[str, str]  # value -> short label for chart bars


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
            {"value": "2to3", "label": "€2 – €3", "hint": "The consensus"},
            {"value": "3to5", "label": "€3 – €5", "hint": "Cautious"},
            {"value": "gt5",  "label": "Over €5",   "hint": "Skeptical"},
        ],
        "short_labels": {
            "lt2": "< €2",
            "2to3": "€2–3",
            "3to5": "€3–5",
            "gt5": "> €5",
        },
    },
    {
        "id": "q2",
        "number": "02",
        "headline": "What's really blocking scale?",
        "sub": "Pick the one you'd name first",
        "chart_title": "Q2 &middot; Biggest blocker",
        "options": [
            {"value": "cost",          "label": "Cost",          "hint": "€/kg parity"},
            {"value": "power",         "label": "Power",         "hint": "Cheap renewables"},
            {"value": "electrolyzers", "label": "Electrolyzers", "hint": "Supply, CAPEX"},
            {"value": "permitting",    "label": "Permitting",    "hint": "Land, grid queues"},
            {"value": "demand",        "label": "Demand",        "hint": "Offtake signal"},
        ],
        "short_labels": {
            "cost": "Cost",
            "power": "Power",
            "electrolyzers": "Electrolyzers",
            "permitting": "Permitting",
            "demand": "Demand",
        },
    },
    {
        "id": "q3",
        "number": "03",
        "headline": "You'd seriously adopt at…",
        "sub": '<b>&euro; / kg</b> H<span style="vertical-align:sub;font-size:.8em">2</span>',
        "chart_title": "Q3 &middot; You'd adopt at…",
        "options": [
            {"value": "lt2",    "label": "Under €2",   "hint": "Instant yes"},
            {"value": "2to3",   "label": "€2 – €3", "hint": "Likely"},
            {"value": "3to5",   "label": "€3 – €5", "hint": "Niche use"},
            {"value": "gt5",    "label": "Over €5",    "hint": "Only mandated"},
            {"value": "not_us", "label": "Not us",          "hint": "Different molecule"},
        ],
        "short_labels": {
            "lt2": "< €2",
            "2to3": "€2–3",
            "3to5": "€3–5",
            "gt5": "> €5",
            "not_us": "Not us",
        },
    },
    {
        "id": "q4",
        "number": "04",
        "headline": "Pilot by 2030?",
        "sub": "On your roadmap, honestly",
        "chart_title": "Q4 &middot; Pilot by 2030?",
        "options": [
            {"value": "yes",   "label": "Yes",   "hint": "Board-ready"},
            {"value": "maybe", "label": "Maybe", "hint": "Watching"},
            {"value": "no",    "label": "No",    "hint": "Not this cycle"},
        ],
        "short_labels": {"yes": "Yes", "maybe": "Maybe", "no": "No"},
    },
]


# ─────────────────────────────────────────────────────────────────────────────
# Hook headlines (rotate by ?hook=A|B|C|D)
# Each entry is a list of strings or {"num": "..."} markers — `num` chunks
# render in red. Words animate in left-to-right.
# ─────────────────────────────────────────────────────────────────────────────
HOOK_HEADLINES: dict[str, list] = {
    "A": ["Green", "hydrogen", "at", {"num": "€1.50/kg."}, "No,", "really."],
    "B": ["The", "room", "says", {"num": "€4/kg."}, "We", "ship", {"num": "€1.80/kg."}],
    "C": ["Everyone", "says", "green", "H₂", "at", {"num": "€2/kg"}, "by", "2030.",
          "What", "if", "it's", "here", "now?"],
    "D": ["Your", "diesel", "costs", "more", "than", "our", "hydrogen."],
}
DEFAULT_HOOK = "B"


# ─────────────────────────────────────────────────────────────────────────────
# ZEF benchmark marker shown on the Q1 reveal chart.
# Set to None to hide it.
# `question_id` says which chart the marker attaches to.
# `bucket` is the option `value` it sits inside.
# `bucket_offset` (0..1) is where within that bucket bar the tick should land.
# ─────────────────────────────────────────────────────────────────────────────
BENCHMARK = {
    "question_id": "q1",
    "kicker": "ZEF · Spain 2030",
    "value": "€2.07",
    "unit": "/kg",
    "pill": "ACTUAL",
    "bucket": "2to3",
    "bucket_offset": 0.07,  # €2.07 sits 7% into the €2–3 bucket
}


# ─────────────────────────────────────────────────────────────────────────────
# Top / bottom copy
# ─────────────────────────────────────────────────────────────────────────────
SITE_TITLE = "ZEF — Settle the debate"
WORDMARK = "ZEF"
HOOK_EYEBROW = "World Hydrogen Summit · Rotterdam · May 2026"
HOOK_SUB = "A live pulse of the room. <b>Four questions.</b> One chart. The benchmark where ZEF actually ships."
HOOK_CTA = "Settle the debate"
HOOK_CTA_HINT = "30 sec →"
HOOK_SIG_LEFT = "Zero Emission Fuels"
HOOK_SIG_RIGHT = "SOLAR CHEMICALS · SIMPLIFIED"

LEAD_KICKER = "After the summit"
LEAD_HEADLINE = "Want the full benchmark after the summit?"
LEAD_SUB = "We'll send you the anonymized results + where ZEF lands in the data."
LEAD_SUBMIT = "Send it to me"
LEAD_SUCCESS_TITLE = "On the list. See you in the inbox."
LEAD_SUCCESS_SUB = "We'll send the anonymized WHS 2026 benchmark within 72h of the summit close."
LEAD_SIG_LEFT = "ZEF · Delft"
LEAD_SIG_RIGHT = "NO SPAM · UNSUBSCRIBE ANY TIME"

LEAD_ROLES = [
    {"value": "investor",  "label": "Investor"},
    {"value": "developer", "label": "Developer"},
    {"value": "offtaker",  "label": "Offtaker"},
    {"value": "policy",    "label": "Policy"},
    {"value": "other",     "label": "Other"},
]


# Fallback aggregates shown when no submissions exist yet (or sheet is unreachable).
# Values are shares (0..1) per option `value`.
FALLBACK_AGGREGATE = {
    "total": 0,
    "q1": {"lt2": 0.09, "2to3": 0.29, "3to5": 0.41, "gt5": 0.21},
    "q2": {"cost": 0.31, "power": 0.19, "electrolyzers": 0.12, "permitting": 0.24, "demand": 0.14},
    "q3": {"lt2": 0.44, "2to3": 0.33, "3to5": 0.14, "gt5": 0.03, "not_us": 0.06},
    "q4": {"yes": 0.38, "maybe": 0.47, "no": 0.15},
}
