"""Regression checks on the public SOC 3 reports. Skipped unless they're downloaded into vendor_reports/.

Expected values were verified by hand against each PDF's CUEC page.
"""
import sys
from datetime import date
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))
from cuec_extract import extract  # noqa: E402

R = ROOT / "vendor_reports"
TODAY = date(2026, 10, 5)


def need(name):
    p = R / name
    if not p.exists():
        pytest.skip(f"{name} not downloaded")
    return p


def test_github_soc3_2023():
    r = extract({"name": "GitHub"}, need("github_soc3_2023.pdf"), TODAY)
    assert r["method"] == "section" and len(r["cuecs"]) == 4
    assert r["cuecs"][0]["text"] == "Enabling SAML for their Enterprise Cloud accounts."
    assert "two-factor" in r["cuecs"][1]["text"]
    assert "security-guides" in r["cuecs"][3]["text"]  # hyphenated URL re-joined across the line break
    assert (r["period_end"], r["freshness"]) == ("2023-09-30", "stale")


def test_pdl_soc3():
    r = extract({"name": "People Data Labs"}, need("pdl_soc3.pdf"), TODAY)
    assert r["method"] == "section" and len(r["cuecs"]) == 7
    assert r["trust_services_categories"] == ["Security"]
    assert all(c["text"].startswith("User entities are responsible for") for c in r["cuecs"])


def test_aws_soc3_embedded_without_marketing_noise():
    r = extract({"name": "AWS"}, need("aws_soc3.pdf"), TODAY)
    assert r["method"] == "embedded"
    assert not any("need to build" in c["text"] for c in r["cuecs"])
    assert r["freshness"] == "bridge letter needed"
