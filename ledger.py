"""Step 2c - The ledger: for every promise each customer holds, is the whole chain still provable?

    customer promise (questionnaire)  ->  vendor CUECs it depends on (approved links)
                                      ->  evidence for each CUEC (automated check) + is the vendor report current?
                                      ->  our own observed state vs the promised value

    python ledger.py      # writes out/ledger.md

Verdicts
  AT RISK    observed state breaks the promise, or a CUEC it depends on is failing
  UNPROVEN   nothing failing, but a link in the chain has no evidence or rests on an out-of-date vendor report
  SUPPORTED  every link has current, passing evidence
"""
import json
import re
from pathlib import Path

import yaml

import taxonomy as tx
from contradictions import meets

ROOT = Path(__file__).parent
OUT = ROOT / "out"
ICON = {"pass": "✅", "fail": "❌", "missing": "❔", "no check": "➖"}


def load():
    claims = json.loads((OUT / "claims.json").read_text())
    reports = {r["vendor"]: r for r in json.loads((OUT / "cuecs.json").read_text())}
    links = yaml.safe_load((ROOT / "data/mappings.approved.yaml").read_text()).get("links", [])
    rules = yaml.safe_load((ROOT / "data/cuec_checks.yaml").read_text())["checks"]
    results = json.loads((ROOT / "evidence/check_results.json").read_text())["results"]
    observed = json.loads((ROOT / "evidence/observed_state.json").read_text())["observed"]
    return claims, reports, links, rules, results, observed


def check_for(link, rules, results):
    for r in rules:
        if r["vendor"] == link["vendor"] and re.search(r["match"], link["cuec_text"], re.I):
            res = results.get(r["check"])
            return r["check"], (res["status"], res["detail"]) if res else ("missing", "no evidence collected")
    return None, ("no check", "no automated check defined for this CUEC")


def evaluate(claims, reports, links, rules, results, observed):
    rows = []
    for c in claims:
        if c["kind"] != "commitment" or not c["topic"]:
            continue
        deps = []
        for l in (l for l in links if l["promise_topic"] == c["topic"]):
            check, (status, detail) = check_for(l, rules, results)
            rep = reports.get(l["vendor"], {})
            deps.append({**l, "check": check, "status": status, "detail": detail,
                         "freshness": rep.get("freshness", "unknown"), "period_end": rep.get("period_end")})
        own = None
        if c["topic"] in observed and c["value"] is not None and tx.TOPICS[c["topic"]]["kind"] != "categorical":
            o = observed[c["topic"]]
            own = {**o, "ok": meets(c["topic"], o["value"], c["value"])}

        reasons = []
        if own and not own["ok"]:
            reasons.append(f"we actually do {own['display']}")
        reasons += [f"{d['vendor']} CUEC failing: {d['detail']}" for d in deps if d["status"] == "fail"]
        if reasons:
            verdict = "AT RISK"
        else:
            gaps = [f"{d['vendor']} CUEC has {'no evidence' if d['status'] in ('missing', 'no check') else d['status']}"
                    for d in deps if d["status"] != "pass"]
            gaps += [f"{d['vendor']} report is {d['freshness']} (period ended {d['period_end']})"
                     for d in deps if d["freshness"] in ("stale", "bridge letter needed")]
            if not deps and not own:
                gaps.append("no evidence of any kind is linked to this promise")
            reasons = sorted(set(gaps))
            verdict = "UNPROVEN" if gaps else "SUPPORTED"
        rows.append({**c, "deps": deps, "own": own, "verdict": verdict, "reasons": reasons})
    return rows


def render(rows, reports):
    customers = sorted({r["customer"] for r in rows})
    L = ["# Trust Ledger", "", "| Customer | Promises | ✅ Supported | ❌ At risk | ❔ Unproven |", "|---|---|---|---|---|"]
    for cust in customers:
        mine = [r for r in rows if r["customer"] == cust]
        n = lambda v: sum(r["verdict"] == v for r in mine)
        L.append(f"| {cust} | {len(mine)} | {n('SUPPORTED')} | {n('AT RISK')} | {n('UNPROVEN')} |")

    L += ["", "## Vendor reports relied on", "", "| Vendor | Report | Period end | Status | CUECs | Subservice orgs |",
          "|---|---|---|---|---|---|"]
    for r in reports.values():
        flag = {"stale": "⚠️ stale: request current report", "bridge letter needed": "⚠️ request bridge letter"}.get(
            r["freshness"], r["freshness"])
        L.append(f"| {r['vendor']} | {r['report']} | {r['period_end']} | {flag} | {len(r['cuecs'])} ({r['method']}) | "
                 f"{', '.join(r['subservice_orgs']) or '-'} |")

    for cust in customers:
        L += ["", f"## {cust}", ""]
        for r in sorted((r for r in rows if r["customer"] == cust), key=lambda r: ["AT RISK", "UNPROVEN", "SUPPORTED"].index(r["verdict"])):
            icon = {"AT RISK": "❌", "UNPROVEN": "❔", "SUPPORTED": "✅"}[r["verdict"]]
            L.append(f"**{icon} {r['verdict']}: {r['topic'].replace('_', ' ')}**: “{r['answer']}” "
                     f"<sub>({r['source_file']} {r['ref']})</sub>  ")
            if r["reasons"]:
                L.append(f"Why: {'; '.join(r['reasons'])}  ")
            if r["own"]:
                L.append(f"- {'✅' if r['own']['ok'] else '❌'} Our environment: {r['own']['display']} <sub>[{r['own']['source']}]</sub>")
            for d in r["deps"]:
                L.append(f"- {ICON[d['status']]} {d['vendor']} CUEC <sub>({d['source']})</sub>: {d['cuec_text']}  \n"
                         f"  ↳ {('`' + d['check'] + '`: ') if d['check'] else ''}{d['detail']}")
            L.append("")
    return "\n".join(L)


def main():
    data = load()
    rows = evaluate(*data)
    report = render(rows, data[1])
    (OUT / "ledger.md").write_text(report)
    (OUT / "ledger.json").write_text(json.dumps([{k: r[k] for k in ("id", "customer", "topic", "answer", "verdict", "reasons")}
                                                 for r in rows], indent=2))
    print(report)


if __name__ == "__main__":
    main()
