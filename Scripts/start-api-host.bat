@echo off
cd /d "%~dp0..\Backend"
if not exist .venv (
  python -m venv .venv
)
call .venv\Scripts\activate.bat
pip install -r requirements.txt
REM Host port 55432 maps to Docker postgres (avoids Windows PostgreSQL 17/18 on 5432/5433)
set DATABASE_URL=postgresql+psycopg://elinkup:elinkup_local@localhost:55432/elinkup
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
