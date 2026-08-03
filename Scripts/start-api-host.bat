@echo off
cd /d "%~dp0..\Backend"
if not exist .venv (
  python -m venv .venv
)
call .venv\Scripts\activate.bat
pip install -r requirements.txt
set DATABASE_URL=postgresql+psycopg://elinkup:elinkup_local@localhost:5432/elinkup
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
