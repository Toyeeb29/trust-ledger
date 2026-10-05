"""Generate three realistic, completed customer security questionnaires for the fictional vendor Brightnote.

Each customer uses a different layout (SIG Lite-style, CAIQ-style, custom), and the answers drift
between customers the way real answers do when different people fill them in months apart.
Planted drift is recorded in planted_truth.json so the extractor can be scored against it.
"""
import json
import random
from pathlib import Path

from openpyxl import Workbook
from openpyxl.styles import Alignment, Font, PatternFill

OUT = Path(__file__).parent
random.seed(7)

# --- Commitment-bearing topics: (domain, question wording, {customer: answer}) -----------------
N, C, F = "Northwind Bank", "Contoso Health", "Fabrikam Retail"

COMMITMENTS = [
    ("Logging", "What is the retention period for security audit logs?",
     {N: "Security audit logs are retained for a minimum of one (1) year.",
      C: "Logs are retained for 12 months in immutable storage.",
      F: "We retain logs for 90 days."}),
    ("Incident Response", "What is your timeframe for notifying customers of a security incident affecting their data?",
     {N: "We will notify affected customers within 72 hours of confirming a security incident.",
      C: "Customers are notified within 24 hours of discovery of a breach involving PHI.",
      F: "Notification occurs without undue delay, typically within 72 hours."}),
    ("Access Control", "How quickly is system access removed when an employee is terminated?",
     {N: "Access is revoked within 24 hours of termination.",
      C: "Access is revoked within 24 hours of the employee's last day.",
      F: "Access removal is completed within 48 hours."}),
    ("Access Control", "Is multi-factor authentication enforced? Describe the scope.",
     {N: "Yes. MFA is enforced for all administrative and production access.",
      C: "Yes. MFA is required for all workforce accounts.",
      F: "Yes, MFA is enabled for administrator accounts."}),
    ("Data Protection", "Is customer data encrypted at rest? Specify the algorithm.",
     {N: "All customer data is encrypted at rest using AES-256.",
      C: "Yes - AES-256 via AWS KMS.",
      F: "Yes, data at rest is encrypted with AES-256."}),
    ("Vulnerability Management", "How often are independent penetration tests performed?",
     {N: "Third-party penetration tests are performed annually.",
      C: "Penetration testing is performed twice a year by an independent firm.",
      F: "Annual penetration test by a third party."}),
    ("Vulnerability Management", "What is your remediation SLA for critical vulnerabilities?",
     {N: "Critical vulnerabilities are remediated within 15 days.",
      C: "Critical vulnerabilities are patched within 7 days of identification.",
      F: "Critical: 30 days."}),
    ("Business Continuity", "Describe backup frequency and retention.",
     {N: "Backups are performed daily and retained for 35 days.",
      C: "Daily backups, retained for 35 days.",
      F: "Daily backups with 30 day retention."}),
    ("Business Continuity", "What is your Recovery Time Objective (RTO)?",
     {N: "Our RTO is 4 hours.",
      C: "RTO is 8 hours for the production platform.",
      F: "We target an RTO of 24 hours."}),
    ("Access Control", "How frequently are user access reviews performed?",
     {N: "User access reviews are performed quarterly.",
      C: "Access is reviewed quarterly by system owners.",
      F: "Access reviews are performed annually."}),
    ("Human Resources", "How often do employees complete security awareness training?",
     {N: "All employees complete security awareness training upon hire and annually thereafter.",
      C: "Training is completed at hire and annually.",
      F: "Upon hire and annually."}),
    ("Data Protection", "How long after contract termination is customer data deleted?",
     {N: "Customer data is deleted within 30 days of contract termination.",
      C: "Data is deleted within 30 days of termination and a certificate of destruction is provided.",
      F: "Customer data is purged within 90 days of termination."}),
    ("Third Party", "Do you notify customers before engaging new subprocessors?",
     {N: "Yes. We provide 30 days' prior notice of new subprocessors.",
      C: "Yes, we notify customers of new subprocessors.",
      F: "N/A"}),
]

