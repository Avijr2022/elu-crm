# E-LinkUp Business Functional Specification — Integration Domain Pack
**Document ID:** ELU-BFS-INT  
**Document Name:** Integration Domain BFS Pack (Enterprise Connectivity)  
**Version:** 1.0  
**Status:** Approved
**Related Documents:** ELU-DOC-001, ELU-DF-001, ELU-BRD-001, ELU-EFS-001, ELU-RTM-001
**Classification:** Internal Confidential  
**Project:** E-LinkUp (By Euphoria Infotech)  
**Prepared By:** Senior BA / Enterprise Solution Architect / Product Owner  
**Document Owner:** PMO  
**Example Tenant:** Euphoria  
**Stack:** Flutter · FastAPI · PostgreSQL · JWT + Refresh · Docker · MinIO · Celery/Redis (Phase 3+)  
**Related Documents:** ELU-DF-001, ELU-BRD-001, ELU-SAD-001, ELU-BFS-CPS (CPS-008)

---

## Version History

| Version | Date | Author | Change |
|---------|------|--------|--------|
| 1.0 | 2026-07-31 | EIIP | Initial BFS pack (seventeen sections) |
| 1.0a | 2026-07-31 | EIIP / PMO | Status Approved; registered in ELU-DOC-001; Related Documents standardized |

## Pack Index

