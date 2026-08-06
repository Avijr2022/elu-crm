# Gap List & Recommended Corrections — PF-004 Mid-Phase
**Document ID:** ELU-GAP-PF004  
**Version:** 1.0  
**Date:** 2026-08-06  
**Parent:** ELU-MPR-PF004  
**Rule:** Close High before QA Release Audit. Do not touch baselined PF-001…PF-003A.

---

## F. Gap List

| ID | Area | Gap | Severity | Owner |
|----|------|-----|----------|-------|
| G-01 | DDD / DB | `address_id` FK to `tenant_address` not implemented | **High** | Backend |
| G-02 | UI | Organization Create screen missing (API exists for children) | **High** | Flutter |
| G-03 | UI | Organization History / audit timeline missing | **High** | Flutter |
| G-04 | UI | Dedicated View screen (read-only summary) missing | Medium | Flutter |
| G-05 | Security | `organization.*` permission grains seeded/enforced | Closed | Backend / PF-009 |
| G-06 | Security | GSTIN/PAN not masked in audit payload | Medium | Backend |
| G-07 | API | PUT is not full-replace semantics | Medium | Backend |
| G-08 | API | Export lacks `organization.export` grain; no CSV Content-Disposition | Low | Backend |
| G-09 | DB | No dedicated rollback SQL pack | Low | DBA |
| G-10 | Docs | ELU-API-PF / ELU-UI-PF not fully synced to implementation | Medium | BA/Docs |
| G-11 | QA | No Flutter widget/integration tests | Medium | QA |
| G-12 | NFR | AC-PF-004-04 PDF name propagation deferred (document engine) | Low | FIN/Doc |
| G-13 | NTF | NTF-PF-004-01…03 not wired | Low | CPS |
| G-14 | Perf | Export hard-capped at 500 rows | Low | Backend |

---

## G. Recommended Corrections (priority order)

### Must before QA Release Audit
1. **G-01** Add nullable `address_id UUID REFERENCES core.tenant_address` + API field.  
2. **G-02 / G-03** Flutter Create (child) + History (audit filter by entity).  
3. **G-04** Read-only View dialog/page with tax/fiscal sections.  
4. **G-10** Sync ELU-API-PF + ELU-UI-PF + RTM to 100% of delivered surface.  
5. Re-run isolation case: Tenant A cannot GET Tenant B org id (explicit PF-004 ISO test).

### Should before baseline
6. **G-05** Seed `organization.create|read|update|delete|export`; wire checks (or track PF-009 with waiver).  
7. **G-06** Mask GSTIN/PAN in audit payloads.  
8. **G-07** Implement true PUT replace or document PATCH-only in OpenAPI.  
9. **G-11** Flutter smoke test for OrganizationsPage.

### Nice / deferred
10. **G-09** Rollback script `013_organization_pf004_rollback.sql`.  
11. **G-12…G-14** Document engine, NTF, export streaming.

### Already corrected this review
- Soft-delete UK, parent index, TENANT_ADMIN write-only, sort, status transitions, Flutter Semantics/empty/dispose, Platform Admin 403 test, OpenAPI fragment, and organization permission-grain enforcement.

---

*© Euphoria Infotech (I) Limited — ELU-GAP-PF004*
