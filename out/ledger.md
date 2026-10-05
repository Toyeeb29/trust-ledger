# Trust Ledger

| Customer | Promises | ✅ Supported | ❌ At risk | ❔ Unproven |
|---|---|---|---|---|
| Contoso Health | 13 | 1 | 3 | 9 |
| Fabrikam Retail | 12 | 3 | 1 | 8 |
| Northwind Bank | 13 | 2 | 2 | 9 |

## Vendor reports relied on

| Vendor | Report | Period end | Status | CUECs | Subservice orgs |
|---|---|---|---|---|---|
| GitHub | github_soc3_2023.pdf | 2023-09-30 | ⚠️ stale: request current report | 4 (section) | Amazon Web Services, Microsoft Azure, Equinix, CoreSite, QTS, Sabey |
| People Data Labs | pdl_soc3.pdf | 2022-09-30 | ⚠️ stale: request current report | 7 (section) | Amazon Web Services |
| AWS | aws_soc3.pdf | 2026-03-31 | ⚠️ request bridge letter | 8 (embedded) | - |

## Contoso Health

**❌ AT RISK: mfa scope**: “Yes. MFA is required for all workforce accounts.” <sub>(contoso_health_caiq.xlsx ACC-02.1)</sub>  
Why: GitHub CUEC failing: Org setting 'Require 2FA' is OFF  
- ❔ GitHub CUEC <sub>(github_soc3_2023.pdf PDF p.22)</sub>: Enabling SAML for their Enterprise Cloud accounts.  
  ↳ `github_saml_enforced`: SAML SSO requires GitHub Enterprise Cloud; org plan is 'free'
- ❌ GitHub CUEC <sub>(github_soc3_2023.pdf PDF p.22)</sub>: Enabling two-factor authentication and ensuring members and collaborators require two-factor authentication; this includes the implementation and management of personal access tokens.  
  ↳ `github_org_2fa_required`: Org setting 'Require 2FA' is OFF

**❌ AT RISK: log retention**: “Logs are retained for 12 months in immutable storage.” <sub>(contoso_health_caiq.xlsx LOG-51.1)</sub>  
Why: we actually do 90 days  
- ❌ Our environment: 90 days <sub>[S3 lifecycle rule on CloudTrail bucket]</sub>

**❌ AT RISK: pentest frequency**: “Penetration testing is performed twice a year by an independent firm.” <sub>(contoso_health_caiq.xlsx VUL-66.1)</sub>  
Why: we actually do annually (last test 2026-02)  
- ❌ Our environment: annually (last test 2026-02) <sub>[Pentest report register]</sub>

**❔ UNPROVEN: access revocation**: “Access is revoked within 24 hours of the employee's last day.” <sub>(contoso_health_caiq.xlsx ACC-05.1)</sub>  
Why: no evidence of any kind is linked to this promise  

**❔ UNPROVEN: access review frequency**: “Access is reviewed quarterly by system owners.” <sub>(contoso_health_caiq.xlsx ACC-06.1)</sub>  
Why: GitHub CUEC has no evidence; GitHub report is stale (period ended 2023-09-30); People Data Labs CUEC has no evidence; People Data Labs report is stale (period ended 2022-09-30)  
- ❔ GitHub CUEC <sub>(github_soc3_2023.pdf PDF p.22)</sub>: Administering and configuring repositories, including permissions, enabling required reviews for pull requests, and enabling required status checks before merging.  
  ↳ `github_branch_protection`: no evidence collected
- ➖ People Data Labs CUEC <sub>(pdl_soc3.pdf PDF p.22)</sub>: User entities are responsible for ensuring the supervision, management, and control of the use of People Data Labs, Inc. services by their personnel.  
  ↳ no automated check defined for this CUEC

**❔ UNPROVEN: rto**: “RTO is 8 hours for the production platform.” <sub>(contoso_health_caiq.xlsx BUS-16.1)</sub>  
Why: no evidence of any kind is linked to this promise  

**❔ UNPROVEN: data deletion**: “Data is deleted within 30 days of termination and a certificate of destruction is provided.” <sub>(contoso_health_caiq.xlsx DAT-27.1)</sub>  
Why: no evidence of any kind is linked to this promise  

**❔ UNPROVEN: encryption at rest**: “Yes - AES-256 via AWS KMS.” <sub>(contoso_health_caiq.xlsx DAT-32.1)</sub>  
Why: no evidence of any kind is linked to this promise  

**❔ UNPROVEN: security training**: “Training is completed at hire and annually.” <sub>(contoso_health_caiq.xlsx HUM-47.1)</sub>  
Why: no evidence of any kind is linked to this promise  

**❔ UNPROVEN: breach notification**: “Customers are notified within 24 hours of discovery of a breach involving PHI.” <sub>(contoso_health_caiq.xlsx INC-50.1)</sub>  
Why: no evidence of any kind is linked to this promise  

