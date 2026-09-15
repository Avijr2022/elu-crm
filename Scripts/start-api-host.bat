@echo off
cd /d "%~dp0..\Backend"
if not exist .venv (
  python -m venv .venv
)
call .venv\Scripts\activate.bat
pip install -r requirements.txt
REM Host port 15432 maps to Docker postgres (avoids Windows PostgreSQL 17/18 on 5432/5433,
REM and Windows reserved/dynamic ranges that cover 55432 on some hosts)
set DATABASE_URL=postgresql+psycopg://elinkup:elinkup_local@localhost:15432/elinkup
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
