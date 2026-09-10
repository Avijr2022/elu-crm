# E-LinkUp Technical Debt — PF-004 Mid-Phase
**Document ID:** ELU-TD-003  
**Version:** 1.0  
**Date:** 2026-08-06  
**Extends:** ELU-TD-002  
**Related:** ELU-MPR-PF004, ELU-GAP-PF004  

---

## Critical
None open for PF-004 after mid-phase corrections.

## High

| ID | Item | Action |
|----|------|--------|
| TD-PF004-H01 | `address_id` not on organization | Add column + API per DDD/BFS |
| TD-PF004-H02 | Flutter Create + History screens missing | Implement before QA audit |

## Medium

| ID | Item | Action |
|----|------|--------|
| TD-PF004-M01 | Permission-grain RBAC for organization.* | Seed + enforce (or PF-009 waiver) |
| TD-PF004-M02 | PUT ≠ full replace | Align OpenAPI or implement replace |
| TD-PF004-M03 | Tax identifiers in audit payloads | Mask GSTIN/PAN |
| TD-PF004-M04 | No Flutter automated tests for org UI | Widget smoke |

## Low

| ID | Item | Action |
|----|------|--------|
| TD-PF004-L01 | Rollback SQL pack | Add paired rollback |
| TD-PF004-L02 | Export 500-row cap / no CSV headers | Stream or raise limit with filter |
| TD-PF004-L03 | NTF-PF-004-* unwired | CPS notification engine |

## Closed this review
- Soft-delete UK for org code  
- Platform Admin write violation vs BFS  
- Missing list sort  
- Missing parent index  

---

*© Euphoria Infotech (I) Limited — ELU-TD-003*
