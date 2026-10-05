# Trust Ledger: promise consistency report

Scanned 201 questionnaire answers. Found **10 inconsistent commitments** (9 high, 1 medium, 0 low).

**Promises the environment breaks today:** Contoso Health, Northwind Bank

## [HIGH] access review frequency

| Customer | Promised | Wording | Source |
|---|---|---|---|
| Contoso Health | quarterly | “Access is reviewed quarterly by system owners.” | contoso_health_caiq.xlsx ACC-06.1 |
| Fabrikam Retail | annually | “Access reviews are performed annually.” | fabrikam_retail_vendor_review.xlsx 6 |
| Northwind Bank | quarterly | “User access reviews are performed quarterly.” | northwind_bank_sig_lite.xlsx ACC-002 |

- Values differ: strictest is quarterly (Contoso Health), loosest is annually (Fabrikam Retail)
- **Operating bar:** you must operate at quarterly to keep every promise. Fall short and the Contoso Health promise breaks first.

## [HIGH] access revocation

| Customer | Promised | Wording | Source |
|---|---|---|---|
| Contoso Health | 24 hours | “Access is revoked within 24 hours of the employee's last day.” | contoso_health_caiq.xlsx ACC-05.1 |
| Fabrikam Retail | 48 hours | “Access removal is completed within 48 hours.” | fabrikam_retail_vendor_review.xlsx 1 |
| Northwind Bank | 24 hours | “Access is revoked within 24 hours of termination.” | northwind_bank_sig_lite.xlsx ACC-005 |

- Values differ: strictest is 24 hours (Contoso Health), loosest is 48 hours (Fabrikam Retail)
- Clock starts at different events: Contoso Health → last working day, Northwind Bank → termination
- **Operating bar:** you must operate at 24 hours to keep every promise. Fall short and the Contoso Health promise breaks first.

## [HIGH] breach notification

| Customer | Promised | Wording | Source |
|---|---|---|---|
| Contoso Health | 24 hours | “Customers are notified within 24 hours of discovery of a breach involving PHI.” | contoso_health_caiq.xlsx INC-50.1 |
| Fabrikam Retail | 72 hours | “Notification occurs without undue delay, typically within 72 hours.” | fabrikam_retail_vendor_review.xlsx 48 |
| Northwind Bank | 72 hours | “We will notify affected customers within 72 hours of confirming a security incident.” | northwind_bank_sig_lite.xlsx INC-048 |

- Values differ: strictest is 24 hours (Contoso Health), loosest is 72 hours (Northwind Bank)
- Clock starts at different events: Contoso Health → discovery, Northwind Bank → confirmation
- Hedged for Fabrikam Retail, firm for the others
- **Operating bar:** you must operate at 24 hours to keep every promise. Fall short and the Contoso Health promise breaks first.

## [HIGH] data deletion

| Customer | Promised | Wording | Source |
|---|---|---|---|
| Contoso Health | 30 days | “Data is deleted within 30 days of termination and a certificate of destruction is provided.” | contoso_health_caiq.xlsx DAT-27.1 |
| Fabrikam Retail | 90 days | “Customer data is purged within 90 days of termination.” | fabrikam_retail_vendor_review.xlsx 33 |
| Northwind Bank | 30 days | “Customer data is deleted within 30 days of contract termination.” | northwind_bank_sig_lite.xlsx DAT-027 |

- Values differ: strictest is 30 days (Contoso Health), loosest is 90 days (Fabrikam Retail)
- **Operating bar:** you must operate at 30 days to keep every promise. Fall short and the Contoso Health promise breaks first.

## [HIGH] log retention

| Customer | Promised | Wording | Source |
|---|---|---|---|
| Contoso Health | 12 months | “Logs are retained for 12 months in immutable storage.” | contoso_health_caiq.xlsx LOG-51.1 |
| Fabrikam Retail | 90 days | “We retain logs for 90 days.” | fabrikam_retail_vendor_review.xlsx 51 |
| Northwind Bank | 1 year | “Security audit logs are retained for a minimum of one (1) year.” | northwind_bank_sig_lite.xlsx LOG-051 |

- Values differ: strictest is 12 months (Contoso Health), loosest is 90 days (Fabrikam Retail)
- **Operating bar:** you must operate at 12 months to keep every promise. Fall short and the Contoso Health promise breaks first.
- ❌ **Reality check:** environment does 90 days [S3 lifecycle rule on CloudTrail bucket]. Broken today for: Contoso Health (12 months), Northwind Bank (1 year).

## [HIGH] mfa scope

| Customer | Promised | Wording | Source |
|---|---|---|---|
| Contoso Health | all workforce accounts | “Yes. MFA is required for all workforce accounts.” | contoso_health_caiq.xlsx ACC-02.1 |
| Fabrikam Retail | administrator accounts only | “Yes, MFA is enabled for administrator accounts.” | fabrikam_retail_vendor_review.xlsx 3 |
| Northwind Bank | admin + production access | “Yes. MFA is enforced for all administrative and production access.” | northwind_bank_sig_lite.xlsx ACC-006 |