ROADMAP = [
    ("Compliance", "Do you hold a current SOC 2 Type II report?",
     {N: "SOC 2 Type I issued; Type II report expected Q1 2027.",
      C: "Type I available under NDA. Type II expected Q1 2027.",
      F: "Type I available."}),
    ("Logging", "Do you operate a SIEM with 24x7 monitoring?",
     {N: "Centralized logging in place; 24x7 monitoring via MDR provider.",
      C: "We are planning to implement a SIEM by end of 2026.",
      F: "Centralized logging in place."}),
    ("Data Protection", "Do you use data loss prevention (DLP) tooling?",
     {N: "Formal DLP tool deployment is planned for Q2 2026.",
      C: "Email DLP in place.",
      F: "No."}),
    ("Compliance", "Do you hold or plan to obtain HITRUST certification?",
     {N: "N/A",
      C: "HITRUST r2 certification is on our roadmap.",
      F: "N/A"}),
]

# --- Plain factual / yes-no filler, as in real questionnaires ----------------------------------
FILLER = [
    ("General", "Legal name of the organization?", "Brightnote, Inc."),
    ("General", "Headquarters location?", "Austin, TX, USA"),
    ("General", "Number of employees?", "85"),
    ("General", "Describe the service provided.", "Cloud note-taking and knowledge management platform for teams."),
    ("General", "Where is customer data hosted?", "AWS us-east-1 with failover to us-west-2."),
    ("Governance", "Is there a documented information security policy?", "Yes"),
    ("Governance", "Is the information security policy approved by management?", "Yes"),
    ("Governance", "Is there a designated security leader?", "Yes, Head of Security reporting to the CTO."),
    ("Governance", "Is there a formal risk assessment process?", "Yes"),
    ("Governance", "Do you maintain cyber insurance?", "Yes"),
    ("Human Resources", "Are background checks performed on new hires?", "Yes, where permitted by law."),
    ("Human Resources", "Do employees sign confidentiality agreements?", "Yes"),
    ("Human Resources", "Is there a disciplinary process for policy violations?", "Yes"),
    ("Asset Management", "Do you maintain an asset inventory?", "Yes"),
    ("Asset Management", "Are company laptops centrally managed?", "Yes, via MDM."),
    ("Asset Management", "Is full-disk encryption enabled on endpoints?", "Yes"),
    ("Access Control", "Is SSO used for internal applications?", "Yes, Okta."),
    ("Access Control", "Are shared accounts permitted?", "No"),
    ("Access Control", "Is the principle of least privilege applied?", "Yes"),
    ("Access Control", "Is remote access to production via VPN or bastion?", "Access is via SSO-backed bastion."),
    ("Data Protection", "Is data encrypted in transit?", "Yes, TLS 1.2+."),
    ("Data Protection", "Do you have a data classification policy?", "Yes"),
    ("Data Protection", "Do you process cardholder data?", "N/A"),
    ("Data Protection", "Is customer data used to train machine learning models?", "No"),
    ("Data Protection", "Are encryption keys managed in a KMS?", "Yes, AWS KMS."),
    ("Application Security", "Do you follow a secure SDLC?", "Yes"),
    ("Application Security", "Is code peer reviewed before merge?", "Yes"),
    ("Application Security", "Do you perform static code analysis?", "Yes, in CI."),
    ("Application Security", "Do you scan third-party dependencies?", "Yes"),
    ("Application Security", "Is there a bug bounty program?", "No"),
    ("Network Security", "Are production networks segmented?", "Yes, VPC-level segmentation."),
    ("Network Security", "Is a WAF in place?", "Yes"),
    ("Network Security", "Is DDoS protection in place?", "Yes, AWS Shield Standard."),
    ("Vulnerability Management", "Do you perform vulnerability scanning?", "Yes"),
    ("Vulnerability Management", "Is anti-malware deployed on endpoints?", "Yes, EDR."),
    ("Incident Response", "Is there a documented incident response plan?", "Yes"),
    ("Incident Response", "Is there a designated incident response team?", "Yes"),
    ("Business Continuity", "Is there a business continuity plan?", "Yes"),
    ("Business Continuity", "Are backups encrypted?", "Yes"),
    ("Business Continuity", "Is the platform deployed across multiple availability zones?", "Yes"),
    ("Third Party", "Do you assess the security of your vendors?", "Yes"),
    ("Third Party", "Do you maintain a list of subprocessors?", "Yes, published on our website."),
    ("Physical Security", "Do you operate your own data centers?", "No, we rely on AWS."),
    ("Physical Security", "Are offices access controlled?", "Yes, badge access."),
    ("Privacy", "Do you have a privacy policy?", "Yes"),
    ("Privacy", "Do you support data subject access requests?", "Yes"),
    ("Privacy", "Have you appointed a DPO?", "N/A"),
    ("Compliance", "Have you had a security breach in the last 24 months?", "No"),
    ("Compliance", "Are you subject to HIPAA?", "Yes, as a business associate for healthcare customers."),
    ("Compliance", "Will you sign a BAA?", "Yes"),
]


