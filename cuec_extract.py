"""Step 2a - Pull CUECs (what a vendor's SOC report says YOU must do) out of SOC 2 / SOC 3 PDFs.

    python cuec_extract.py                      # reads data/vendors.yaml, writes out/cuecs.json
    python cuec_extract.py --manifest tests/fixtures/vendors.yaml --out out/cuecs_mock.json

Two strategies, because real reports come in two shapes:
  section   a dedicated "Complementary User Entity Controls" section (GitHub, most SaaS SOC 2s)
            -> find the real heading (not the table-of-contents line), read until the next heading,
               strip running headers/footers, split into items even across page breaks
  embedded  no CUEC section; duties buried in service descriptions (AWS-style)
            -> collect "customers are responsible for..." sentences, lower confidence, flagged for review

Also captures report period, freshness (current / bridge-letter gap / stale), and subservice orgs.
Report PDFs stay local (vendor_reports/ is gitignored): most SOC reports are licensed, not redistributable.
"""
import argparse
import json
import re
from collections import Counter
from datetime import date
from pathlib import Path

import pdfplumber
import yaml

ROOT = Path(__file__).parent

HEADING_RE = re.compile(r"^(?:section\s+[ivx]+[:.]?\s*|[a-z]\.\s+|\d+(?:\.\d+)*\.?\s+)?"
                        r"(complementary user entity controls?|user entity (?:control )?(?:responsibilities|considerations))\s*:?$",
                        re.I)
TOC_RE = re.compile(r"(\.{4,}|…{2,})\s*\d+\s*$|\s\d{1,3}$")
NEXT_HEADING_RE = re.compile(
    r"^(?:section\s+[ivx]+[:.]|[A-Z]\.\s+[A-Z]|\d+(?:\.\d+)*\.?\s+[A-Z][A-Za-z ]{3,60}$|"
    r"complementary subservice|principal service commitments|subservice organizations?$|"
    r"trust services criteria|system incidents|changes to the system)", re.I)
ITEM_START_RE = re.compile(r"^(?:[•●▪◦\-–·]\s*|\(?\d{1,2}[.)]\s+|\d{1,2}\s+(?=[A-Z])|\(?[a-z][.)]\s+)")
INTRO_RE = re.compile(r"assum|listed below|following|responsible for the following|designed with|:\s*$", re.I)
# deliberately narrow: "customers need to build..." is marketing copy, not an obligation
EMBEDDED_RE = re.compile(r"\b(customers?|user entities|users)\s+(?:are|is)\s+responsible\s+for\b|"
                         r"\bcustomers?\s+must\b|\b(it is|is) the customer'?s responsibility\b", re.I)
PERIOD_RE = re.compile(r"period\s+(?:from\s+)?([A-Z][a-z]+\s+\d{1,2},\s+\d{4})\s+(?:to|through|and ending)\s+"
                       r"([A-Z][a-z]+\s+\d{1,2},\s+\d{4})")
KNOWN_SUBSERVICE = ["Amazon Web Services", "AWS", "Microsoft Azure", "Azure", "Google Cloud", "GCP", "Equinix",
                    "CoreSite", "QTS", "Sabey", "Cloudflare", "Rackspace", "Snowflake", "Digital Realty", "Heroku",
                    "Salesforce", "Okta", "Twilio", "Stripe", "MongoDB"]
TSC = ["security", "availability", "confidentiality", "processing integrity", "privacy"]


# ---- page text with running headers/footers removed -------------------------------------------
def read_pages(path):
    with pdfplumber.open(path) as pdf:
        pages = [(p.extract_text() or "").splitlines() for p in pdf.pages]
    norm = lambda s: re.sub(r"\d+", "#", s.strip().lower())
    counts = Counter(norm(l) for lines in pages for l in set(lines) if l.strip())
    repeated = {k for k, v in counts.items() if len(pages) >= 3 and v >= 0.5 * len(pages)}
    clean = []
    for lines in pages:
        clean.append([l.strip() for l in lines
                      if l.strip() and norm(l) not in repeated and not re.fullmatch(r"(page\s*)?\d+(\s*of\s*\d+)?", l.strip(), re.I)])
    return clean


# ---- metadata ---------------------------------------------------------------------------------
def report_meta(pages, today):
    head = "\n".join(" ".join(p) for p in pages[:8])
    meta = {"period_start": None, "period_end": None, "freshness": "unknown", "months_since_period_end": None}
    m = PERIOD_RE.search(head)
    if m:
        from datetime import datetime
        start, end = (datetime.strptime(x.replace("  ", " "), "%B %d, %Y").date() for x in m.groups())
        months = (today.year - end.year) * 12 + today.month - end.month
        meta.update(period_start=start.isoformat(), period_end=end.isoformat(), months_since_period_end=months,
                    freshness="current" if months <= 3 else "bridge letter needed" if months <= 12 else "stale")
    low = head.lower()
    # the first "relevant to ..." phrase that names a category is the report's scope statement
    cats = None
    for m in re.finditer(r"relevant to(.{0,110})", low, re.S):
        window = m.group(1).split(" were ")[0]
        hit = [t.title() for t in TSC if t in window]
        if hit:
            cats = hit
            break
    meta["trust_services_categories"] = cats
    full = "\n".join(" ".join(p) for p in pages)
    sub_ctx = " ".join(re.findall(r"[^.]*subservice[^.]*\.", full, re.I)) + " ".join(
        re.findall(r"[^.]*(?:carved out|carve-out)[^.]*\.", full, re.I))
    alias = {"AWS": "Amazon Web Services", "Azure": "Microsoft Azure", "GCP": "Google Cloud"}
    found = []
    for name in KNOWN_SUBSERVICE:
        canon = alias.get(name, name)
        if re.search(rf"\b{re.escape(name)}\b", sub_ctx) and canon not in found:
            found.append(canon)
    meta["subservice_orgs"] = found
    return meta


