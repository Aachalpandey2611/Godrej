"""
Domain classifier — gates every user message before it reaches Claude.

Strategy (two layers):
  1. Keyword blocklist: instantly reject obviously off-topic queries
     (coding, sports, finance, etc.) with zero API cost.
  2. Allow-list heuristic: if the message contains at least one medical
     keyword/phrase, pass it through directly.
  3. Ambiguous queries fall through to Claude itself — the strict system
     prompt handles them at the LLM level (no extra API call needed).
"""

import re

# ── Off-topic blocklist ────────────────────────────────────────────────────────
# Patterns that clearly signal a non-medical query.
_BLOCKLIST_PATTERNS: list[re.Pattern] = [
    re.compile(r"\b(python|javascript|typescript|java|golang|rust|c\+\+|c#|php|ruby|swift|kotlin)\b", re.I),
    re.compile(r"\b(algorithm|data structure|linked list|binary tree|sorting|leetcode|dsa|recursion|dynamic programming)\b", re.I),
    re.compile(r"\b(coding|programming|software|debug|compile|runtime error|stack overflow|github|git)\b", re.I),
    re.compile(r"\b(stock market|cryptocurrency|bitcoin|forex|trading|investment|finance|tax|economy)\b", re.I),
    re.compile(r"\b(football|cricket|basketball|soccer|tennis|olympic|sport|athlete|stadium)\b", re.I),
    re.compile(r"\b(movie|series|netflix|song|music|celebrity|actor|actress|oscar|grammy)\b", re.I),
    re.compile(r"\b(recipe|cooking|ingredient|cuisine|restaurant|food review)\b", re.I),
    re.compile(r"\b(history of world|geography|capital city|flag of|country trivia)\b", re.I),
]

# ── Medical allow-list ─────────────────────────────────────────────────────────
# Presence of any of these strongly signals a medical query.
_MEDICAL_PATTERNS: list[re.Pattern] = [
    re.compile(r"\b(symptom|diagnosis|diagnose|treatment|medication|medicine|drug|dosage|prescription)\b", re.I),
    re.compile(r"\b(disease|disorder|condition|syndrome|infection|virus|bacteria|pathogen)\b", re.I),
    re.compile(r"\b(doctor|physician|surgeon|nurse|hospital|clinic|emergency|patient)\b", re.I),
    re.compile(r"\b(anatomy|organ|tissue|cell|blood|heart|lung|liver|kidney|brain|nerve|muscle|bone)\b", re.I),
    re.compile(r"\b(pain|fever|nausea|fatigue|cough|rash|swelling|inflammation|bleeding|fracture)\b", re.I),
    re.compile(r"\b(cancer|tumor|diabetes|hypertension|asthma|allergy|arthritis|depression|anxiety|covid|hiv|aids)\b", re.I),
    re.compile(r"\b(vaccine|immunization|antibiotic|antiviral|steroid|insulin|chemotherapy|surgery|therapy)\b", re.I),
    re.compile(r"\b(pregnant|pregnancy|childbirth|menstrual|fertility|contraception)\b", re.I),
    re.compile(r"\b(mental health|psychiatry|psychology|ptsd|bipolar|schizophrenia|ocd)\b", re.I),
    re.compile(r"\b(nutrition|vitamin|mineral|supplement|calorie|bmi|obesity|diet)\b", re.I),
    re.compile(r"\b(first aid|cpr|wound|burn|fracture|sprain|emergency care)\b", re.I),
]

# ── Refusal message ────────────────────────────────────────────────────────────
OUT_OF_SCOPE_REPLY = (
    "I'm MedBot, a medical information assistant. I can only help with "
    "health and medicine-related questions — things like symptoms, conditions, "
    "medications, treatments, or anatomy. Your question seems to be outside "
    "that scope. Please feel free to ask something medical!"
)


def is_medical_query(text: str) -> tuple[bool, str | None]:
    """
    Returns (is_medical, refusal_message).

    - (True, None)        → pass the query to Claude
    - (False, str)        → reject immediately with the returned message
    """
    # Layer 1: hard reject on blocklist hit
    for pattern in _BLOCKLIST_PATTERNS:
        if pattern.search(text):
            return False, OUT_OF_SCOPE_REPLY

    # Layer 2: fast approve on medical keyword hit
    for pattern in _MEDICAL_PATTERNS:
        if pattern.search(text):
            return True, None

    # Layer 3: ambiguous — let Claude's system prompt decide
    # (returning True lets the message reach Claude with its strict prompt)
    return True, None