**❔ UNPROVEN: subprocessor notice**: “Yes, we notify customers of new subprocessors.” <sub>(contoso_health_caiq.xlsx THI-62.1)</sub>  
Why: no evidence of any kind is linked to this promise  

**❔ UNPROVEN: vuln remediation critical**: “Critical vulnerabilities are patched within 7 days of identification.” <sub>(contoso_health_caiq.xlsx VUL-65.1)</sub>  
Why: no evidence of any kind is linked to this promise  

**✅ SUPPORTED: backup retention**: “Daily backups, retained for 35 days.” <sub>(contoso_health_caiq.xlsx BUS-19.1)</sub>  
- ✅ Our environment: 35 days <sub>[AWS Backup plan 'prod-daily']</sub>


## Fabrikam Retail

**❌ AT RISK: mfa scope**: “Yes, MFA is enabled for administrator accounts.” <sub>(fabrikam_retail_vendor_review.xlsx 3)</sub>  
Why: GitHub CUEC failing: Org setting 'Require 2FA' is OFF  
- ❔ GitHub CUEC <sub>(github_soc3_2023.pdf PDF p.22)</sub>: Enabling SAML for their Enterprise Cloud accounts.  
  ↳ `github_saml_enforced`: SAML SSO requires GitHub Enterprise Cloud; org plan is 'free'
- ❌ GitHub CUEC <sub>(github_soc3_2023.pdf PDF p.22)</sub>: Enabling two-factor authentication and ensuring members and collaborators require two-factor authentication; this includes the implementation and management of personal access tokens.  
  ↳ `github_org_2fa_required`: Org setting 'Require 2FA' is OFF

**❔ UNPROVEN: access revocation**: “Access removal is completed within 48 hours.” <sub>(fabrikam_retail_vendor_review.xlsx 1)</sub>  
Why: no evidence of any kind is linked to this promise  

**❔ UNPROVEN: access review frequency**: “Access reviews are performed annually.” <sub>(fabrikam_retail_vendor_review.xlsx 6)</sub>  
Why: GitHub CUEC has no evidence; GitHub report is stale (period ended 2023-09-30); People Data Labs CUEC has no evidence; People Data Labs report is stale (period ended 2022-09-30)  
- ❔ GitHub CUEC <sub>(github_soc3_2023.pdf PDF p.22)</sub>: Administering and configuring repositories, including permissions, enabling required reviews for pull requests, and enabling required status checks before merging.  
  ↳ `github_branch_protection`: no evidence collected
- ➖ People Data Labs CUEC <sub>(pdl_soc3.pdf PDF p.22)</sub>: User entities are responsible for ensuring the supervision, management, and control of the use of People Data Labs, Inc. services by their personnel.  
  ↳ no automated check defined for this CUEC

**❔ UNPROVEN: rto**: “We target an RTO of 24 hours.” <sub>(fabrikam_retail_vendor_review.xlsx 19)</sub>  
Why: no evidence of any kind is linked to this promise  

**❔ UNPROVEN: encryption at rest**: “Yes, data at rest is encrypted with AES-256.” <sub>(fabrikam_retail_vendor_review.xlsx 30)</sub>  
Why: no evidence of any kind is linked to this promise  

**❔ UNPROVEN: data deletion**: “Customer data is purged within 90 days of termination.” <sub>(fabrikam_retail_vendor_review.xlsx 33)</sub>  
Why: no evidence of any kind is linked to this promise  

**❔ UNPROVEN: security training**: “Upon hire and annually.” <sub>(fabrikam_retail_vendor_review.xlsx 47)</sub>  
Why: no evidence of any kind is linked to this promise  

**❔ UNPROVEN: breach notification**: “Notification occurs without undue delay, typically within 72 hours.” <sub>(fabrikam_retail_vendor_review.xlsx 48)</sub>  
Why: no evidence of any kind is linked to this promise  

**❔ UNPROVEN: vuln remediation critical**: “Critical: 30 days.” <sub>(fabrikam_retail_vendor_review.xlsx 64)</sub>  
Why: no evidence of any kind is linked to this promise  

**✅ SUPPORTED: backup retention**: “Daily backups with 30 day retention.” <sub>(fabrikam_retail_vendor_review.xlsx 16)</sub>  
- ✅ Our environment: 35 days <sub>[AWS Backup plan 'prod-daily']</sub>

**✅ SUPPORTED: log retention**: “We retain logs for 90 days.” <sub>(fabrikam_retail_vendor_review.xlsx 51)</sub>  
- ✅ Our environment: 90 days <sub>[S3 lifecycle rule on CloudTrail bucket]</sub>

