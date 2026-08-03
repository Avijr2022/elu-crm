@echo off
REM Start local Postgres + MinIO for E-LinkUp
cd /d "%~dp0.."
docker compose up -d postgres minio
echo.
echo Postgres: localhost:55432  (user/db/password from .env.example; maps to container 5432)
echo MinIO API: localhost:9000  Console: localhost:9001
pause