def rows_for(customer):
    rows = [(d, q, a[customer]) for d, q, a in COMMITMENTS + ROADMAP]
    rows += FILLER
    random.shuffle(rows)
    rows.sort(key=lambda r: r[0])  # real questionnaires are grouped by domain
    return rows


HEAD = Font(bold=True, color="FFFFFF")
FILL = PatternFill("solid", fgColor="1F3864")


def style_header(ws, row):
    for cell in ws[row]:
        cell.font, cell.fill = HEAD, FILL


def write_sig_lite(path):
    """Northwind Bank: SIG Lite-like layout with a cover block above the table."""
    wb = Workbook(); ws = wb.active; ws.title = "SIG Lite"
    ws.append(["Northwind Bank - Third Party Risk Assessment (SIG Lite format)"])
    ws.append(["Vendor:", "Brightnote, Inc.", "", "Completed:", "2026-03-14"])
    ws.append([])
    ws.append(["Ques Num", "Domain", "Question", "Response", "Additional Information"])
    style_header(ws, 4)
    for i, (d, q, a) in enumerate(rows_for(N), 1):
        short = a in ("Yes", "No", "N/A")
        ws.append([f"{d[:3].upper()}-{i:03d}", d, q, a if short else "Yes", "" if short else a])
    wb.save(path)


def write_caiq(path):
    """Contoso Health: CAIQ-like layout - Yes/No/NA column plus separate notes column."""
    wb = Workbook(); ws = wb.active; ws.title = "CAIQ"
    ws.append(["Question ID", "Control Domain", "Question", "CSP Answer (Yes/No/NA)", "CSP Implementation Description"])
    style_header(ws, 1)
    for i, (d, q, a) in enumerate(rows_for(C), 1):
        yn = a if a in ("Yes", "No", "N/A") else ("No" if a.lower().startswith(("no", "we are planning")) else "Yes")
        ws.append([f"{d[:3].upper()}-{i:02d}.1", d, q, yn.replace("N/A", "NA"), "" if a in ("Yes", "No", "N/A") else a])
    wb.save(path)


def write_custom(path):
    """Fabrikam Retail: home-grown form, answer in one free-text column, two sheets."""
    wb = Workbook()
    intro = wb.active; intro.title = "Instructions"
    intro.append(["Please answer every question. Attach evidence where possible."])
    ws = wb.create_sheet("Vendor Security Review")
    ws.append(["#", "Category", "Question", "Vendor Response"])
    style_header(ws, 1)
    for i, (d, q, a) in enumerate(rows_for(F), 1):
        ws.append([i, d, q, a])
    wb.save(path)


files = {
    N: OUT / "northwind_bank_sig_lite.xlsx",
    C: OUT / "contoso_health_caiq.xlsx",
    F: OUT / "fabrikam_retail_vendor_review.xlsx",
}
write_sig_lite(files[N]); write_caiq(files[C]); write_custom(files[F])

# Ground truth for scoring the extractor
truth = {
    "contradicting_topics": ["log_retention", "breach_notification", "access_revocation", "mfa_scope",
                             "pentest_frequency", "vuln_remediation_critical", "backup_retention", "rto",
                             "access_review_frequency", "data_deletion"],
    "consistent_topics": ["encryption_at_rest", "security_training"],
    "clock_start_mismatch": ["breach_notification"],
    "hedged": [[F, "breach_notification"], [F, "rto"]],
    "vague_commitments": [[C, "subprocessor_notice"]],
    "roadmap_items": [[N, "SOC 2 Type II"], [C, "SOC 2 Type II"], [C, "SIEM"], [N, "DLP"], [C, "HITRUST"]],
    "past_due_roadmap": [[N, "DLP"]],
}
(OUT / "planted_truth.json").write_text(json.dumps(truth, indent=2))
print({k: str(v.name) for k, v in files.items()})
print("rows per questionnaire:", len(COMMITMENTS) + len(ROADMAP) + len(FILLER))
