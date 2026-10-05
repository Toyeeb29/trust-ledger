"""Score the pipeline against the drift deliberately planted in the sample questionnaires.

    python -m pytest tests/ -q
"""
import json
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

import contradictions  # noqa: E402
import taxonomy as tx  # noqa: E402
from extract import classify_rules, read_rows  # noqa: E402

TRUTH = json.loads((ROOT / "samples/planted_truth.json").read_text())


def run_pipeline():
    files = sorted(str(p) for p in (ROOT / "samples").glob("*.xlsx"))
    subprocess.run([sys.executable, "extract.py", *files], cwd=ROOT, check=True, capture_output=True)
    claims, observed = contradictions.load()
    return claims, *contradictions.analyse(claims, observed)


CLAIMS, FINDINGS, VAGUE, ROADMAP = run_pipeline()
FOUND = {f["topic"]: f for f in FINDINGS}


def test_reads_all_three_layouts():
    for f in (ROOT / "samples").glob("*.xlsx"):
        rows = list(read_rows(f))
        assert len(rows) == 67, f.name
        assert all(r["answer"] for r in rows), f"empty answers in {f.name}"


def test_every_planted_contradiction_is_caught():
    missed = set(TRUTH["contradicting_topics"]) - set(FOUND)
    assert not missed, f"missed: {missed}"


def test_no_false_contradictions():
    for t in TRUTH["consistent_topics"]:
        assert t not in FOUND, f"false positive on {t}"


def test_clock_and_hedge_drift():
    for t in TRUTH["clock_start_mismatch"]:
        assert any("Clock starts" in i for i in FOUND[t]["issues"])
    for cust, t in TRUTH["hedged"]:
        assert any(c["customer"] == cust and c["strength"] == "soft" for c in FOUND[t]["promises"])


def test_vague_and_roadmap():
    assert {(c["customer"], c["topic"]) for c in VAGUE} == {tuple(x) for x in TRUTH["vague_commitments"]}
    got = {(c["customer"], c["topic"]) for c in ROADMAP}
    want = {(cust, subj) for cust, subj in TRUTH["roadmap_items"]}
    assert got == want
    past_due = {(c["customer"], c["topic"]) for c in ROADMAP if c["status"] == "PAST DUE"}
    assert past_due == {tuple(x) for x in TRUTH["past_due_roadmap"]}


def test_plain_attestations_are_not_commitments():
    for q, a in [("Is data encrypted in transit?", "Yes, TLS 1.2+."), ("Number of employees?", "85"),
                 ("Do you scan third-party dependencies?", "Yes")]:
        assert classify_rules(q, a)["kind"] == "attestation"


def test_duration_parsing_variants():
    cases = {"a minimum of one (1) year": 8760, "12 months": 8760, "within 72 hours": 72,
             "30 day retention": 720, "30 days' prior notice": 720}
    for text, hours in cases.items():
        assert tx.parse_value("duration", text)[0] == hours, text
