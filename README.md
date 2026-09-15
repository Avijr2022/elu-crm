# E-LinkUp — Local Development Guide (Step 1 & 2)

**Product:** E-LinkUp (By Euphoria Infotech)  
**Tenant seed:** Euphoria (`EIIP001`)  
**Defaults:** Currency `INR` · Timezone `Asia/Kolkata` · FY start **1 April**  

Related: **ELU-DEV-001**, **ELU-ADR-001**, **ELU-RDM-001**, **ELU-MSL-001**

---

## What this step delivers

| Step | Deliverable |
|------|-------------|
| **1** | Repo scaffold: `Backend/`, `Frontend/`, `docker-compose.yml`, scripts |
| **2** | Platform Foundation: editions, tenant, org, roles, users, JWT login + seed Euphoria |

---

## Prerequisites

- **Docker Desktop** with **WSL 2** (Ubuntu must be VERSION 2 — check with `wsl -l -v`)  
  - If Ubuntu shows VERSION 1: `wsl --update` then `wsl --set-version Ubuntu 2`  
  - Enable Docker Desktop → Settings → Resources → WSL Integration → Ubuntu  
- Python 3.12+ recommended (3.14 may work; Docker API image uses 3.12)  
- Flutter SDK (for frontend)  
- Ports **15432** (Docker Postgres), **8000**, **9000/9001** free
  - Windows PostgreSQL 17/18 often occupy **5432/5433**; Docker defaults to **15432**
  - Some Windows hosts reserve port ranges covering **55432**, so **15432** is used instead

---

## Quick start (Windows)

### 1) Start infrastructure

```bat
cd D:\CRM
docker compose up -d postgres minio
```

Or double-click `Scripts\start-infra.bat`.

### 2) Run API on the host (recommended for local Flutter)

```bat
cd D:\CRM\Backend
python -m venv .venv
.venv\Scripts\activate
pip install -r requirements.txt
set DATABASE_URL=postgresql+psycopg://elinkup:elinkup_local@localhost:15432/elinkup
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

Or double-click `Scripts\start-api-host.bat`.

> Host API uses **localhost:15432** → Docker `postgres:5432`. Avoid Windows PostgreSQL on 5432/5433,
> and avoid host ports inside Windows reserved/dynamic ranges (which cover 55432 on some hosts).

On first boot the API will:

- Create PostgreSQL schemas/tables  
- Seed editions, tenant **Euphoria**, Head Office, roles, permissions  
- Create admin user  

### 3) Verify API

- Health: http://localhost:8000/health  
- Swagger: http://localhost:8000/docs  

**Login**

```http
POST http://localhost:8000/api/v1/auth/login
Content-Type: application/json

{
  "email": "admin@euphoriainfotech.com",
  "password": "Admin@12345",
  "tenant_code": "EIIP001"
}
```

**Me**

```http
GET http://localhost:8000/api/v1/auth/me
Authorization: Bearer <access_token>
```

### 4) Run Flutter (after `flutter create` assets exist)

```bat
cd D:\CRM\Frontend
flutter pub get
flutter run -d chrome --web-port 8080
```

Configure API base URL in `lib/core/network/api_config.dart` (default `http://127.0.0.1:8000`).

---

## Seed credentials

| Field | Value |
|-------|-------|
| Tenant code | `EIIP001` |
| Tenant name | Euphoria |
| Edition | PROFESSIONAL |
| Admin email | `admin@euphoriainfotech.com` |
| Admin password | `Admin@12345` |
| Currency | INR |
| Timezone | Asia/Kolkata |
| FY start | 01-Apr |

Change the password before any shared/demo environment.

---

## Alternative: API inside Docker

```bat
cd D:\CRM
docker compose up -d
```

API: http://localhost:8000  

---

## Project layout

```text
D:\CRM
  Backend/          FastAPI app (ELU-DEV-001)
  Frontend/         Flutter Web + Android
  Database/         Reference SQL + init schemas
  DevOps/           (reserved)
  Documentation/    Specs (ELU-*)
  ProjectStartupfiles/
  Scripts/          Local helpers
  docker-compose.yml
  .env.example
```

---

## Next step (Step 3)

CRM Lead module (`REQ-CRM-001`) — tables under `crm` schema + Flutter Lead List/Create.
