# PF-010 Audit & Compliance — Phase 2 Release Notes

## Release Identification

- Module: PF-010 — Audit & Compliance
- Release Phase: Phase 2
- Release scope: CORE — append-only audit trail, edition-based retention windows, callable retention purge service
- Release baseline (tag target): `30bc3a0ecdb865367b6a5c61f0c5f2f04a6ede16`
- Merge commit: `30bc3a0ecdb865367b6a5c61f0c5f2f04a6ede16` (PR #32)
- Implementation commit: `2085ea67971c47da1b34202c03c95b2988598ddb`
- Release tag: `Phase-2-PF010` — **NOT YET CREATED**
- Governance status: **RELEASE APPROVED** — CORE implemented, merged and documented; tag pending

## Human Authorization

**PF-010 RELEASE APPROVED: YES**

This is the verbatim human release-approval decision recorded for PF-010 CORE. It is not an AI-originated approval.

## Verification Evidence

| Evidence | Result |
|----------|--------|
| Focused PF-010 tests | **7 passed** |
| Full backend regression at PF-010 implementation | **271 passed / 1 skipped** |
| CI run `36419765262` | **SUCCESS** |
| Merge | PR #32 merged into `master` |
| App lifespan with `apply_pf010_ddl` | OK (`GET /health` 200) |

## Delivered CORE Scope

- `audit.audit_event` append-only enforcement: a `BEFORE UPDATE` trigger rejects mutation for every role, and `elu_app` is denied `UPDATE` / `DELETE`.
- `DELETE` on `audit.audit_event` remains privilege-controlled so the AC-03 retention purge under `owner_role()` stays possible.
- Edition-based retention windows: Community 90 / Professional 365 / Enterprise 2555 days, exposed through `retention_days_for_edition()`.
- `purge_expired_audit_events()` — retention implemented as a callable purge service (AC-03 decision, Option A).
- Index `idx_audit_event_created_on`; DDL applied through `apply_pf010_ddl`.

## Deferred Scope

- `JOB-PF-010-01` — scheduled retention-purge trigger, explicitly deferred from CORE (see the ELU-MSL-002 `PF-010 AC-03 Retention Decision` section).
- PF-010 audit reporting / UI / export surfaces.
- PF-011 System Configuration — separate phase, out of PF-010 scope.

## Governance Boundaries

- **Release baseline:** `30bc3a0ecdb865367b6a5c61f0c5f2f04a6ede16`.
- Later commits on `master` — the PF-011 implementation and the governance-reconciliation commits that include this document — are **not** part of the PF-010 release baseline.
- When `Phase-2-PF010` is created it must point at the release baseline above. It must **not** point at the tip of `master`, and it must **not** point at this governance commit.
- Existing PF-001 to PF-009 tags are immutable and are unchanged by this record.
- This document creates no tag and authorizes no push, PR or merge.

## Verification Boundary

This document records the PF-010 CORE release approval and names the release baseline. It creates no tag. `Phase-2-PF010` **does not exist** at the time this document is written.

---

*© Euphoria Infotech (I) Limited — ELU-REL-PF010 v1.0*
