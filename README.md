# Trust Ledger

**Find the security promises your company made to customers, catch where they contradict each other, and prove whether you're still keeping them.**

Security questionnaire answers become commitments the moment a deal closes. Different people answer them months apart, so the same company ends up telling one bank "logs kept 1 year" and a retailer "90 days", and nobody notices until a customer's auditor asks. Trust Ledger reads the questionnaires you already sent and turns them into a ledger of promises you can test.

```
questionnaires (.xlsx, any layout)
   └─ extract.py ─────────► every answer classified: commitment / roadmap / attestation / n/a
                             commitments normalised: topic, value, firm vs hedged, when the clock starts
                             └─ out/review_queue.csv   (a human approves each one)
   └─ contradictions.py ──► conflicts across customers, the "operating bar" you must meet,
                             reality check against observed evidence, vague + past-due promises
                             └─ out/contradictions.md
vendor SOC 2 / SOC 3 PDFs
   └─ cuec_extract.py ────► CUECs per vendor (dedicated section, or embedded "customers are responsible for…"),
                             report period, freshness (current / bridge letter needed / stale), subservice orgs
   └─ map_cuecs.py ───────► proposes promise topic → CUEC links with rationale → out/mapping_review.csv
                             human approves → data/mappings.approved.yaml
   └─ ledger.py ──────────► per customer, per promise: our observed state + every CUEC it rests on +
                             each CUEC's evidence + vendor report freshness → SUPPORTED / AT RISK / UNPROVEN
```

## Quick start
```bash
pip install openpyxl pyyaml pytest
python samples/gen_questionnaires.py     # 3 sample questionnaires, 201 answers, planted drift
python extract.py samples/*.xlsx         # -> out/claims.json, out/review_queue.csv
python contradictions.py                 # -> out/contradictions.md
python -m pytest tests/ -q               # scores the pipeline against the planted drift

# step 2: download the reports listed in data/vendors.yaml into vendor_reports/, then
python cuec_extract.py                   # -> out/cuecs.json
python map_cuecs.py propose              # -> out/mapping_review.csv  (fill in approved + reviewer)
python map_cuecs.py apply out/mapping_review.csv
python ledger.py                         # -> out/ledger.md
```

## What it catches (sample run)
- **10 inconsistent commitments across 3 customers**, for example breach notification promised at 24h from *discovery* to a health customer but 72h from *confirmation* to a bank.
- **Operating bar per topic**: the strictest promise is the level you actually have to run at.
- **Promises broken today**: 90-day CloudTrail retention breaks the 1-year promise made to two customers.
- **Clock drift and hedge drift**: same number, different trigger event; firm to one customer, "typically" to another.
- **Vague commitments** with nothing measurable, and **roadmap promises** with due dates (one already past due).

## Design choices
- **Layout-agnostic reading.** It finds the questionnaire sheet and header row itself and merges Yes/No columns with free-text notes (SIG Lite, CAIQ and home-grown formats in the samples).
- **Deterministic by default.** Rule-based classification is offline, reproducible and explainable to an auditor. `--llm` adds Claude classification for messier wording, but numeric values are still parsed by code, never trusted from model output.
- **Human in the loop.** Nothing becomes a tracked promise until someone approves it in `review_queue.csv`.
- **Commitment vs attestation.** "Yes, TLS 1.2+" is a current-state claim. "Critical vulns patched within 7 days" is an obligation that can quietly break. They're tracked differently.

## Limits (honest)
- The sample questionnaires are generated, and the tests check that the pipeline catches what was planted in them. Real questionnaires will use wording the rules miss; that's what the `--llm` path and the review queue are for.
- `--llm` has not been exercised in the sample run (no API key in the build environment).
- Observed evidence in `evidence/` is simulated until step 3 wires up real checks.

## Roadmap
1. ✅ Questionnaire extraction + cross-customer contradiction detection
2. ✅ Extract CUECs from vendor SOC reports, map promises → CUECs with approved rationale, per-customer ledger
3. Real evidence: GitHub org 2FA, CloudTrail retention, Okta deprovisioning
4. Drift history, owner alerts, customer-notification decision memo for AT RISK promises

*All companies and data are fictional.*