# ---- strategy 1: dedicated section ------------------------------------------------------------
def find_section(pages):
    for p_idx, lines in enumerate(pages):
        for l_idx, line in enumerate(lines):
            if HEADING_RE.match(line) and not TOC_RE.search(line):
                return p_idx, l_idx
    return None


def section_lines(pages, start):
    p_idx, l_idx = start
    out = []
    for pi in range(p_idx, len(pages)):
        lines = pages[pi][l_idx + 1:] if pi == p_idx else pages[pi]
        for line in lines:
            if NEXT_HEADING_RE.match(line) and out:
                return out
            out.append((pi + 1, line))
        if pi - p_idx > 4:  # a CUEC list never runs this long; stop runaway reads
            break
    return out


def split_items(lines):
    items, cur, cur_page = [], [], None
    for page, line in lines:
        if HEADING_RE.match(line):  # a table caption repeating the section title
            continue
        if cur and cur[-1].endswith("-") and line[:1].islower():
            cur[-1] = cur[-1] + line
            continue
        starts_new = ITEM_START_RE.match(line) or (cur and cur[-1].rstrip().endswith((".", ":", ";")) and line[:1].isupper())
        if starts_new and cur:
            items.append((cur_page, " ".join(cur)))
            cur = []
        if not cur:
            cur_page = page
        cur.append(ITEM_START_RE.sub("", line).strip() if not cur else line)
    if cur:
        items.append((cur_page, " ".join(cur)))
    cleaned = []
    for page, text in items:
        text = re.sub(r"\s+", " ", text).strip(" ;")
        if len(text) < 15 or (INTRO_RE.search(text) and "responsible for" not in text.lower()[:40]):
            continue
        if INTRO_RE.search(text) and text.endswith(":"):
            continue
        cleaned.append((page, text))
    return cleaned


# ---- strategy 2: embedded responsibilities ----------------------------------------------------
def embedded(pages):
    seen, out = set(), []
    for p_no, lines in enumerate(pages, 1):
        text = re.sub(r"\s+", " ", " ".join(lines))
        for sent in re.split(r"(?<=[.;])\s+(?=[A-Z])", text):
            if EMBEDDED_RE.search(sent):
                key = sent.lower()[:80]
                if key not in seen:
                    seen.add(key); out.append((p_no, sent.strip()))
    return out


# ---- driver -----------------------------------------------------------------------------------
def extract(vendor, path, today):
    pages = read_pages(path)
    meta = report_meta(pages, today)
    start = find_section(pages)
    if start:
        found, method, confidence = split_items(section_lines(pages, start)), "section", "high"
    else:
        found, method, confidence = embedded(pages), "embedded", "medium"
    slug = re.sub(r"[^A-Z0-9]", "", vendor["name"].upper())[:10]
    cuecs = [{"id": f"{slug}-{i:02d}", "vendor": vendor["name"], "text": t, "page": p, "method": method,
              "confidence": confidence, "report": Path(path).name} for i, (p, t) in enumerate(found, 1)]
    return {"vendor": vendor["name"], "report": Path(path).name, "url": vendor.get("url"),
            "our_usage": vendor.get("our_usage"), "pages": len(pages), "method": method, **meta,
            "cuecs": cuecs}


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--manifest", default=str(ROOT / "data/vendors.yaml"))
    ap.add_argument("--out", default=str(ROOT / "out/cuecs.json"))
    ap.add_argument("--today", default=date.today().isoformat())
    args = ap.parse_args()

    manifest_path = Path(args.manifest)
    vendors = yaml.safe_load(manifest_path.read_text())["vendors"]
    today = date.fromisoformat(args.today)
    results = []
    for v in vendors:
        path = (manifest_path.parent / v["file"]).resolve()
        if not path.exists():
            print(f"  skip {v['name']}: {v['file']} not found (download it from {v.get('url', 'the vendor trust center')})")
            continue
        r = extract(v, path, today)
        results.append(r)
        print(f"  {r['vendor']:<18} {r['method']:<9} {len(r['cuecs']):>2} CUECs  "
              f"period ends {r['period_end']}  -> {r['freshness']}  subservice: {', '.join(r['subservice_orgs']) or '-'}")
    Path(args.out).parent.mkdir(exist_ok=True, parents=True)
    Path(args.out).write_text(json.dumps(results, indent=2))
    print(f"wrote {args.out}")


if __name__ == "__main__":
    main()
