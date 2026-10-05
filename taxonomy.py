"""Commitment topics, how to recognise them, and how to parse/compare their values.

Each topic says:
  match      keyword groups that must ALL appear in the question (each group = any-of)
  kind       duration | frequency | scope | categorical
  stricter   'lower' or 'higher' value is the stricter promise (duration/frequency/scope)
"""
import re

TOPICS = {
    # order matters: first match wins
    "data_deletion":             {"match": [["delet", "purge"], ["terminat"]], "kind": "duration", "stricter": "lower"},
    "access_revocation":         {"match": [["terminat"], ["access"]], "kind": "duration", "stricter": "lower"},
    "log_retention":             {"match": [["log"], ["retention", "retain"]], "kind": "duration", "stricter": "higher"},
    "backup_retention":          {"match": [["backup"], ["retention", "retain"]], "kind": "duration", "stricter": "higher"},
    "breach_notification":       {"match": [["notif"], ["incident", "breach"]], "kind": "duration", "stricter": "lower"},
    "subprocessor_notice":       {"match": [["subprocessor"], ["notif"]], "kind": "duration", "stricter": "higher"},
    "vuln_remediation_critical": {"match": [["critical"], ["vulnerab"]], "kind": "duration", "stricter": "lower"},
    "rto":                       {"match": [["rto", "recovery time"]], "kind": "duration", "stricter": "lower"},
    "mfa_scope":                 {"match": [["multi-factor", "mfa"]], "kind": "scope", "stricter": "higher"},
    "pentest_frequency":         {"match": [["penetration"]], "kind": "frequency", "stricter": "higher"},
    "access_review_frequency":   {"match": [["access review"]], "kind": "frequency", "stricter": "higher"},
    "security_training":         {"match": [["training"]], "kind": "frequency", "stricter": "higher"},
    "encryption_at_rest":        {"match": [["encrypt"], ["at rest"]], "kind": "categorical", "stricter": None},
}


def match_topic(question):
    q = question.lower()
    for name, spec in TOPICS.items():
        if all(any(k in q for k in group) for group in spec["match"]):
            return name
    return None


# ---- value parsers ---------------------------------------------------------------------------
WORDNUM = {"one": 1, "two": 2, "three": 3, "four": 4, "five": 5, "six": 6, "seven": 7,
           "ten": 10, "twelve": 12, "fourteen": 14, "thirty": 30, "ninety": 90}
UNIT_HOURS = {"hour": 1, "day": 24, "week": 168, "month": 730, "year": 8760}
DURATION_RE = re.compile(r"\b(\d+|" + "|".join(WORDNUM) + r")\s*(?:\(\d+\)\s*)?[- ]?(hour|day|week|month|year)s?\b", re.I)

FREQ = [(r"\bdaily\b", 365), (r"\bweekly\b", 52), (r"\bmonthly\b", 12), (r"\bquarterly\b", 4),
        (r"\btwice a year\b|\bsemi-?annual(ly)?\b|\bbi-?annual(ly)?\b", 2), (r"\bannual(ly)?\b|\byearly\b", 1)]

SCOPE = [(r"\ball (workforce|users|accounts|employees|personnel)\b", 3, "all workforce accounts"),
         (r"\bproduction\b", 2, "admin + production access"),
         (r"\badmin(istrator|istrative)?\b", 1, "administrator accounts only")]


def human_hours(h):
    for unit, size in (("year", 8760), ("month", 730), ("day", 24)):
        if h >= size and h % size == 0:
            n = h // size
            return f"{n} {unit}{'s' if n != 1 else ''}"
    return f"{h} hour{'s' if h != 1 else ''}"


def parse_value(kind, text):
    """Return (numeric_value, display) or (None, None)."""
    t = text.lower()
    if kind == "duration":
        m = DURATION_RE.search(t)
        if not m:
            return None, None
        n = int(m.group(1)) if m.group(1).isdigit() else WORDNUM[m.group(1).lower()]
        unit = m.group(2).lower()
        # compare in hours, but display the promise in the unit the customer actually read
        return n * UNIT_HOURS[unit], f"{n} {unit}{'s' if n != 1 else ''}"
    if kind == "frequency":
        for pat, per_year in FREQ:
            if re.search(pat, t):
                label = {365: "daily", 52: "weekly", 12: "monthly", 4: "quarterly", 2: "twice a year", 1: "annually"}[per_year]
                return per_year, label
        return None, None
    if kind == "scope":
        for pat, rank, label in SCOPE:
            if re.search(pat, t):
                return rank, label
        return None, None
    if kind == "categorical":
        m = re.search(r"aes-?\s?(128|256)", t)
        return (f"AES-{m.group(1)}", f"AES-{m.group(1)}") if m else (None, None)
    return None, None


# ---- wording signals -------------------------------------------------------------------------
HEDGE_RE = re.compile(r"\b(typically|generally|usually|target|aim|best[- ]effort|approximately|where possible)\b", re.I)
ROADMAP_RE = re.compile(r"\b(planned|planning|plan to|on (our|the) roadmap|expected|in progress|will be implemented|"
                        r"by end of)\b|\bQ[1-4]\s*20\d\d\b", re.I)
NA_VALUES = {"n/a", "na", "not applicable", "-"}


# ---- promise -> CUEC dependency rules ---------------------------------------------------------
# A promise topic depends on a vendor CUEC when the CUEC text matches the topic's pattern.
# Topics absent here (pentest frequency, training, subprocessor notice) don't rest on vendor CUECs.
DEPENDS_ON = {
    "mfa_scope":                 r"two-factor|multi-factor|\b2fa\b|\bmfa\b|\bsaml\b|single sign-on",
    "access_revocation":         r"terminat|deprovision|remov\w* access|revok",
    "access_review_frequency":   r"permission|least privilege|supervision|review\w* (?:user )?access",
    "encryption_at_rest":        r"encrypt",
    "log_retention":             r"\blogs?\b[^.]*\bretain|retention period|\blog groups?\b",
    "rto":                       r"disaster recovery|business continuity|failover",
    "backup_retention":          r"\bbackups?\b|disaster recovery",
    "vuln_remediation_critical": r"\bpatch|vulnerab",
    "data_deletion":             r"\bdelet|\bwipe",
}


def clock_start(text):
    t = text.lower()
    for pat, label in ((r"confirm", "confirmation"), (r"discover|become aware|identif", "discovery"),
                       (r"last day", "last working day"), (r"terminat", "termination")):
        if re.search(pat, t):
            return label
    return None
