"""Live-check logic with the GitHub API stubbed out (no token or network needed)."""
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from collect_evidence import check_github  # noqa: E402


def fake(org_status=200, required=False, members=(), plan="free"):
    def call(path, token):
        if "/members" in path:
            return (200 if org_status == 200 else org_status), list(members)
        return org_status, {"two_factor_requirement_enabled": required, "plan": {"name": plan}}
    return call


def test_pass_when_required_and_everyone_enrolled():
    r, raw = check_github("o", "t", fake(required=True))
    assert r["github_org_2fa_required"]["status"] == "pass"


def test_fail_when_setting_off():
    r, _ = check_github("o", "t", fake(required=False))
    assert r["github_org_2fa_required"]["status"] == "fail"
    assert "OFF" in r["github_org_2fa_required"]["detail"]


def test_fail_when_members_lack_2fa_even_if_required():
    r, raw = check_github("o", "t", fake(required=True, members=[{"login": "a"}, {"login": "b"}]))
    assert r["github_org_2fa_required"]["status"] == "fail" and "2 member" in r["github_org_2fa_required"]["detail"]
    assert "login" not in str(raw)  # raw evidence keeps counts, not usernames


def test_missing_without_owner_access():
    r, _ = check_github("o", None, fake(org_status=403, required=None))
    assert r["github_org_2fa_required"]["status"] == "missing"


def test_saml_recorded_as_unavailable_off_enterprise():
    r, _ = check_github("o", "t", fake(required=True))
    assert r["github_saml_enforced"]["status"] == "missing" and "Enterprise Cloud" in r["github_saml_enforced"]["detail"]