**✅ SUPPORTED: pentest frequency**: “Annual penetration test by a third party.” <sub>(fabrikam_retail_vendor_review.xlsx 66)</sub>  
- ✅ Our environment: annually (last test 2026-02) <sub>[Pentest report register]</sub>


## Northwind Bank

**❌ AT RISK: mfa scope**: “Yes. MFA is enforced for all administrative and production access.” <sub>(northwind_bank_sig_lite.xlsx ACC-006)</sub>  
Why: GitHub CUEC failing: Org setting 'Require 2FA' is OFF  
- ❔ GitHub CUEC <sub>(github_soc3_2023.pdf PDF p.22)</sub>: Enabling SAML for their Enterprise Cloud accounts.  
  ↳ `github_saml_enforced`: SAML SSO requires GitHub Enterprise Cloud; org plan is 'free'
- ❌ GitHub CUEC <sub>(github_soc3_2023.pdf PDF p.22)</sub>: Enabling two-factor authentication and ensuring members and collaborators require two-factor authentication; this includes the implementation and management of personal access tokens.  
  ↳ `github_org_2fa_required`: Org setting 'Require 2FA' is OFF

**❌ AT RISK: log retention**: “Security audit logs are retained for a minimum of one (1) year.” <sub>(northwind_bank_sig_lite.xlsx LOG-051)</sub>  
Why: we actually do 90 days  
- ❌ Our environment: 90 days <sub>[S3 lifecycle rule on CloudTrail bucket]</sub>

**❔ UNPROVEN: access review frequency**: “User access reviews are performed quarterly.” <sub>(northwind_bank_sig_lite.xlsx ACC-002)</sub>  
Why: GitHub CUEC has no evidence; GitHub report is stale (period ended 2023-09-30); People Data Labs CUEC has no evidence; People Data Labs report is stale (period ended 2022-09-30)  
- ❔ GitHub CUEC <sub>(github_soc3_2023.pdf PDF p.22)</sub>: Administering and configuring repositories, including permissions, enabling required reviews for pull requests, and enabling required status checks before merging.  
  ↳ `github_branch_protection`: no evidence collected
- ➖ People Data Labs CUEC <sub>(pdl_soc3.pdf PDF p.22)</sub>: User entities are responsible for ensuring the supervision, management, and control of the use of People Data Labs, Inc. services by their personnel.  
  ↳ no automated check defined for this CUEC

**❔ UNPROVEN: access revocation**: “Access is revoked within 24 hours of termination.” <sub>(northwind_bank_sig_lite.xlsx ACC-005)</sub>  
Why: no evidence of any kind is linked to this promise  

**❔ UNPROVEN: rto**: “Our RTO is 4 hours.” <sub>(northwind_bank_sig_lite.xlsx BUS-018)</sub>  
Why: no evidence of any kind is linked to this promise  

**❔ UNPROVEN: data deletion**: “Customer data is deleted within 30 days of contract termination.” <sub>(northwind_bank_sig_lite.xlsx DAT-027)</sub>  
Why: no evidence of any kind is linked to this promise  

**❔ UNPROVEN: encryption at rest**: “All customer data is encrypted at rest using AES-256.” <sub>(northwind_bank_sig_lite.xlsx DAT-032)</sub>  
Why: no evidence of any kind is linked to this promise  

**❔ UNPROVEN: security training**: “All employees complete security awareness training upon hire and annually thereafter.” <sub>(northwind_bank_sig_lite.xlsx HUM-044)</sub>  
Why: no evidence of any kind is linked to this promise  

**❔ UNPROVEN: breach notification**: “We will notify affected customers within 72 hours of confirming a security incident.” <sub>(northwind_bank_sig_lite.xlsx INC-048)</sub>  
Why: no evidence of any kind is linked to this promise  

**❔ UNPROVEN: subprocessor notice**: “Yes. We provide 30 days' prior notice of new subprocessors.” <sub>(northwind_bank_sig_lite.xlsx THI-061)</sub>  
Why: no evidence of any kind is linked to this promise  

**❔ UNPROVEN: vuln remediation critical**: “Critical vulnerabilities are remediated within 15 days.” <sub>(northwind_bank_sig_lite.xlsx VUL-066)</sub>  
Why: no evidence of any kind is linked to this promise  

**✅ SUPPORTED: backup retention**: “Backups are performed daily and retained for 35 days.” <sub>(northwind_bank_sig_lite.xlsx BUS-019)</sub>  
- ✅ Our environment: 35 days <sub>[AWS Backup plan 'prod-daily']</sub>

**✅ SUPPORTED: pentest frequency**: “Third-party penetration tests are performed annually.” <sub>(northwind_bank_sig_lite.xlsx VUL-065)</sub>  
- ✅ Our environment: annually (last test 2026-02) <sub>[Pentest report register]</sub>
