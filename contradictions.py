"""Step 1b - Find where the same company promised different things to different customers.

    python contradictions.py        # reads out/claims.json, writes out/contradictions.md + .json

For every commitment topic answered by 2+ customers:
  - CONFLICT       the promised values differ (e.g. 90-day vs 1-year log retention)
  - operating bar  the strictest promise: the level you must actually run at to keep them all
  - clock drift    same number, different trigger ("72h from confirmation" vs "24h from discovery")
  - hedge drift    firm to one customer, hedged ("typically") to another
  - reality check  if observed evidence exists, which customers' promises it breaks today
Also lists vague commitments (no measurable value) and roadmap promises with due dates.
"""
import json
from datetime import date
from pathlib import Path

import taxonomy as tx

ROOT = Path(__file__).parent
OUT = ROOT / "out"
TODAY = date.today()


def load():
    claims = json.loads((OUT / "claims.json").read_text())
    obs_file = ROOT / "evidence/observed_state.json"
    observed = json.loads(obs_file.read_text())["observed"] if obs_file.exists() else {}
    return claims, observed


def stricter_key(topic):
    return (lambda c: c["value"]) if tx.TOPICS[topic]["stricter"] == "lower" else (lambda c: -c["value"])


def meets(topic, actual, promised):
    return actual <= promised if tx.TOPICS[topic]["stricter"] == "lower" else actual >= promised


def analyse(claims, observed):
    commitments = [c for c in claims if c["kind"] == "commitment" and c["topic"]]
    topics = {}
    for c in commitments:
        topics.setdefault(c["topic"], []).append(c)

    findings, vague = [], []
    for topic, items in sorted(topics.items()):
        valued = [c for c in items if c["value"] is not None]
        vague += [c for c in items if c["value"] is None]
        if len(valued) < 2:
            continue
        spec = tx.TOPICS[topic]
        values = {c["value"] for c in valued}
        f = {"topic": topic, "promises": valued, "issues": [], "severity": None}

        if len(values) > 1:
            if spec["kind"] == "categorical":
                f["issues"].append("Different values promised")
                f["severity"] = "HIGH"
            else:
                ordered = sorted(valued, key=stricter_key(topic))
                strict, loose = ordered[0], ordered[-1]
                ratio = max(strict["value"], loose["value"]) / max(min(strict["value"], loose["value"]), 1)
                f["severity"] = "HIGH" if (ratio >= 2 or spec["kind"] == "scope") else "MEDIUM"
                f["operating_bar"] = strict
                f["issues"].append(f"Values differ: strictest is {strict['value_display']} ({strict['customer']}), "
                                   f"loosest is {loose['value_display']} ({loose['customer']})")

        clocks = {c["clock_start"] for c in valued if c["clock_start"]}
        if len(clocks) > 1:
            f["issues"].append("Clock starts at different events: " + ", ".join(
                f"{c['customer']} → {c['clock_start']}" for c in valued if c["clock_start"]))
            f["severity"] = f["severity"] or "MEDIUM"

        strengths = {c["strength"] for c in valued}
        if len(strengths) > 1:
            soft = [c["customer"] for c in valued if c["strength"] == "soft"]
            f["issues"].append(f"Hedged for {', '.join(soft)}, firm for the others")
            f["severity"] = f["severity"] or "LOW"

        if topic in observed and spec["kind"] != "categorical":
            o = observed[topic]
            broken = [c for c in valued if not meets(topic, o["value"], c["value"])]
            f["reality"] = {"observed": o, "broken_for": broken}
            if broken:
                f["severity"] = "HIGH"

        if f["issues"] or f.get("reality", {}).get("broken_for"):
            findings.append(f)

    roadmap = []
    for c in claims:
        if c["kind"] == "roadmap":
            status = "no date given"
            if c["due"]:
                status = "PAST DUE" if date.fromisoformat(c["due"]) < TODAY else f"due {c['due']}"
            roadmap.append({**c, "status": status})

    order = {"HIGH": 0, "MEDIUM": 1, "LOW": 2}
    findings.sort(key=lambda f: (order[f["severity"]], f["topic"]))
    return findings, vague, roadmap


def render(findings, vague, roadmap, n_claims):
    sev = {s: sum(f["severity"] == s for f in findings) for s in ("HIGH", "MEDIUM", "LOW")}
    broken_customers = sorted({c["customer"] for f in findings for c in f.get("reality", {}).get("broken_for", [])})
    L = ["# Trust Ledger: promise consistency report", "",
         f"Scanned {n_claims} questionnaire answers. Found **{len(findings)} inconsistent commitments** "
         f"({sev['HIGH']} high, {sev['MEDIUM']} medium, {sev['LOW']} low).", ""]
    if broken_customers:
        L += [f"**Promises the environment breaks today:** {', '.join(broken_customers)}", ""]

    for f in findings:
        L += [f"## [{f['severity']}] {f['topic'].replace('_', ' ')}", "",
              "| Customer | Promised | Wording | Source |", "|---|---|---|---|"]
        for c in f["promises"]:
            L.append(f"| {c['customer']} | {c['value_display']} | “{c['answer']}” | {c['source_file']} {c['ref']} |")
        L.append("")
        for i in f["issues"]:
            L.append(f"- {i}")
        if f.get("operating_bar"):
            b = f["operating_bar"]
            L.append(f"- **Operating bar:** you must operate at {b['value_display']} to keep every promise. "
                     f"Fall short and the {b['customer']} promise breaks first.")
        if f.get("reality"):
            r = f["reality"]
            if r["broken_for"]:
                who = ", ".join(f"{c['customer']} ({c['value_display']})" for c in r["broken_for"])
                L.append(f"- ❌ **Reality check:** environment does {r['observed']['display']} "
                         f"[{r['observed']['source']}]. Broken today for: {who}.")
            else:
                L.append(f"- ✅ Reality check: environment does {r['observed']['display']}; all promises met.")
        L.append("")

    if vague:
        L += ["## Vague commitments (promised, but not measurable)", ""]
        for c in vague:
            L.append(f"- {c['customer']}, {c['topic'].replace('_', ' ')}: “{c['answer']}” ({c['source_file']} {c['ref']})")
        L.append("")

    if roadmap:
        L += ["## Roadmap promises", "", "| Customer | Subject | Wording | Status |", "|---|---|---|---|"]
        for c in sorted(roadmap, key=lambda c: (c["status"] != "PAST DUE", c["customer"])):
            flag = "⚠️ **PAST DUE**" if c["status"] == "PAST DUE" else c["status"]
            L.append(f"| {c['customer']} | {c['topic']} | “{c['answer']}” | {flag} |")
        L.append("")
    return "\n".join(L)


def main():
    claims, observed = load()
    findings, vague, roadmap = analyse(claims, observed)
    report = render(findings, vague, roadmap, len(claims))
    (OUT / "contradictions.md").write_text(report)
    slim = lambda c: {k: c[k] for k in ("id", "customer", "answer", "value_display", "source_file", "ref")}
    (OUT / "contradictions.json").write_text(json.dumps([
        {"topic": f["topic"], "severity": f["severity"], "issues": f["issues"],
         "promises": [slim(c) for c in f["promises"]],
         "broken_for": [slim(c) for c in f.get("reality", {}).get("broken_for", [])]} for f in findings], indent=2))
    print(report)


if __name__ == "__main__":
    main()
