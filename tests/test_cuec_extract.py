"""CUEC extraction and mapping against the two mock report layouts.

    python -m pytest tests/ -q
"""
import sys
from datetime import date
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
FIX = ROOT / "tests/fixtures"
sys.path.insert(0, str(ROOT))

import taxonomy as tx  # noqa: E402
from cuec_extract import extract  # noqa: E402

TODAY = date(2026, 10, 5)
SECTION = extract({"name": "Lumenvault"}, FIX / "mock_section_style.pdf", TODAY)
EMBEDDED = extract({"name": "Corvid Cloud"}, FIX / "mock_embedded_style.pdf", TODAY)


def test_section_style_finds_real_heading_not_toc():
    assert SECTION["method"] == "section"
    assert all(c["page"] == 5 for c in SECTION["cuecs"])  # TOC line on p.1 must be ignored


def test_section_style_exact_items_across_page_break():
    texts = [c["text"] for c in SECTION["cuecs"]]
    assert len(texts) == 5
    assert texts[0].startswith("Enforcing multi-factor") and texts[-1].startswith("Notifying Lumenvault")
    assert not any("assumption" in t or "Principal Service" in t or "Page " in t or "Proprietary" in t for t in texts)


def test_metadata_and_freshness():
    assert (SECTION["period_start"], SECTION["period_end"]) == ("2024-10-01", "2025-09-30")
    assert SECTION["freshness"] == "stale"
    assert EMBEDDED["freshness"] == "bridge letter needed"
    assert SECTION["trust_services_categories"] == ["Security", "Availability"]
    assert SECTION["subservice_orgs"] == ["Amazon Web Services", "Cloudflare"]


def test_embedded_style_falls_back_to_responsibility_sentences():
    assert EMBEDDED["method"] == "embedded"
    texts = [c["text"] for c in EMBEDDED["cuecs"]]
    assert len(texts) == 3
    assert not any("Corvid manages" in t for t in texts)  # vendor's own duty is not a CUEC
    assert all(c["confidence"] == "medium" for c in EMBEDDED["cuecs"])


def test_dependency_rules():
    import re
    hit = lambda topic, text: bool(re.search(tx.DEPENDS_ON[topic], text, re.I))
    assert hit("mfa_scope", "Enabling two-factor authentication for members")
    assert hit("access_revocation", "removing access for terminated personnel")
    assert hit("log_retention", "Customers must configure a retention period for their log groups")
    assert not hit("encryption_at_rest", "Enabling SAML for their Enterprise Cloud accounts")