- Values differ: strictest is all workforce accounts (Contoso Health), loosest is administrator accounts only (Fabrikam Retail)
- **Operating bar:** you must operate at all workforce accounts to keep every promise. Fall short and the Contoso Health promise breaks first.
- ❌ **Reality check:** environment does admins only: GitHub org does not require 2FA [github_org_2fa_required check]. Broken today for: Contoso Health (all workforce accounts), Northwind Bank (admin + production access).

## [HIGH] pentest frequency

| Customer | Promised | Wording | Source |
|---|---|---|---|
| Contoso Health | twice a year | “Penetration testing is performed twice a year by an independent firm.” | contoso_health_caiq.xlsx VUL-66.1 |
| Fabrikam Retail | annually | “Annual penetration test by a third party.” | fabrikam_retail_vendor_review.xlsx 66 |
| Northwind Bank | annually | “Third-party penetration tests are performed annually.” | northwind_bank_sig_lite.xlsx VUL-065 |

- Values differ: strictest is twice a year (Contoso Health), loosest is annually (Northwind Bank)
- **Operating bar:** you must operate at twice a year to keep every promise. Fall short and the Contoso Health promise breaks first.
- ❌ **Reality check:** environment does annually (last test 2026-02) [Pentest report register]. Broken today for: Contoso Health (twice a year).

## [HIGH] rto

| Customer | Promised | Wording | Source |
|---|---|---|---|
| Contoso Health | 8 hours | “RTO is 8 hours for the production platform.” | contoso_health_caiq.xlsx BUS-16.1 |
| Fabrikam Retail | 24 hours | “We target an RTO of 24 hours.” | fabrikam_retail_vendor_review.xlsx 19 |
| Northwind Bank | 4 hours | “Our RTO is 4 hours.” | northwind_bank_sig_lite.xlsx BUS-018 |

- Values differ: strictest is 4 hours (Northwind Bank), loosest is 24 hours (Fabrikam Retail)
- Hedged for Fabrikam Retail, firm for the others
- **Operating bar:** you must operate at 4 hours to keep every promise. Fall short and the Northwind Bank promise breaks first.

## [HIGH] vuln remediation critical

| Customer | Promised | Wording | Source |
|---|---|---|---|
| Contoso Health | 7 days | “Critical vulnerabilities are patched within 7 days of identification.” | contoso_health_caiq.xlsx VUL-65.1 |
| Fabrikam Retail | 30 days | “Critical: 30 days.” | fabrikam_retail_vendor_review.xlsx 64 |
| Northwind Bank | 15 days | “Critical vulnerabilities are remediated within 15 days.” | northwind_bank_sig_lite.xlsx VUL-066 |

- Values differ: strictest is 7 days (Contoso Health), loosest is 30 days (Fabrikam Retail)
- **Operating bar:** you must operate at 7 days to keep every promise. Fall short and the Contoso Health promise breaks first.

## [MEDIUM] backup retention

| Customer | Promised | Wording | Source |
|---|---|---|---|
| Contoso Health | 35 days | “Daily backups, retained for 35 days.” | contoso_health_caiq.xlsx BUS-19.1 |
| Fabrikam Retail | 30 days | “Daily backups with 30 day retention.” | fabrikam_retail_vendor_review.xlsx 16 |
| Northwind Bank | 35 days | “Backups are performed daily and retained for 35 days.” | northwind_bank_sig_lite.xlsx BUS-019 |

- Values differ: strictest is 35 days (Contoso Health), loosest is 30 days (Fabrikam Retail)
- **Operating bar:** you must operate at 35 days to keep every promise. Fall short and the Contoso Health promise breaks first.
- ✅ Reality check: environment does 35 days; all promises met.

## Vague commitments (promised, but not measurable)

- Contoso Health, subprocessor notice: “Yes, we notify customers of new subprocessors.” (contoso_health_caiq.xlsx THI-62.1)

## Roadmap promises

| Customer | Subject | Wording | Status |
|---|---|---|---|
| Northwind Bank | DLP | “Formal DLP tool deployment is planned for Q2 2026.” | ⚠️ **PAST DUE** |
| Contoso Health | SOC 2 Type II | “Type I available under NDA. Type II expected Q1 2027.” | due 2027-03-31 |
| Contoso Health | HITRUST | “HITRUST r2 certification is on our roadmap.” | no date given |
| Contoso Health | SIEM | “We are planning to implement a SIEM by end of 2026.” | due 2026-12-31 |
| Northwind Bank | SOC 2 Type II | “SOC 2 Type I issued; Type II report expected Q1 2027.” | due 2027-03-31 |
