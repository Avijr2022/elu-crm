# E-LinkUp CRM Build Tracker
**Document ID:** ELU-MSL-002  
**Version:** 4.12  
**Status:** Active — SAL/PRJ/FIN v4  
**Last synced:** 2026-09-07

---

## Executive snapshot

| Area | Remark |
|------|--------|
| FIN | Payment receipt list/detail API + Flutter pages; invoice stub from confirmed SO |
| FIN | Payment allocation stub links receipt → invoice on invoice generation |
| PF | Branding primary-color picker with PDF accent preview |
| Tests | **18 pytest** (SAL/PRJ/PF/FIN slice) + **25 Flutter** |

---

## Deliverables (v4.12)

| # | Feature |
|---|---------|
| 1 | `GET /api/v1/fin/payment-receipts` + detail; Flutter list/detail pages + nav |
| 2 | `POST /api/v1/sal/sales-orders/{id}/generate-invoice-stub` → `finance.invoice` (FIN_INVOICE) |
| 3 | `PUT /api/v1/tenant/branding/primary-color`; Flutter color presets + preview bar |
| 4 | `finance.payment_allocation` auto-created when invoice stub matches SO receipts |

---

## API changes (v4.12)

| Endpoint | Notes |
|----------|-------|
| `GET /api/v1/fin/payment-receipts` | List with `customer_name`, `so_number` |
| `GET /api/v1/fin/payment-receipts/{id}` | Detail with `allocations[]` |
| `POST /api/v1/sal/sales-orders/{id}/generate-invoice-stub` | Creates `INV-YYYY-####`, allocates receipts |
| `PUT /api/v1/tenant/branding/primary-color` | Body `{ "primary_color": "#RRGGBB" }` |

---

## Next jobs

| # | Job | Module |
|---|-----|--------|
| 1 | Invoice list/detail API + Flutter view | FIN |
| 2 | Issue invoice workflow (DRAFT → ISSUED) | FIN |
| 3 | Payment receipt → SO detail deep link | UI / FIN |
| 4 | Quotation PDF live preview in branding settings | UI / PF |

---

## Change log

| Version | Date | Change |
|---------|------|--------|
| 4.10 | 2026-09-07 | Branding UI; SO filter UI; payment stub persistence; JPEG PDF dimensions |
| 4.11 | 2026-09-07 | SO deep links; FIN payment receipt; PDF color bar; SO name labels |
| 4.12 | 2026-09-07 | FIN receipt API/UI; invoice stub; payment allocation; color picker |

| 4.13 | 2026-09-07 | Added DeepSeek V4 Flash integration helpers (`Backend/app/deepseek_client.py`, `Backend/scripts/test_deepseek.py`); updated `.continue/config.yaml` to source `DEEPSEEK_API_KEY` from environment. |
| 4.14 | 2026-09-07 | Added Redis-backed rate limiting + per-tenant token metrics, JWT-protected DeepSeek endpoint (`/api/v1/integrations/deepseek/generate`), logging, and README with scrub instructions. |
| 4.15 | 2026-09-07 | Started v4.12 work: implemented Payment Receipts UI scaffold in Flutter and verified backend payment receipt APIs + invoice stub endpoints are present. Next: implement invoice generation flow wiring in UI and payment allocation workflow. |
| 4.16 | 2026-09-07 | Implemented Flutter UI wiring for invoice-stub generation: added button on receipt detail to call `POST /sal/sales-orders/{id}/generate-invoice-stub` (token prompt + cached access token). Updated app navigation. |
| 4.17 | 2026-09-07 | Implemented backend allocation endpoint `POST /fin/payment-receipts/{id}/allocate` and updated Flutter to call allocation after invoice-stub creation; UI shows compact invoice summary. |

