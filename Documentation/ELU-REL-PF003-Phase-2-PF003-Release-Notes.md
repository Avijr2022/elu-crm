# Release Notes — PF-003 Subscription Management (Candidate)
**Document ID:** ELU-REL-PF003  
**Release:** Phase-2-PF003 (candidate)  
**Status:** **AWAITING RELEASE APPROVED**  
**Date:** 2026-08-06  
**Prior baselines:** Phase-2-PF001, Phase-2-PF002  

---

## Summary

PF-003 delivers Subscription Lifecycle: create, activate trial, renew, upgrade edition, expire (cascade tenant SUSPENDED), reactivate, cancel, history, usage, and Flutter Subscriptions UI.

## Delivered

### API
- `/api/v1/platform/subscriptions` CRUD + search/export
- `POST .../renew|upgrade|reactivate|expire`
- `GET .../history`
- `GET /api/v1/tenant/subscription` + `/usage`

### Data
- `011_subscription_pf003.sql` / `migrate_pf003.py`
- Columns: billing_cycle, seat_count, trial_end_date
- Tables: `subscription_history`, `subscription_usage`
- `tenant.current_subscription_id` backfill

### Flutter
- Platform Admin **Subscriptions** tab

### Tests
- `test_pf003_subscriptions.py` — **9/9** (×2)

## Freeze pending
- Await **RELEASE APPROVED** before tagging `Phase-2-PF003` and unlocking PF-004
- PF-001 / PF-002 remain locked

---

*© Euphoria Infotech (I) Limited — ELU-REL-PF003*
