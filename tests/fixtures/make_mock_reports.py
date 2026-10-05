"""Build two fictional SOC 3-style PDFs that reproduce the layouts the extractor must survive:

  mock_section_style.pdf   table of contents, lettered sections, a CUEC list that spans a page break,
                           running header/footer on every page, subservice organizations
  mock_embedded_style.pdf  no CUEC section; customer duties buried in per-service descriptions

Both companies and all wording are invented.
"""
from pathlib import Path

from reportlab.lib.pagesizes import letter
from reportlab.pdfgen import canvas

HERE = Path(__file__).parent
W, H = letter


class Doc:
    def __init__(self, path, header):
        self.c = canvas.Canvas(str(path), pagesize=letter)
        self.header, self.page, self.y = header, 0, 0
        self.new_page()

    def new_page(self):
        if self.page:
            self.c.showPage()
        self.page += 1
        self.c.setFont("Helvetica", 8)
        self.c.drawString(72, H - 40, self.header)
        self.c.drawRightString(W - 72, 40, f"Page {self.page}")
        self.y = H - 80

    def line(self, text, size=10, bold=False, gap=14):
        if self.y < 80:
            self.new_page()
        self.c.setFont("Helvetica-Bold" if bold else "Helvetica", size)
        self.c.drawString(72, self.y, text)
        self.y -= gap

    def para(self, text, width=88):
        words, cur = text.split(), ""
        for w in words:
            if len(cur) + len(w) + 1 > width:
                self.line(cur); cur = w
            else:
                cur = f"{cur} {w}".strip()
        if cur:
            self.line(cur)
        self.y -= 6

    def save(self):
        self.c.save()


def section_style():
    d = Doc(HERE / "mock_section_style.pdf", "Lumenvault, Inc. | SOC 3 Report | Proprietary")
    d.line("System and Organization Controls (SOC) 3 Report", 16, True, 24)
    d.line("Report on Lumenvault, Inc.'s Secrets Management Platform", 12)
    d.line("Relevant to Security and Availability", 12)
    d.line("For the period October 1, 2024 to September 30, 2025", 12, gap=30)
    d.line("Table of Contents", 12, True)
    for t, p in [("Section I: Independent Service Auditor's Report", 2), ("Section II: Management's Assertion", 3),
                 ("Section III: Description of the System", 4), ("D. Complementary User Entity Controls", 5)]:
        d.line(f"{t} {'.' * 30} {p}")
    d.new_page()
    d.line("Section I: Independent Service Auditor's Report", 12, True)
    d.para("We have examined management's assertion that the controls within Lumenvault, Inc.'s system were "
           "effective throughout the period October 1, 2024 to September 30, 2025, to provide reasonable assurance "
           "that service commitments were achieved based on the trust services criteria relevant to security and "
           "availability. Complementary user entity controls are required to achieve those commitments.")
    d.new_page()
    d.line("Section II: Management's Assertion", 12, True)
    d.para("Management asserts that the controls were effective, if complementary user entity controls and "
           "complementary subservice organization controls operated effectively.")
    d.new_page()
    d.line("Section III: Description of the System", 12, True)
    d.line("A. Overview", 11, True)
    d.para("Lumenvault provides a hosted secrets vault and key rotation service for engineering teams.")
    d.line("B. Subservice Organizations", 11, True)
    d.para("Lumenvault uses Amazon Web Services (AWS) for infrastructure hosting and Cloudflare for edge "
           "network services. These subservice organizations are carved out of this report.")
    d.line("C. Infrastructure", 11, True)
    for _ in range(14):
        d.para("The platform runs in multiple availability zones with automated failover and continuous monitoring.")
    d.line("D. Complementary User Entity Controls", 11, True)
    d.para("Lumenvault's controls were designed with the assumption that certain controls would be implemented "
           "by user entities. User entities are responsible for the following:")
    items = [
        "1. Enforcing multi-factor authentication for all users who access the Lumenvault console.",
        "2. Configuring single sign-on (SAML) and removing access for terminated personnel in a timely manner.",
        "3. Restricting API tokens to least privilege and rotating them according to their own policy.",
        "4. Reviewing audit logs exported from Lumenvault and retaining them to meet their own requirements.",
        "5. Notifying Lumenvault promptly of any suspected compromise of credentials or secrets.",
    ]
    for it in items:
        d.para(it)
    d.line("E. Principal Service Commitments", 11, True)
    d.para("Lumenvault commits to 99.9% availability and encryption of all stored secrets.")
    d.save()


def embedded_style():
    d = Doc(HERE / "mock_embedded_style.pdf", "Corvid Cloud SOC 3")
    d.line("System and Organization Controls 3 (SOC 3) Report", 16, True, 24)
    d.line("Corvid Cloud Services", 12)
    d.line("For the period April 1, 2025 through March 31, 2026", 12, gap=30)
    d.line("Description of Services", 12, True)
    d.para("Corvid Object Store: durable storage for any amount of data. Server-side encryption is available; "
           "customers are responsible for enabling encryption on buckets that hold sensitive data.")
    d.para("Corvid Compute: virtual machines in isolated networks. Customers are responsible for patching guest "
           "operating systems and configuring firewall rules for their instances.")
    d.para("Corvid Logs: collects platform API activity. Customers must configure a retention period for their log "
           "groups; by default logs are kept for 30 days.")
    d.para("Corvid Directory: identity service for customer workloads. Corvid manages the underlying hosts.")
    d.save()


if __name__ == "__main__":
    section_style(); embedded_style()
    print("wrote", [p.name for p in HERE.glob("*.pdf")])
