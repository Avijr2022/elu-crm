# Release Notes — PF-004 Organization Management
**Document ID:** ELU-REL-PF004  
**Release:** Phase-2-PF004  
**Status:** **QA PASS — RELEASE APPROVED**  
**Date:** 2026-08-06  
**Git tag:** **`Phase-2-PF004-R1`** (annotated) @ `3f30159a3ba73be1f09be791164982ec74ff8044` — created and pushed 2026-09-11. Per HD-10 the existing `Phase-2-PF004` tag is preserved as a historical artefact.  
**Prior baselines:** Phase-2-PF001 … Phase-2-PF003A  
**QA:** ELU-QA-PF004 v1.0 PASS — RELEASE APPROVED  

---

## Summary

PF-004 delivers tenant Organization Management: ROOT uniqueness, child create, profile/tax/fiscal fields, hierarchy, audit history, address link, Tenant-Admin writes with Platform-Admin read-only, Flutter Organizations UX (Create / View / Edit / Hierarchy / History), and rollback SQL.

## Delivered

- APIs: `/api/v1/org/organizations` (list, search, export, root, CRUD, hierarchy, history)
- SQL: `013_organization_pf004.sql` + `013_organization_pf004_rollback.sql` / `migrate_pf004.py`
- Flutter: `organizations_page.dart` + `organization_service.dart`
- Permissions seeded: `organization.create|read|update|delete|export`
- Tests: **13** PF-004 + **1** org isolation (suite **25** with isolation) — **2× consecutive PASS**
- Flutter analyze: **0 issues** on org feature files

## Business rules enforced

- BR-PF-028 one ROOT / child-only create  
- BR-PF-029 active code UK  
- BR-PF-030 GSTIN  
- BR-PF-031 no delete ROOT  
- BR-PF-033 fiscal month  

## Freeze (after human approval)

- **PF-001…PF-004** locked — change only on documented bug, approved CR, or ADR  
- Next module starts only after explicit human instruction  

## Approval

- [x] QA Release Audit PASS  
- [x] Human **RELEASE APPROVED**  
- [x] Git tag `Phase-2-PF004-R1` @ `3f30159a3ba73be1f09be791164982ec74ff8044`  

## Tag disposition (HD-10) — 2026-09-11

Decision recorded as governance documentation only — **no tag was created, moved or deleted** (historical record, retained verbatim in meaning):

- The existing `Phase-2-PF004` tag is **preserved unchanged** as a historical artefact (target `a3397b4`, the PF-004 mid-phase review snapshot; it does not contain the approved corrections merged via PR #7).
- The existing `Phase-2-PF004-MidReview` tag is **preserved unchanged**.
- **Neither existing tag is treated as the approved PF-004 release tag.**
- **Historical status at the time of the HD-10 decision: Human RELEASE APPROVED was PENDING** — consequently **no tag was created or moved** while that condition held.
- After Human **RELEASE APPROVED** is formally recorded here and in `ELU-QA-PF004`, a **distinct annotated release tag** may be created against the actual approved release commit (proposed name: `Phase-2-PF004-R1`).
- **PF-005 remains blocked** until that human release approval is recorded.

### Post-approval disposition (RECONCILED 2026-09-11)

Human **RELEASE APPROVED** was recorded on **2026-09-11** (see Approval above and `ELU-QA-PF004` §5); the blocking PENDING condition is therefore satisfied. The approved release tag has since been **created and pushed**:

- **Tag:** `Phase-2-PF004-R1` — **annotated**
- **Target commit:** `3f30159a3ba73be1f09be791164982ec74ff8044` — `Baseline PF-004 as Phase-2-PF004 RELEASE APPROVED.` (single-parent baseline commit on `master`, child of `ad039ea`; introduces no file changes)
- **Remote:** `origin` — `refs/tags/Phase-2-PF004-R1` (tag object `badf34a2…`, peels to `3f30159a…`)
- **Historical tags untouched:** `Phase-2-PF004` and `Phase-2-PF004-MidReview` both remain at `a3397b4a5cdca667b0a5c1a54eb8dd6f417e1fa7`.

---

*© Euphoria Infotech (I) Limited — ELU-REL-PF004*
