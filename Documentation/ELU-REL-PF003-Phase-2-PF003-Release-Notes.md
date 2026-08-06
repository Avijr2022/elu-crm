# Release Notes — PF-003 Subscription Management (Candidate)
**Document ID:** ELU-REL-PF003  
**Release:** Phase-2-PF003 (candidate)  
**Status:** **QA PASS — awaiting HUMAN RELEASE APPROVED**  
**Date:** 2026-08-06  
**QA:** ELU-QA-PF003 v2.0 PASS  

---

## Summary

PF-003 Subscription Lifecycle with full platform APIs, DB constraints (one-current UK, current_subscription FK, seat CHECK), Flutter Create/Edit/History/My Subscription, expire→tenant SUSPENDED, cancel→tenant OFFBOARDING.

## Remediation in v2 audit
- `uk_subscription_one_current` (BR-PF-019)
- `fk_tenant_current_subscription` ON DELETE SET NULL
- `seat_count` / `billing_cycle` NOT NULL + seat CHECK
- Flutter Create, Edit, History, My Subscription + responsive filters
- Cancel cascades OFFBOARDING
- Schema + OpenAPI regression tests (12/12)

## Tests
- `test_pf003_subscriptions.py` — **12/12 × 2**
- Flutter analyze — **PASS**

## Freeze rule (after approval)
- Tag `Phase-2-PF003` only after human RELEASE APPROVED
- Do not start PF-004 until approved
- PF-001 / PF-002 remain locked

---

*© Euphoria Infotech (I) Limited — ELU-REL-PF003*