| Module ID | Module / Sub Module / Feature | Priority | Phase / Release | Section |
|-----------|-------------------------------|----------|-----------------|---------|
| INT-001 | REST API Management | High | v2.0 Phase 4 | [§ INT-001](#module-int-001--rest-api-management) |
| INT-002 | Webhook Management | High | v2.0 Phase 4 | [§ INT-002](#module-int-002--webhook-management) |
| INT-003 | OAuth Management | Medium | v2.0 Phase 4 | [§ INT-003](#module-int-003--oauth-management) |
| INT-004 | Connector Management | Medium | v2.0 Phase 4 | [§ INT-004](#module-int-004--connector-management) |

**API Prefix:** `/api/v1/integration/`  
**Business Rule Prefix:** `BR-INT-xxx`  
**Minimum Edition:** Enterprise (Professional: read-only API docs portal)

### Downstream Artefact Index

| Artefact | Document ID |
|----------|-------------|
| Field Dictionary | ELU-FD-INT-001 … 004 |
| ERD Pack | ELU-ERD-INT |
| API Specification | ELU-API-INT |
| Flutter Screen Spec | ELU-UI-INT |
| RBAC Matrix | ELU-RBAC-INT |
| Test Case Pack | ELU-TC-INT |

### Platform Dependencies

| Dependency | Module | Role |
|------------|--------|------|
| Integration Framework | CPS-008 | Runtime execution, retry, circuit breaker |
| Audit Service | CPS-005 | API key usage, webhook delivery logs |
| Notification Engine | CPS-003 | Integration failure alerts |
| Rule Engine | CPS-002 | Webhook payload routing |

---

# Module INT-001 — REST API Management

**Document ID:** ELU-BFS-INT-001  
**Module:** INT-001 — REST API Management  
**Sub Module:** INT-001-001 — API Consumer Registry  
**Feature:** INT-001-001-001 — REST API Management  
**Domain:** INT  
**Priority / Phase / Release:** High · v2.0 · Phase 4  
**Example Tenant:** Euphoria

---

## 1. Business Objective

### 1.1 Why this module exists
Euphoria customers and partner systems (billing, data warehouse, mobile apps) must consume E-LinkUp **CRM**, **Sales**, and **Service** data programmatically. Ad-hoc sharing of user passwords is unacceptable. **REST API Management** provides tenant-scoped API consumers, keys, scopes, rate limits, and usage analytics for outbound integration by external systems calling **into** E-LinkUp.

### 1.2 Business value
- Secure machine-to-machine access with scoped permissions  
- Rate limiting protects platform stability  
- Usage dashboards for governance and chargeback  
- OpenAPI catalogue alignment for partner onboarding  

### 1.3 Business scope

| In Scope | Out of Scope |
|----------|--------------|
| API consumer registration | GraphQL gateway (v3.0) |
| API key / client credentials issuance | Full API marketplace |
| Scope assignment per domain object | SOAP endpoints |
| Rate limits, IP allowlist | |
| Usage metering & logs | |
| Developer portal (read OpenAPI) | |

### 1.4 Users involved
Tenant Admin, Platform Admin, System (API Gateway middleware), Developer (external — documented, not a CRM role).

### 1.5 Module reference
INT-001 · REST API Management · High · Phase 4 · v2.0 · Enterprise

---

## 2. Business Actors

| Actor | Type | Primary Actions | Secondary Actions |
|-------|------|-----------------|-------------------|
| Tenant Admin | Internal | Register consumers, rotate keys, set scopes | View usage |
| Platform Admin | Internal | Global rate limit policies, platform keys | — |
| External System | External | Call REST APIs with issued credentials | — |
| System (API Gateway) | System | Validate key, scope, rate limit | Audit log |
| System (Audit Service) | System | Log each authenticated API call | — |

---

## 3. Business Story

**Tenant Admin** at Euphoria registers an API Consumer *Finance Data Sync* for the internal data team. They assign scopes: `customer.read`, `invoice.read`, `ticket.read`. The system generates a **Client ID** and **Client Secret** (shown once). IP allowlist restricts calls to Euphoria office egress IPs.

The data team's ETL job authenticates via `POST /api/v1/auth/token` (client credentials grant — see INT-003), receives a short-lived JWT, and calls `GET /api/v1/crm/customers?updated_since=...`. Each call increments usage counters. When the job exceeds 1000 requests/hour, **API Gateway** returns `429 Too Many Requests` per BR-INT-005.

Quarterly, **Tenant Admin** reviews the usage dashboard, rotates the secret, and revokes an unused consumer *Legacy Mobile App*. All key rotations are audited.

---

## 4. Business Workflow

```text
Tenant Admin creates API Consumer
   ▼
Assign scopes + rate limit + IP allowlist
   ▼
Issue credentials (one-time secret display)
   ▼
External System: token exchange (INT-003)
   ▼
API Gateway: validate JWT scopes per route
   ▼
Business API executes (tenant_id from token)
   ▼
Log usage + audit
   ▼
[Admin] Rotate / Revoke as needed
```

| Step | Actor | Action | Input | Output | Engine |
|------|-------|--------|-------|--------|--------|
| 1 | Tenant Admin | Register consumer | Form | api_consumer | API |
| 2 | System | Generate credentials | Consumer | client_id, secret hash | API |
| 3 | External System | Obtain token | Credentials | JWT | INT-003 |
| 4 | API Gateway | Authorise request | JWT + route | Allow/deny | Middleware |
| 5 | System | Meter usage | Request metadata | usage_log | Redis/Celery |

---

## 5. Business States

| State Code | Label | Description | Next States |
|------------|-------|-------------|-------------|
| DRAFT | Draft | Consumer created, not active | ACTIVE, CANCELLED |
| ACTIVE | Active | Credentials valid | SUSPENDED, REVOKED |
| SUSPENDED | Suspended | Temporarily blocked | ACTIVE, REVOKED |
| REVOKED | Revoked | Permanent disable | — |

---

## 6. Business Rules

| Rule ID | Statement | Type | Severity | Enforcement |
|---------|-----------|------|----------|-------------|
| BR-INT-001 | API Consumer name unique per tenant | Validation | Error | DB |
| BR-INT-002 | Client secret stored as Argon2id hash only | Security | Error | DB |
| BR-INT-003 | Secret shown in full only at creation/rotation | Security | — | API |
| BR-INT-004 | JWT for API consumers shall not exceed scope granted | Security | Error | API Gateway |
| BR-INT-005 | Default rate limit 1000 req/hour per consumer (tenant override) | Security | Error | Redis |
| BR-INT-006 | Revoked consumers fail authentication immediately | Lifecycle | Error | API |
| BR-INT-007 | API calls must resolve tenant_id from token not header override | Security | Error | API |
| BR-INT-008 | Platform Admin may view but not use tenant secrets | Security | Error | RBAC |
| BR-INT-009 | Scopes use `{resource}.{action}` aligned with RBAC | Security | Error | Config |
| BR-INT-010 | Usage logs retained 90 days default (tenant policy) | Audit | Info | Config |

---

## 7. Database Impact

| Table | Type | Purpose | Tenant Scoped |
|-------|------|---------|---------------|
| api_consumer | Master | Consumer registry | Yes |
| api_consumer_scope | Link | Granted scopes | Yes |
| api_consumer_ip_allowlist | Master | IP CIDR rules | Yes |
| api_usage_log | Audit | Request metering | Yes |
| api_rate_limit_policy | Master | Limit definitions | Yes/Platform |

---

## 8. Relationships

| Parent | Child | Cardinality | On Delete |
|--------|-------|-------------|-----------|
| tenant | api_consumer | 1:N | Restrict |
| api_consumer | api_consumer_scope | 1:N | Cascade |
| api_consumer | api_usage_log | 1:N | Archive |

---

## 9. Field Groups

### api_consumer
General (name, description), Credentials (client_id, secret_hash), Limits (rate_limit_id), Network (IP allowlist), Status, Expiry, Audit

---

## 10. REST APIs

**Admin base:** `/api/v1/integration/api-consumers`

| Method | Path | Purpose | Permission |
|--------|------|---------|------------|
| POST | `/api/v1/integration/api-consumers` | Register consumer | `api_consumer.create` |
| GET | `/api/v1/integration/api-consumers` | List | `api_consumer.read` |
| GET | `/api/v1/integration/api-consumers/{id}` | Detail | `api_consumer.read` |
| PUT | `/api/v1/integration/api-consumers/{id}` | Update metadata | `api_consumer.update` |
| POST | `/api/v1/integration/api-consumers/{id}/rotate-secret` | Rotate secret | `api_consumer.update` |
| PATCH | `/api/v1/integration/api-consumers/{id}/status` | Suspend/revoke | `api_consumer.update` |
| GET | `/api/v1/integration/api-consumers/{id}/usage` | Usage stats | `api_consumer.read` |
| GET | `/api/v1/integration/openapi` | Tenant-filtered OpenAPI | `api_consumer.read` |

---

## 11. Flutter Screens

| Screen ID | Screen | Type | Actor |
|-----------|--------|------|-------|
| UI-INT-001-L | API Consumer List | List | Tenant Admin |
| UI-INT-001-C | API Consumer Create | Create | Tenant Admin |
| UI-INT-001-V | Consumer Detail + Scopes | View | Tenant Admin |
| UI-INT-001-U | Usage Dashboard | Dashboard | Tenant Admin |
| UI-INT-001-D | Developer Docs (OpenAPI) | View | Tenant Admin |

---

## 12. RBAC Permissions

`api_consumer.create`, `api_consumer.read`, `api_consumer.update`, `api_consumer.delete` — Tenant Admin only (Enterprise). Platform Admin: read aggregate usage cross-tenant (no PII).

---

## 13. Notifications

| Event | Channels | Recipients | Template |
|-------|----------|------------|----------|
| Consumer Created | Email | Tenant Admin | NTF-INT-001 |
| Secret Rotated | Email | Tenant Admin | NTF-INT-002 |
| Rate Limit Exceeded | Email, In-app | Tenant Admin | NTF-INT-003 |
| Consumer Revoked | Email | Tenant Admin | NTF-INT-004 |

---

## 14. Reports

| Report ID | Name | Audience |
|-----------|------|----------|
| RPT-INT-001 | API Usage by Consumer | Tenant Admin |
| RPT-INT-002 | Top Endpoints Called | Tenant Admin |
| RPT-INT-003 | Error Rate by Consumer | Platform Admin |

---

## 15. Audit Requirements
Consumer CRUD, scope change, status change, secret rotation, failed auth attempts (aggregated), rate limit breaches.

---

## 16. Acceptance Criteria

1. Create consumer returns client_secret once; subsequent GET never exposes secret.  
2. Token without `invoice.read` scope gets 403 on invoice endpoint.  
3. 429 returned when rate limit exceeded.  
4. Revoked consumer token rejected within 60 seconds.  
5. Tenant A consumer cannot access tenant B data.

---

## 17. Future Enhancements

| Version | Idea |
|---------|------|
| v2.5 | Per-endpoint quotas, burst allowance |
| v3.0 | GraphQL admin API, API product bundles |

---

# Module INT-002 — Webhook Management

**Document ID:** ELU-BFS-INT-002  
**Module:** INT-002 — Webhook Management  
**Sub Module:** INT-002-001 — Webhook Subscription  
**Feature:** INT-002-001-001 — Webhook Management  
**Domain:** INT  
**Priority / Phase / Release:** High · v2.0 · Phase 4  
**Example Tenant:** Euphoria

---

## 1. Business Objective

### 1.1 Why this module exists
External systems need **push** notification when E-LinkUp records change (e.g. new **Ticket**, **Invoice** paid). Polling is inefficient. Webhook Management lets Euphoria configure HTTPS endpoints, event subscriptions, signing secrets, and delivery retry policies.

### 1.2 Business value
- Real-time integration with ERP, Slack, Power Automate  
- Signed payloads prevent tampering  
- Delivery log aids debugging  
- Dead-letter queue for failed deliveries  

### 1.3 Business scope

| In Scope | Out of Scope |
|----------|--------------|
| Webhook endpoint registration | Kafka streaming (v3.0) |
| Event catalogue subscription | Bi-directional sync |
| HMAC signature | |
| Retry with exponential backoff | |
| Delivery log | |

### 1.4 Users involved
Tenant Admin, System (Celery worker, CPS-008), External endpoint (receiver).

### 1.5 Module reference
INT-002 · Webhook Management · High · Phase 4 · v2.0 · Enterprise

---

## 2. Business Actors

| Actor | Type | Primary Actions |
|-------|------|-----------------|
| Tenant Admin | Internal | Configure endpoints, events, secrets |
| System (Webhook Dispatcher) | System | Deliver payloads, retry |
| External System | External | Receive POST, verify signature |
| System (Rule Engine) | System | Optional payload filter/transform |

---

## 3. Business Story

Euphoria connects Microsoft Power Automate to receive events when **Tickets** are created or **Invoices** are issued. **Tenant Admin** registers webhook URL `https://flow.microsoft.com/.../elinkup`, selects events `ticket.created`, `invoice.issued`, and copies the **Signing Secret**.

When **Support Agent** creates a ticket, **Webhook Dispatcher** enqueues delivery. Payload JSON includes `event`, `tenant_id`, `timestamp`, `data` (ticket summary). Header `X-ELU-Signature: sha256=...` signs the body (BR-INT-015). On HTTP 200, delivery marked success. On 500, Celery retries 3 times with backoff; then dead-letter with alert to Tenant Admin.

---

## 4. Business Workflow

```text
Domain event occurs (e.g. ticket.created)
   ▼
Match active webhook subscriptions for tenant + event
   ▼
Build payload + sign
   ▼
Celery: POST to subscriber URL
   ├── 2xx ──► Log success
   └── non-2xx / timeout ──► Retry ──► Dead letter
   ▼
Notify admin on repeated failure (BR-INT-018)
```

---

## 5. Business States

### Webhook Endpoint
`DRAFT` → `ACTIVE` → `SUSPENDED` → `REVOKED`

### Delivery Attempt
`PENDING` → `DELIVERED` | `FAILED` → `DEAD_LETTER`

---

## 6. Business Rules

| Rule ID | Statement | Type | Severity | Enforcement |
|---------|-----------|------|----------|-------------|
| BR-INT-011 | Webhook URL must be HTTPS | Validation | Error | API |
| BR-INT-012 | Max 20 active webhooks per tenant (edition limit) | Validation | Error | API |
| BR-INT-013 | Event subscription must use catalogue enum | Validation | Error | API |
| BR-INT-014 | Payload size max 256 KB | Validation | Error | Dispatcher |
| BR-INT-015 | HMAC-SHA256 signature mandatory on outbound | Security | Error | Dispatcher |
| BR-INT-016 | Retry: 3 attempts, exponential backoff 1m/5m/30m | Lifecycle | — | Celery |
| BR-INT-017 | Timeout 30 seconds per delivery | — | — | HTTP client |
| BR-INT-018 | Dead-letter after retries notifies Tenant Admin | Notification | — | CPS-003 |
| BR-INT-019 | PII fields masked per tenant webhook policy | Security | Warning | Rule Engine |
| BR-INT-020 | Webhook test ping available without persisting event | — | Info | API |

---

## 7. Database Impact

| Table | Type | Purpose | Tenant Scoped |
|-------|------|---------|---------------|
| webhook_endpoint | Master | Subscriber URL config | Yes |
| webhook_event_subscription | Link | Events per endpoint | Yes |
| webhook_delivery_log | Audit | Delivery attempts | Yes |
| webhook_dead_letter | Audit | Failed final state | Yes |

---

## 8. Relationships

| Parent | Child | Cardinality | On Delete |
|--------|-------|-------------|-----------|
| webhook_endpoint | webhook_event_subscription | 1:N | Cascade |
| webhook_endpoint | webhook_delivery_log | 1:N | Archive |

---

## 9. Field Groups

### webhook_endpoint
General (name, url), Security (signing_secret_hash), Events (subscriptions), Retry Policy, Status, Audit

### webhook_delivery_log
Endpoint Reference, Event Type, Payload Hash, HTTP Status, Duration Ms, Attempt Number, Response Snippet, Timestamp

---

## 10. REST APIs

| Method | Path | Purpose | Permission |
|--------|------|---------|------------|
| POST | `/api/v1/integration/webhooks` | Create endpoint | `webhook.create` |
| GET | `/api/v1/integration/webhooks` | List | `webhook.read` |
| GET | `/api/v1/integration/webhooks/{id}` | Detail | `webhook.read` |
| PUT | `/api/v1/integration/webhooks/{id}` | Update | `webhook.update` |
| POST | `/api/v1/integration/webhooks/{id}/test` | Test ping | `webhook.update` |
| GET | `/api/v1/integration/webhooks/{id}/deliveries` | Delivery log | `webhook.read` |
| POST | `/api/v1/integration/webhooks/{id}/replay/{delivery_id}` | Replay | `webhook.update` |
| PATCH | `/api/v1/integration/webhooks/{id}/status` | Activate/suspend | `webhook.update` |
| GET | `/api/v1/integration/webhooks/events` | Event catalogue | `webhook.read` |

---

## 11. Flutter Screens

| Screen ID | Screen | Type |
|-----------|--------|------|
| UI-INT-002-L | Webhook List | List |
| UI-INT-002-C | Webhook Configure | Create/Edit |
| UI-INT-002-D | Delivery Log | List |
| UI-INT-002-T | Test Webhook | Action |

---

## 12. RBAC Permissions
`webhook.create`, `webhook.read`, `webhook.update`, `webhook.delete` — Tenant Admin (Enterprise).

---

## 13. Notifications

| Event | Recipients | Template |
|-------|------------|----------|
| Delivery Dead Letter | Tenant Admin | NTF-INT-010 |
| Webhook Suspended (auto) | Tenant Admin | NTF-INT-011 |

---

## 14. Reports

| Report ID | Name |
|-----------|------|
| RPT-INT-010 | Webhook Delivery Success Rate |
| RPT-INT-011 | Failed Deliveries Detail |

---

## 15. Audit Requirements
Endpoint CRUD, subscription changes, delivery attempts, replays, auto-suspend.

---

## 16. Acceptance Criteria

1. ticket.created fires webhook within 60s to subscribed endpoint.  
2. Invalid signature verification documented for receiver (test vector in docs).  
3. Retry occurs on 503; success on 200 stops retries.  
4. Dead-letter visible in UI after 3 failures.  
5. HTTP URL rejected at registration.

---

## 17. Future Enhancements

| Version | Idea |
|---------|------|
| v2.5 | Payload transformation templates |
| v3.0 | Event streaming bus (Kafka) |

---

# Module INT-003 — OAuth Management

**Document ID:** ELU-BFS-INT-003  
**Module:** INT-003 — OAuth Management  
**Sub Module:** INT-003-001 — OAuth Client  
**Feature:** INT-003-001-001 — OAuth Management  
**Domain:** INT  
**Priority / Phase / Release:** Medium · v2.0 · Phase 4  
**Example Tenant:** Euphoria

---

## 1. Business Objective

### 1.1 Why this module exists
**REST API Management** (INT-001) and third-party connectors require standards-based **OAuth 2.0** flows: client credentials for machine clients, authorization code for user-delegated apps. Central OAuth Management avoids bespoke token endpoints per module.

### 1.2 Business value
- Industry-standard security for partners  
- Token lifecycle (issue, refresh, revoke)  
- SSO foundation for Enterprise edition user federation  

### 1.3 Business scope

| In Scope | Out of Scope |
|----------|--------------|
| OAuth client registry (linked to api_consumer) | Full IdP (Okta replacement) |
| Client credentials grant | Device code flow (v2.5) |
| Authorization code + PKCE (Enterprise) | |
| Refresh token rotation | |
| Token revocation | |

### 1.4 Users involved
Tenant Admin, CRM User (delegated apps), External System, System (Auth Service).

### 1.5 Module reference
INT-003 · OAuth Management · Medium · Phase 4 · v2.0 · Enterprise

---

## 2. Business Actors

| Actor | Type | Primary Actions |
|-------|------|-----------------|
| Tenant Admin | Internal | Configure OAuth clients, redirect URIs |
| CRM User | Internal | Authorize delegated third-party app |
| External System | External | Token exchange, API calls |
| System (Auth Service) | System | Issue/validate/revoke tokens |

---

## 3. Business Story

Euphoria's mobile field app uses authorization code with PKCE. **Tenant Admin** registers OAuth Client linked to API Consumer, sets redirect URI `com.euphoria.elinkup://callback`, grants scopes `lead.read`, `activity.create`.

**Sales Executive** installs app, signs in via E-LinkUp login page, approves scopes. App receives authorization code, exchanges for access + refresh tokens. Access token JWT expires in 15 minutes; app uses refresh token (rotated each use per BR-INT-025). **Tenant Admin** revokes client; refresh fails immediately.

Machine integration uses `grant_type=client_credentials` without user context — tenant_id embedded in token claims.

---

## 4. Business Workflow

```text
[Client Credentials]
Client POST /auth/token (client_id, secret, grant_type)
   ▼
Validate consumer (INT-001) + scopes
   ▼
Issue JWT access token (no refresh)

[Authorization Code + PKCE]
User redirected to /oauth/authorize
   ▼
Login + consent screen
   ▼
Redirect with code
   ▼
App POST /auth/token (code, verifier)
   ▼
Issue access + refresh tokens
```

---

## 5. Business States

### OAuth Client
`ACTIVE` · `SUSPENDED` · `REVOKED`

### Refresh Token
`ACTIVE` · `ROTATED` · `REVOKED` · `EXPIRED`

---

## 6. Business Rules

| Rule ID | Statement | Type | Severity | Enforcement |
|---------|-----------|------|----------|-------------|
| BR-INT-021 | OAuth client must link to api_consumer record | Validation | Error | DB |
| BR-INT-022 | Redirect URI must match registered list exactly | Security | Error | Auth |
| BR-INT-023 | Authorization code expires in 10 minutes | Lifecycle | Error | Auth |
| BR-INT-024 | Access token TTL default 15 minutes | Security | — | Auth |
| BR-INT-025 | Refresh token rotation: old token invalidated on use | Security | Error | Auth |
| BR-INT-026 | PKCE required for public clients | Security | Error | Auth |
| BR-INT-027 | Revocation endpoint invalidates all descendant tokens | Lifecycle | Error | Auth |
| BR-INT-028 | Consent screen lists human-readable scope labels | — | Info | UI |
| BR-INT-029 | Client credentials grant prohibited for user-delegated scopes | Security | Error | Auth |
| BR-INT-030 | Token claims include tenant_id, client_id, scopes | Security | Error | JWT |

---

## 7. Database Impact

| Table | Type | Purpose | Tenant Scoped |
|-------|------|---------|---------------|
| oauth_client | Master | OAuth client metadata | Yes |
| oauth_redirect_uri | Master | Allowed redirects | Yes |
| oauth_authorization_code | Transaction | Short-lived codes | Yes |
| oauth_refresh_token | Transaction | Refresh token store (hash) | Yes |
| oauth_consent | Master | User consent records | Yes |

---

## 8. Relationships

| Parent | Child | Cardinality | On Delete |
|--------|-------|-------------|-----------|
| api_consumer | oauth_client | 1:1 | Cascade |
| oauth_client | oauth_redirect_uri | 1:N | Cascade |
| user | oauth_consent | 1:N | Cascade |

---

## 9. Field Groups

### oauth_client
Consumer Link, Client Type (confidential/public), Grant Types, PKCE Required, Token TTLs, Status, Audit

---

## 10. REST APIs

| Method | Path | Purpose | Permission |
|--------|------|---------|------------|
| POST | `/api/v1/integration/oauth/clients` | Register OAuth client | `oauth.configure` |
| GET | `/api/v1/integration/oauth/clients` | List | `oauth.read` |
| PUT | `/api/v1/integration/oauth/clients/{id}` | Update | `oauth.configure` |
| POST | `/api/v1/auth/token` | Token endpoint (public) | Client auth |
| GET | `/api/v1/oauth/authorize` | Authorization endpoint | User session |
| POST | `/api/v1/auth/revoke` | Revoke token | Client or user |
| GET | `/api/v1/integration/oauth/consents` | User consents admin view | `oauth.read` |

---

## 11. Flutter Screens

| Screen ID | Screen | Actor |
|-----------|--------|-------|
| UI-INT-003-L | OAuth Client List | Tenant Admin |
| UI-INT-003-C | OAuth Client Configure | Tenant Admin |
| UI-INT-003-CONSENT | User Consent Screen | CRM User |

---

## 12. RBAC Permissions
`oauth.configure`, `oauth.read` — Tenant Admin. User consent is self-service for own account.

---

## 13. Notifications

| Event | Recipients | Template |
|-------|------------|----------|
| New App Authorized | CRM User | NTF-INT-020 |
| OAuth Client Revoked | Tenant Admin | NTF-INT-021 |

---

## 14. Reports
RPT-INT-020 Active OAuth Clients; RPT-INT-021 Token Issuance Volume.

---

## 15. Audit Requirements
Client CRUD, authorization grants, token issue, refresh, revoke, consent grant/revoke.

---

## 16. Acceptance Criteria

1. Client credentials flow returns JWT with correct scopes.  
2. PKCE flow succeeds with valid verifier; fails without.  
3. Refresh rotation invalidates previous refresh token.  
4. Revoked client cannot obtain new tokens.  
5. Redirect URI mismatch returns error.

---

## 17. Future Enhancements

| Version | Idea |
|---------|------|
| v2.5 | Device authorization grant |
| v3.0 | External IdP federation (SAML/OIDC inbound) |

---

# Module INT-004 — Connector Management

**Document ID:** ELU-BFS-INT-004  
**Module:** INT-004 — Connector Management  
**Sub Module:** INT-004-001 — Connector Template  
**Feature:** INT-004-001-001 — Connector Management  
**Domain:** INT  
**Priority / Phase / Release:** Medium · v2.0 · Phase 4  
**Example Tenant:** Euphoria

---

## 1. Business Objective

### 1.1 Why this module exists
Repeated integration patterns (sync **Customer** to accounting software, push **Invoice** to Tally/Zoho) need configurable **Connectors** rather than custom code per tenant. Connector Management provides templates, credential vault references, field mappings, and scheduled sync jobs via **Integration Framework** (CPS-008).

### 1.2 Business value
- Faster time-to-integration for Euphoria implementations  
- Governed credential storage  
- Mapping UI reduces developer dependency  
- Sync status visibility for operations  

### 1.3 Business scope

| In Scope | Out of Scope |
|----------|--------------|
| Connector catalogue (prebuilt templates) | Unlimited custom Python scripts |
| Instance configuration per tenant | Real-time bi-directional ERP (v3.0) |
| Field mapping (source ↔ target) | |
| Scheduled sync (Celery) | |
| Sync run log | |

### 1.4 Users involved
Tenant Admin, Finance User (invoice connector), System (CPS-008, Celery).

### 1.5 Module reference
INT-004 · Connector Management · Medium · Phase 4 · v2.0 · Enterprise

---

## 2. Business Actors

| Actor | Type | Primary Actions |
|-------|------|-----------------|
| Tenant Admin | Internal | Enable connector, map fields, schedule |
| Finance User | Internal | Trigger manual sync, view logs |
| System (Integration Framework) | System | Execute sync jobs |
| External System | External | API target (accounting, etc.) |

---

## 3. Business Story

**Tenant Admin** enables connector template *Zoho Books — Customer & Invoice Export* for Euphoria. They store API credentials in encrypted connector vault (reference only in DB). Field mapping: E-LinkUp `customer.legal_name` → Zoho `contact_name`; `invoice.total_amount` → Zoho `total`.

Schedule: daily 02:00 IST. **Celery** triggers sync; CPS-008 fetches Customers modified since last watermark, transforms per mapping, POSTs to Zoho. Run log shows 45 records synced, 2 warnings (duplicate skipped). **Finance User** reviews log and manually re-runs failed records.

---

## 4. Business Workflow

```text
Select Connector Template
   ▼
Configure credentials + mapping + schedule
   ▼
Validate connection (test)
   ▼
Activate connector instance
   ▼
[Scheduled / Manual] Trigger sync job
   ▼
Extract → Transform → Load
   ▼
Write sync_run + sync_record_log
   ▼
On failure ──► Notify + retry policy
```

---

## 5. Business States

### Connector Instance
`DRAFT` → `ACTIVE` → `PAUSED` → `ERROR` → `ARCHIVED`

### Sync Run
`QUEUED` → `RUNNING` → `COMPLETED` | `COMPLETED_WITH_ERRORS` | `FAILED`

---

## 6. Business Rules

| Rule ID | Statement | Type | Severity | Enforcement |
|---------|-----------|------|----------|-------------|
| BR-INT-031 | Connector credentials encrypted at rest (AES-256) | Security | Error | DB |
| BR-INT-032 | Credentials never returned in API GET (mask only) | Security | Error | API |
| BR-INT-033 | Test connection required before activate | Validation | Error | API |
| BR-INT-034 | Field mapping must include required target fields | Validation | Error | UI |
| BR-INT-035 | Sync watermark prevents duplicate full loads | Calculation | — | Framework |
| BR-INT-036 | Max 10 active connector instances per tenant | Validation | Error | Edition |
| BR-INT-037 | Failed run retries max 2 times | Lifecycle | — | Celery |
| BR-INT-038 | Manual sync cannot run concurrent with scheduled | Concurrency | Warning | Redis lock |
| BR-INT-039 | Connector template version pinned on instance | Lifecycle | Info | DB |
| BR-INT-040 | PII export requires `connector.sync` + domain read scope | Security | Error | RBAC |

---

## 7. Database Impact

| Table | Type | Purpose | Tenant Scoped |
|-------|------|---------|---------------|
| connector_template | Master | Platform catalogue | No |
| connector_instance | Master | Tenant configuration | Yes |
| connector_credential | Master | Encrypted secrets ref | Yes |
| connector_field_mapping | Master | Field maps | Yes |
| connector_sync_run | Transaction | Run header | Yes |
| connector_sync_record_log | Audit | Per-record outcome | Yes |

---

## 8. Relationships

| Parent | Child | Cardinality | On Delete |
|--------|-------|-------------|-----------|
| connector_template | connector_instance | 1:N | Restrict |
| connector_instance | connector_field_mapping | 1:N | Cascade |
| connector_instance | connector_sync_run | 1:N | Archive |

---

## 9. Field Groups

### connector_instance
Template Reference, Name, Credentials Ref, Schedule (cron), Watermark, Status, Last Run Summary, Audit

### connector_field_mapping
Source Entity, Source Field, Target Field, Transform Rule, Required Flag

---

## 10. REST APIs

| Method | Path | Purpose | Permission |
|--------|------|---------|------------|
| GET | `/api/v1/integration/connectors/templates` | Catalogue | `connector.read` |
| POST | `/api/v1/integration/connectors/instances` | Create instance | `connector.configure` |
| GET | `/api/v1/integration/connectors/instances` | List | `connector.read` |
| PUT | `/api/v1/integration/connectors/instances/{id}` | Update | `connector.configure` |
| POST | `/api/v1/integration/connectors/instances/{id}/test` | Test connection | `connector.configure` |
| POST | `/api/v1/integration/connectors/instances/{id}/sync` | Manual sync | `connector.sync` |
| GET | `/api/v1/integration/connectors/instances/{id}/runs` | Sync history | `connector.read` |
| GET | `/api/v1/integration/connectors/runs/{run_id}/records` | Record log | `connector.read` |
| PATCH | `/api/v1/integration/connectors/instances/{id}/status` | Pause/activate | `connector.configure` |

---

## 11. Flutter Screens

| Screen ID | Screen | Type |
|-----------|--------|------|
| UI-INT-004-CAT | Connector Catalogue | List |
| UI-INT-004-CFG | Instance Configure | Wizard |
| UI-INT-004-MAP | Field Mapping | Editor |
| UI-INT-004-LOG | Sync Run Log | List |
| UI-INT-004-DET | Run Detail | View |

---

## 12. RBAC Permissions

| Permission | Tenant Admin | Finance User |
|------------|--------------|--------------|
| `connector.configure` | ✓ | — |
| `connector.read` | ✓ | ✓ |
| `connector.sync` | ✓ | ✓ |

---

## 13. Notifications

| Event | Recipients | Template |
|-------|------------|----------|
| Sync Failed | Tenant Admin | NTF-INT-030 |
| Sync Completed with Errors | Finance User | NTF-INT-031 |

---

## 14. Reports

| Report ID | Name |
|-----------|------|
| RPT-INT-030 | Connector Sync Summary |
| RPT-INT-031 | Failed Records by Connector |

---

## 15. Audit Requirements
Instance CRUD, credential update, mapping change, sync trigger, run outcomes.

---

## 16. Acceptance Criteria

1. Test connection validates credentials without persisting test data incorrectly.  
2. Scheduled sync runs at configured cron (±2 min).  
3. Field mapping error blocks activation.  
4. Credentials not exposed in API response.  
5. Watermark incremental sync only fetches delta records.

---

## 17. Future Enhancements

| Version | Idea |
|---------|------|
| v2.5 | Custom connector SDK |
| v3.0 | Real-time change data capture |

---

## Document Control

| Field | Value |
|-------|-------|
| Status | Ready for API pack authoring |
| Version | 1.0 |
| Owner | PMO |

---

*© Euphoria Infotech (I) Limited — E-LinkUp Integration Domain BFS Pack*
