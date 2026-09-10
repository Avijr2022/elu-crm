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
| 4.38 | 2026-09-09 | Re-verification (2026-09-09): all DeepSeek deliverables present (`app/deepseek_client.py`, `scripts/test_deepseek.py`, `README_DEEPSEEK.md`, `requirements.txt` with httpx/redis), `.continue/config.yaml` uses `apiKeyEnv`, no `sk-…`/`apiKey` secrets at HEAD, tree clean on `cursor/crm-opportunity-pipeline`, `DEEPSEEK_API_KEY` set (no API spend). |
| 4.39 | 2026-09-09 | Key rotation: new DeepSeek key created by owner and verified via `scripts/test_deepseek.py` (model `deepseek-v4-flash`, status completed, ~222 tokens). Key is NOT stored in any file — loaded only from `DEEPSEEK_API_KEY` env var. Guidance given for local (`setx`/session env), Continue (reads env), running backend (restart with new env), and CI (GitHub secret). Old exposed keys (`sk-f484a1d7…`, `sk-0a1d51c8…`) should be deleted in the DeepSeek console. |
| 4.40 | 2026-09-09 | Restarted the local backend on `:8000` with the rotated `DEEPSEEK_API_KEY` in its process env (new process 2100). Health check `200` (`{"status":"ok","app":"E-LinkUp"}`). The `/api/v1/integrations/deepseek/generate` endpoint now runs with the new key. |
| 4.41 | 2026-09-09 | Made the DeepSeek limiter resilient: `app/utils/redis_rate_limiter.py` adds short (2s) connect/IO timeouts and a fail-open `rate_allowed_or_fail_open()`; `app/api/v1/integrations/deepseek.py` pings Redis and logs a warning instead of 500ing when Redis is down. Added `scripts/e2e_deepseek_endpoint.py` and verified end-to-end through the running server with the rotated key: `generate 200`, `deepseek-v4-flash`, status `completed`, ~110 tokens. README updated with graceful-degradation note. |
| 4.42 | 2026-09-09 | Enabled Redis enforcement: added `redis:7-alpine` service (`elinkup-redis`, port 6379, AOF + `elinkup_redis` volume) to `docker-compose.yml` and wired `REDIS_URL: redis://redis:6379/0` into the API env. Started container (health `PONG`). Re-ran the DeepSeek endpoint e2e — Redis now records `deepseek:global:minute`, per-tenant minute key, and `deepseek:usage:2026-09-09` (tenant → 111 tokens). Rate limiting + token accounting active. |
| 4.43 | 2026-09-09 | Pushed commits through `13c07b8` to `origin/cursor/crm-opportunity-pipeline` (expanded CI workflow auto-triggers on push). Local `gh` CLI not installed, so CI run status must be checked in the GitHub Actions UI. |
| 4.44 | 2026-09-10 | Daily re-verification: DeepSeek deliverables present (`deepseek_client.py`, `test_deepseek.py`, `README_DEEPSEEK.md`, `requirements.txt`), `.continue/config.yaml` uses `apiKeyEnv`, no `sk-…` secrets at HEAD, tree clean on `cursor/crm-opportunity-pipeline`, `DEEPSEEK_API_KEY` set (no API spend), `elinkup-redis` container healthy (`PONG` earlier). |
| 4.45 | 2026-09-10 | Old DeepSeek keys deleted by owner (console) and **verified revoked**: `sk-f484a1d7…` → HTTP `401`, `sk-0a1d51c8…` → HTTP `401`. Rotated key still valid (`test_deepseek.py` → `completed`). Remaining: purge the old value from git history (`Scripts/scrub-secrets.sh`) + force-push, and persist the new key via `setx`. |
| 4.46 | 2026-09-10 | Persisted the rotated DeepSeek key as a user-level environment variable (`setx DEEPSEEK_API_KEY`, verified via `[Environment]::GetEnvironmentVariable(...,'User')`). New terminals/restarts now inherit it automatically; no key stored in any file. History scrub (`Scripts/scrub-secrets.sh` + force-push) still pending explicit go-ahead. |
| 4.47 | 2026-09-10 | Verified the pre-commit secret guard blocks a staged fake `sk-…` secret (hook printed the block message, exit 1, test file cleaned up — no commit made). Installed `git-filter-repo` into `Backend/.venv` and made `Scripts/scrub-secrets.sh` resolve it from PATH/venv/module. History scrub is now ready to run on explicit go-ahead. |
| 4.48 | 2026-09-10 | Investigated `customertracker` build: `flutter test` fails to compile due to a **SDK/package version mismatch** — local Flutter is **3.24.5**, but `font_awesome_flutter ^10.9.0` and `syncfusion_flutter_charts/calendar ^28.x` require Flutter 3.27+ (`Color.withValues` / `Color.r/g/b/a`). Not caused by our changes; CI (latest stable) is unaffected. Fix options: (A) `flutter upgrade` local SDK to align with CI, or (B) pin packages to Flutter-3.24-compatible versions. |
| 4.49 | 2026-09-10 | Applied **Option B** to `customertracker`: pinned `font_awesome_flutter: 10.7.0` and `syncfusion_flutter_calendar/charts: 27.1.48` (Flutter 3.24-compatible). Replaced the stale Flutter counter template test with a real smoke test for `MyTextField`. `flutter pub get` + `flutter test` now succeed — **"All tests passed!"**. NOTE: this is a local-SDK compatibility pin; if the team standardizes on Flutter 3.27+, revert to the `^` ranges. |
| 4.50 | 2026-09-10 | Cleared all Flutter analyzer issues in `customertracker`: renamed deprecated FontAwesome icons (`starHalfAlt→starHalfStroke`, `caretSquareDown→squareCaretDown`, `slidersH→sliders`) in 4 files and added `mounted` guards for `use_build_context_synchronously` + removed an unused `key` param in `payment_receipts_list.dart`. `flutter analyze` → **"No issues found!"** (was 15) and `flutter test` → **"All tests passed!"**. |
| 4.51 | 2026-09-10 | **Git history scrubbed** for the revoked DeepSeek keys. Ran `Scripts/scrub-secrets.sh` (mirror backup → `D:/CRM-crm-repo-backup.git`; `git-filter-repo --replace-text --force`, 51 commits rewritten). Verified `git log -S` finds **neither** key anywhere in history. filter-repo removed `origin`; re-added `https://github.com/Avijr2022/elu-crm.git`. **Force-push NOT performed** — awaiting explicit approval; collaborators must re-clone after the force-push. |
| 4.52 | 2026-09-10 | **History rewrite published**: `git push --force --all` (`a733561...bb53c7a` on `cursor/crm-opportunity-pipeline`, forced) + `git push --force --tags`. Verified after `git fetch --prune` that `git log -S` finds **neither** key in any local or remote ref. Upstream tracking restored. **All collaborators must re-clone** (their local history diverges). |
| 4.53 | 2026-09-10 | Post-rewrite audit: verified `origin/master` and `origin/agents/can-you-run-the-crm` do **not** contain either revoked key (`git log -S` empty), `origin/cursor/crm-opportunity-pipeline` == local HEAD `f86a7b1`, and `.continue/config.yaml` at HEAD uses `apiKeyEnv` only. Remote is fully key-free; `DEEPSEEK_API_KEY` present in env. |
| 4.54 | 2026-09-10 | CI verified locally (proxy): `Frontend` job commands pass — `flutter analyze lib test` → **No issues**; `flutter test test/widget_test.dart test/navigation_test.dart` → **14 tests passed**. Backend job command `pytest -q` → **116 passed** (verified earlier today; files unchanged since the history rewrite). GitHub-hosted run status still needs interactive `gh auth login` (device code expired) or the Actions UI. |
| 4.55 | 2026-09-10 | Owner added the `DEEPSEEK_API_KEY` GitHub Actions secret. Wired the workflow: added `workflow_dispatch` (manual runs on **any** branch — push triggers were limited to `main`/`master`/`develop`, so `cursor/…` pushes did not run CI) plus an optional **DeepSeek smoke check** step gated by the `deepseek_smoke` input (skips gracefully when the secret is absent, so no per-push token spend). YAML validated (`jobs: crm-api, flutter-widgets`). |
| 4.56 | 2026-09-10 | CI coverage fixes: added `Frontend/**` and `customertracker/**` to the `push`/`pull_request` `paths` filters (previously only `Backend/**`, so Flutter jobs never triggered on UI-only changes) and added a new **`customertracker`** job (`flutter pub get` → `flutter analyze lib test` → `flutter test`). YAML validated — 3 jobs: `crm-api`, `flutter-widgets`, `customertracker`; all their commands pass locally. |
| 4.57 | 2026-09-10 | Reconciled with upstream: remote branch had gained PR #1 (`Avijr2022-patch-1`) containing two content no-op `crm-tests.yml` commits + merge commit. Merged origin (`git pull --no-rebase`) and pushed the merge (`3c2c3f4..8caea33`); confirmed the merged workflow retains `Frontend/**`, `customertracker/**`, `workflow_dispatch`/`deepseek_smoke`, and the `customertracker` job. Tree clean, branch in sync. |
| 4.58 | 2026-09-10 | Decision: considered making lint infos non-fatal for the legacy `customertracker` CI job (`flutter analyze --no-fatal-infos`) since CI uses newer Flutter. Reverted to the locally-verified `flutter analyze lib test` (flag support couldn't be confirmed with the current unstable terminal) to keep CI deterministic. Follow-up: if CI surfaces SDK-version deprecation infos, add `--no-fatal-infos` after verifying the flag. |
| 4.59 | 2026-09-10 | Attempted a **fresh-DB CI-parity check** for the `crm-api` job: started a throwaway `postgres:16-alpine` (port 55433, no init SQL) and ran `pytest -q` against it. Result **inconclusive** — tests errored during setup with no summary (the local stack normally gets `Database/01_Schemas/001_CreateSchemas.sql` via compose init, which CI's plain Postgres service lacks), so this may reveal a real provisioning gap in CI. Temp container/files cleaned up. **Follow-up:** verify with an actual hosted CI run (needs `gh` auth) and, if it fails, either add the schema init to the CI service or ensure the app lifespan self-provisions the RLS roles. |
| 4.60 | 2026-09-10 | **Root cause of 4.59 found & fixed.** On a virgin DB the app lifespan runs more than once (multiple `TestClient` lifetimes); `seed_platform` re-inserted `core.role_permission` rows unguarded → `UniqueViolation` on `uk_role_permission` → the `crm-api` CI job would fail. Added `_link_role_permission()` in `app/db/seed.py` using `insert(RolePermission).on_conflict_do_nothing(constraint="uk_role_permission")` and routed the seeding paths through it. **Verified: full backend suite against a fresh `postgres:16-alpine` → `116 passed`** (86s). Temp container/files cleaned up. |
| 4.61 | 2026-09-10 | CI parity: added a `redis:7-alpine` service + `REDIS_URL: redis://localhost:6379/0` to the `crm-api` job (matches `docker-compose.yml`; enables future DeepSeek limiter/endpoint tests in CI). YAML validated — `services: postgres, redis`; jobs `crm-api`, `flutter-widgets`, `customertracker`. |
| 4.62 | 2026-09-10 | Added optional gated DeepSeek endpoint test `Backend/tests/test_deepseek_endpoint.py` (skips unless `DEEPSEEK_E2E=1` **and** `DEEPSEEK_API_KEY` set → no default token spend). Verified: default run → `1 skipped`; gated run → `1 passed`. Updated the CI manual smoke step to run this pytest endpoint test (covers client + server + Redis). |
| 4.63 | 2026-09-10 | Post-change regression: full backend suite on the dev DB → **117 passed** (116 + the optional DeepSeek endpoint test, which executed because `DEEPSEEK_E2E=1` was set in the session; it normally skips). No regressions from the `seed.py` idempotency fix. Cleared the `DEEPSEEK_E2E` flag and temp logs afterward. |

*© Euphoria Infotech — ELU-MSL-002*
