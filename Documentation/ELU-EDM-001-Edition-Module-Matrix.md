# E-LinkUp Edition × Module Matrix
**Document ID:** ELU-EDM-001  
**Version:** 1.0  
**Status:** Approved  
**Document Owner:** Product Owner  
**Related Documents:** ELU-RDM-001, ELU-BFS-PF, ELU-SAD-001, ELU-ADR-009, ELU-ADR-013, ELU-DOC-001  
**Example Tenant:** Euphoria  

---

## Version History

| Version | Date | Author | Change |
|---------|------|--------|--------|
| 1.0 | 2026-08-06 | EIIP / Product Owner | Single packaging SoT for Community / Professional / Enterprise |

---

## 1. Purpose

**ELU-EDM-001** is the **authoritative edition × module matrix** for E-LinkUp.  
BFS headers, SAD §5.3, and server-side feature gates (**ADR-009**) must match this document.

---

## 2. Module Availability by Edition (v1.0 Product Scope)

| Module | Community | Professional | Enterprise | Release |
|--------|:---------:|:------------:|:----------:|---------|
| PF-001 Edition Management | Platform | Platform | Platform | v1.0 |
| PF-002 Tenant Management | Platform | Platform | Platform | v1.0 |
| PF-003 Subscription | Platform | Platform | Platform | v1.0 |
| PF-004 Organization (single) | ✓ | ✓ | ✓ | v1.0 |
| PF-005 Branch | — | ✓ | ✓ | v1.0 |
| PF-006 Department | ✓ | ✓ | ✓ | v1.0 |
| PF-007 Business Unit | — | ✓ | ✓ | v1.0 |
| PF-008 Users & Identity | ✓ | ✓ + MFA | ✓ + SSO/MFA | v1.0 |
| PF-009 RBAC | ✓ (≤5 custom roles) | ✓ (≤25) | ✓ unlimited | v1.0 |
| PF-010 Audit | ✓ 90 days | ✓ 1 year | ✓ 7 years | v1.0 |
| PF-011 System Configuration | ✓ | ✓ partial branding | ✓ full white-label | v1.0 |
| CRM-001 Lead | ✓ basic | ✓ | ✓ | v1.0 |
| CRM-001 Lead convert | Customer only | Customer + Opportunity | Customer + Opportunity | v1.0 |
| CRM-002 Opportunity | — | ✓ | ✓ | v1.0 |
| CRM-003 Customer | ✓ basic | ✓ | ✓ | v1.0 |
| CRM-004 Activity | ✓ | ✓ | ✓ | v1.0 |
| SAL-001…004 Sales | — | ✓ | ✓ | v1.0 |
| PRJ-001…006 Projects | — | ✓ | ✓ | v1.0 |
| FIN-001…004 Finance | — | ✓ | ✓ | v1.0 |
| SRV-001…003 Service | — | ✓ | ✓ | v1.1 |
| CPS engines (depth) | stub | ✓ | ✓ | v1.1 |
| INT-001…004 Integration | — | — | ✓ | v2.0 |
| CPS-004 BI / CPS-007 AI | — | partial / optional | ✓ | v2.0 |

---

## 3. Capability Limits

| Limit | Community | Professional | Enterprise |
|-------|-----------|--------------|------------|
| Max users | 5 | 50 | Unlimited (contract) |
| Max storage | 5 GB | 100 GB | Contract |
| Max custom roles | 5 | 25 | Unlimited |
| API access | Read-only (v2) | Full REST (v2) | REST + Webhooks (v2) |
| Tenant self-registration | — | ✓ | ✓ |

---

## 4. Enforcement

- UI may hide unavailable modules; **API must return 403** with code `EDITION_FORBIDDEN` if gated.
- Subscription expiry restricts licensed features (**BR-PF-***).
- Changes to this matrix require Product Owner approval and version bump; update BFS/SAD/RDM references.

---

*© Euphoria Infotech (I) Limited — ELU-EDM-001*