| 4.18 | 2026-09-07 | Added partial-allocation support to backend `allocate` endpoint (optional `allocated_amount`); wired Flutter receipt list to fetch real receipts and support full/partial allocation flows against `POST /fin/payment-receipts/{id}/allocate`. |
| 4.19 | 2026-09-07 | Added developer usage examples: DeepSeek curl/Python/Node snippets and API allocation curl examples in `Backend/README_DEEPSEEK.md`. |
| 4.20 | 2026-09-07 | Added unit tests for partial-allocation logic (`Backend/tests/test_unit_payment_allocation.py`) to validate full, partial, and edge-case allocation behavior without DB dependencies. |
| 4.21 | 2026-09-07 | Added Branding UI screen in Flutter (`customertracker/lib/screens/branding_primary_color.dart`) and navigation entry; uses `PUT /api/v1/tenant/branding/primary-color` to persist primary color and shows PDF accent preview. |
| 4.22 | 2026-09-07 | Ran DeepSeek minimal token check via `Backend/scripts/test_deepseek.py`; token present and minimal call (max 1 token) succeeded — usage recorded in `Documentation/ELU-MSL-002-CRM-Build-Tracker.md`. |
| 4.23 | 2026-09-07 | Ran smoke-imports and unit tests: `scripts/smoke_imports.py` imported key modules successfully; `tests/test_unit_payment_allocation.py` — 4 tests passed. |
| 4.24 | 2026-09-07 | Added `BrandingService` in `customertracker` Flutter app (`customertracker/lib/features/platform/data/branding_service.dart`) to include auth headers from `SharedPreferences` and wire the Branding screen to backend `PUT /api/v1/tenant/branding/primary-color`. |
| 4.25 | 2026-09-07 | Ran end-to-end branding check against local backend (`scripts/e2e_branding_check.py`): login 200, `PUT /api/v1/tenant/branding/primary-color` 200, primary color persisted (`#FF8F00`) → `E2E_BRANDING_OK`. |
| 4.26 | 2026-09-07 | Verification pass on DeepSeek deliverables — all present and correct: `app/deepseek_client.py` (reads `DEEPSEEK_API_KEY`, model `deepseek-v4-flash`), `.continue/config.yaml` uses `apiKeyEnv: DEEPSEEK_API_KEY` (no hard-coded key), `requirements.txt` includes `httpx`/`redis`, `scripts/test_deepseek.py` minimal check, examples in `README_DEEPSEEK.md`. |
| 4.27 | 2026-09-07 | Stabilized FIN integration tests and fixed surfaced bugs. `tests/test_fin_payment_receipts.py::_so_with_payment_stub` now adds a quotation line before `SUBMITTED` (and asserts transitions) so the quote reaches `ACCEPTED`. Fixed `list_payment_receipts` and `get_payment_receipt` in `app/services/fin/payment_receipt_service.py` (excluded `customer_name`/`so_number` from `model_dump()` to stop duplicate kwargs). Added `response_model=PaymentAllocationResponse` to `POST /fin/payment-receipts/{id}/allocate`. Rewrote `test_fin_partial_allocation.py` to use a real invoice + a second fresh receipt, covering 422/409/partial/full/over-allocation. Result: 9 passed (unit + FIN + branding + SAL slice). |
| 4.28 | 2026-09-07 | Full backend suite green. Fixed DB-state pollution in `tests/test_crm_activity_outcomes.py`: `test_create_and_deactivate_activity_outcome` now uses a unique uppercase code (`WARM_LEAD_<hex>`) and always deactivates it (try/finally) so a shared persistent DB never leaks an extra active CALL outcome; deactivated the one leftover `WARM_LEAD` artifact. Full `pytest` suite: **116 passed** (exit 0). |
| 4.29 | 2026-09-07 | Live end-to-end FIN allocation verified against running backend via new `scripts/e2e_fin_allocation.py` (quote → accept → SO → confirm → stub R1 → invoice stub auto-allocates R1 → stub R2 → allocate 0/neg/excess → partial 200 → remaining 200 → over-allocation 409). Also restarted the local uvicorn so it serves the corrected service code (previously stale → 500 on receipt detail). Result: `E2E_FIN_ALLOCATION_OK`. |
| 4.30 | 2026-09-07 | CI: expanded `.github/workflows/crm-tests.yml` `crm-api` job from the CRM/SAL subset to the full backend suite (`python -m pytest -q --tb=short`) against a fresh Postgres service — covers CRM, SAL, FIN (receipts + partial allocation), PF (branding/editions/tenants/subscriptions/organizations), PRJ, and RLS isolation tests. YAML validated. |
| 4.31 | 2026-09-07 | Resolved Flutter analysis issues: fixed the branding screen import in `customertracker/lib/side_menu_app.dart` (now `package:customertracker/screens/branding_primary_color.dart`) so `BrandingPrimaryColorScreen` resolves; cleaned 3 lints in `branding_primary_color.dart` (string interpolation ×2, `use_build_context_synchronously` via `mounted` guards). `flutter analyze` on touched files: **No issues found**. |
| 4.32 | 2026-09-07 | Secret hygiene: re-scanned repo source dirs — no `sk-…` keys or hard-coded `apiKey:` remain (specific leaked key gone from config/docs). Added `.pre-commit-config.yaml` (`gitleaks`) and `.githooks/pre-commit` fallback guard; documented enable commands in `DevOps/SCRUB_DEEPSEEK_KEY.md`. Reviewed `git status`: accumulated FIN/SAL/PF/CRM/Flutter/CI changes present but uncommitted. |
| 4.33 | 2026-09-07 | Post-restart live verification sweep passed against the running backend: `E2E_BRANDING_OK` (login 200, `PUT /api/v1/tenant/branding/primary-color` 200, color persisted `#FF8F00`) and `E2E_FIN_ALLOCATION_OK` (invoice auto-allocated 1 receipt, partial 590.0 → 200, remaining → 200, over-allocation → 409). Server on `:8000` is serving all current fixes. |
| 4.34 | 2026-09-08 | Re-verified DeepSeek deliverables in current tree (no API spend; env check only): `.continue/config.yaml` uses `apiKeyEnv: DEEPSEEK_API_KEY` (no hard-coded key), `Backend/app/deepseek_client.py` present (env key, `deepseek-v4-flash`, `max_tokens`), `Backend/scripts/test_deepseek.py` + `Backend/README_DEEPSEEK.md` examples present, `requirements.txt` includes `httpx`/`redis`. `DEEPSEEK_API_KEY` is set in the environment. |
| 4.35 | 2026-09-08 | Commit verified: HEAD `9ac9fd3` ("implement deepseek v4 flash integration and sync database endpoints", branch `cursor/crm-opportunity-pipeline` synced with origin) — working tree clean. HEAD tree has no hard-coded keys; `.continue/config.yaml` uses `apiKeyEnv`. **History finding:** commit `5b643ca` (Add Continue config, already pushed) contains a committed DeepSeek key `sk-f484a1d7…` (removed only in `9ac9fd3`); a second key `sk-0a1d51c8…` existed only in an uncommitted working-tree state (now gone). Both keys should be rotated; history scrub (`git-filter-repo`) + force-push required to purge `5b643ca`. |
| 4.36 | 2026-09-08 | Secret-guard execution: enabled repo-local `core.hooksPath=.githooks` (lightweight pre-commit secret scanner is now active). Added `Scripts/scrub-secrets.sh` — ready-to-run `git-filter-repo` history scrub that reads keys from `SECRET1`/`SECRET2` env vars (no keys embedded), creates a mirror backup, rewrites history, and prints the force-push commands. Scrub NOT executed (requires key rotation + team approval). Token availability confirmed (`DEEPSEEK_API_KEY` set; no API spend). |
| 4.37 | 2026-09-08 | Pushed local commits to `origin/cursor/crm-opportunity-pipeline` (`9ac9fd3..66be459`; remote `github.com/Avijr2022/elu-crm.git`). Working tree clean and branch synced. |

*© Euphoria Infotech — ELU-MSL-002*
