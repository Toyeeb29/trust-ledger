"""Step 2b - Propose which vendor CUECs each customer promise depends on, then record human approval.

    python map_cuecs.py propose                    # out/claims.json + out/cuecs.json -> out/mapping_review.csv
    # open the CSV, put Y/N in 'approved', your name in 'reviewer', edit 'rationale' if you disagree
    python map_cuecs.py apply out/mapping_review.csv   # approved rows -> data/mappings.approved.yaml

Links are proposed at topic level ("log retention" -> AWS log-group CUEC), not per customer: every customer
promise on that topic inherits the dependency. CUECs no promise depends on are listed as 'unmapped' -
you still owe them (they're part of your own vendor-management evidence), but no customer promise is
exposed if they slip.
"""
import csv
import json
import re
import sys
from datetime import date
from pathlib import Path

import yaml

import taxonomy as tx

ROOT = Path(__file__).parent
OUT = ROOT / "out"
APPROVED = ROOT / "data/mappings.approved.yaml"


def propose():
    claims = json.loads((OUT / "claims.json").read_text())
    reports = json.loads((OUT / "cuecs.json").read_text())
    cuecs = [c for r in reports for c in r["cuecs"]]
    topics = sorted({c["topic"] for c in claims if c["kind"] == "commitment" and c["topic"]})

    rows, used = [], set()
    for topic in topics:
        pat = tx.DEPENDS_ON.get(topic)
        if not pat:
            continue
        for c in cuecs:
            m = re.search(pat, c["text"], re.I)
            if not m:
                continue
            used.add(c["id"])
            conf = "high" if c["method"] == "section" else "medium"
            rows.append({
                "link_id": f"L{len(rows) + 1:03d}", "promise_topic": topic, "cuec_id": c["id"], "vendor": c["vendor"],
                "cuec_text": c["text"], "source": f"{c['report']} PDF p.{c['page']}", "matched_on": m.group(0),
                "confidence": conf, "approved": "", "reviewer": "",
                "rationale": f"Promises on {topic.replace('_', ' ')} hold for {c['vendor']} only if we meet this "
                             f"customer-side control (matched '{m.group(0)}').",
            })

    with open(OUT / "mapping_review.csv", "w", newline="") as fh:
        w = csv.DictWriter(fh, fieldnames=list(rows[0]) if rows else ["link_id"])
        w.writeheader(); w.writerows(rows)

    unmapped = [c for c in cuecs if c["id"] not in used]
    (OUT / "unmapped_cuecs.json").write_text(json.dumps(unmapped, indent=2))
    print(f"Proposed {len(rows)} promise->CUEC links across {len({r['promise_topic'] for r in rows})} topics "
          f"-> out/mapping_review.csv")
    print(f"{len(unmapped)} CUECs back no customer promise (still owed) -> out/unmapped_cuecs.json")
    for r in rows:
        print(f"  {r['link_id']} {r['promise_topic']:<24} <- {r['cuec_id']:<14} [{r['confidence']}] {r['cuec_text'][:70]}")


def apply(csv_path):
    with open(csv_path) as fh:
        rows = list(csv.DictReader(fh))
    decided = [r for r in rows if r["approved"].strip().upper() in ("Y", "N")]
    approved = [r for r in decided if r["approved"].strip().upper() == "Y"]
    missing_reviewer = [r["link_id"] for r in decided if not r["reviewer"].strip()]
    if missing_reviewer:
        sys.exit(f"Every decision needs a reviewer name: {', '.join(missing_reviewer)}")
    data = {"approved_on": date.today().isoformat(), "links": [
        {k: r[k] for k in ("promise_topic", "vendor", "cuec_text", "source", "reviewer", "rationale")} for r in approved],
        "rejected": [{k: r[k] for k in ("promise_topic", "vendor", "cuec_text", "reviewer")}
                     for r in decided if r not in approved]}
    APPROVED.write_text(yaml.safe_dump(data, sort_keys=False, width=120))
    print(f"{len(approved)} approved, {len(decided) - len(approved)} rejected, {len(rows) - len(decided)} undecided "
          f"-> {APPROVED.relative_to(ROOT)}")


if __name__ == "__main__":
    if len(sys.argv) >= 2 and sys.argv[1] == "propose":
        propose()
    elif len(sys.argv) == 3 and sys.argv[1] == "apply":
        apply(sys.argv[2])
    else:
        sys.exit(__doc__)
