"""Step 3 - Replace simulated evidence with live checks.

    export GITHUB_TOKEN=...            # classic PAT with admin:org, from an OWNER of the org
    python collect_evidence.py --github-org brightnote-demo

Checks (each maps to a vendor CUEC in data/cuec_checks.yaml):
  github_org_2fa_required   org setting "Require two-factor authentication" + members without 2FA
  github_saml_enforced      SAML SSO is an Enterprise Cloud feature; recorded as unavailable on other plans

Writes results into evidence/check_results.json (other checks are left as they are) and keeps the raw
API responses in evidence/raw/ so an auditor can re-perform the check.
The token is read from the environment only; it is never written to disk or logs.
"""
import argparse
import json
import os
import urllib.error
import urllib.request
from datetime import datetime, timezone
from pathlib import Path

ROOT = Path(__file__).parent
RESULTS = ROOT / "evidence/check_results.json"
RAW = ROOT / "evidence/raw"
API = "https://api.github.com"


def gh(path, token):
    req = urllib.request.Request(f"{API}{path}", headers={
        "Accept": "application/vnd.github+json", "X-GitHub-Api-Version": "2022-11-28",
        **({"Authorization": f"Bearer {token}"} if token else {})})
    try:
        with urllib.request.urlopen(req, timeout=20) as r:
            return r.status, json.loads(r.read() or b"null")
    except urllib.error.HTTPError as e:
        return e.code, json.loads(e.read() or b"null")


def check_github(org, token, call=gh):
    now = datetime.now(timezone.utc).isoformat(timespec="seconds")
    raw, results = {}, {}

    status, o = call(f"/orgs/{org}", token)
    raw["org"] = {"status": status, "two_factor_requirement_enabled": (o or {}).get("two_factor_requirement_enabled"),
                  "plan": ((o or {}).get("plan") or {}).get("name")}
    required = (o or {}).get("two_factor_requirement_enabled") if status == 200 else None

    status_m, members = call(f"/orgs/{org}/members?filter=2fa_disabled&per_page=100", token)
    no_2fa = len(members) if status_m == 200 and isinstance(members, list) else None
    raw["members_2fa_disabled"] = {"status": status_m, "count": no_2fa}  # logins deliberately not stored

    if required is None:
        results["github_org_2fa_required"] = {
            "status": "missing", "detail": f"Could not read org 2FA setting (HTTP {status}); token must belong to an org "
                                           f"owner and have admin:org", "collected_at": now, "source": "GitHub API"}
    elif required and no_2fa == 0:
        results["github_org_2fa_required"] = {"status": "pass", "detail": "Org requires 2FA; 0 members without 2FA",
                                              "collected_at": now, "source": "GitHub API"}
    else:
        parts = ["Org setting 'Require 2FA' is " + ("ON" if required else "OFF")]
        if no_2fa:
            parts.append(f"{no_2fa} member(s) without 2FA")
        results["github_org_2fa_required"] = {"status": "fail", "detail": "; ".join(parts),
                                              "collected_at": now, "source": "GitHub API"}

    plan = raw["org"]["plan"]
    results["github_saml_enforced"] = {
        "status": "missing", "collected_at": now, "source": "GitHub API",
        "detail": f"SAML SSO requires GitHub Enterprise Cloud; org plan is '{plan or 'unknown'}'"}
    return results, raw


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--github-org", required=True)
    args = ap.parse_args()
    token = os.environ.get("GITHUB_TOKEN")
    if not token:
        print("warning: GITHUB_TOKEN not set; the org 2FA setting is only visible to an authenticated owner")

    results, raw = check_github(args.github_org, token)
    current = json.loads(RESULTS.read_text())
    current["results"].update(results)
    current["collected_at"] = datetime.now(timezone.utc).isoformat(timespec="seconds")
    RESULTS.write_text(json.dumps(current, indent=2))

    RAW.mkdir(parents=True, exist_ok=True)
    stamp = datetime.now(timezone.utc).strftime("%Y%m%dT%H%M%SZ")
    (RAW / f"github_{args.github_org}_{stamp}.json").write_text(json.dumps(raw, indent=2))
    for k, v in results.items():
        print(f"  {k:<26} {v['status']:<8} {v['detail']}")


if __name__ == "__main__":
    main()
