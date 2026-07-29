@echo off
setlocal enabledelayedexpansion
REM GreenWeave -- one-command demo launcher (Windows)
REM Checks Docker, resets containers cleanly, rebuilds, and waits for a
REM healthy elastic_router before handing control back to the presenter.

cd /d "%~dp0"

echo [GreenWeave] Checking Docker...
docker info >nul 2>&1
if errorlevel 1 (
    echo [GreenWeave] ERROR: Docker is not running. Start Docker Desktop and try again.
    exit /b 1
)

docker compose version >nul 2>&1
if errorlevel 1 (
    set COMPOSE=docker-compose
) else (
    set COMPOSE=docker compose
)
echo [GreenWeave] Docker is running (using: %COMPOSE%)

if not exist ".env" (
    echo [GreenWeave] .env not found -- copying .env.example. Edit .env and add your API keys before routing real traffic.
    copy /y ".env.example" ".env" >nul
)

echo [GreenWeave] Stopping any existing GreenWeave containers...
%COMPOSE% down --remove-orphans

echo [GreenWeave] Building and starting the stack (this can take a few minutes on first run)...
%COMPOSE% up --build -d
if errorlevel 1 (
    echo [GreenWeave] ERROR: docker compose up failed. See output above.
    exit /b 1
)

echo [GreenWeave] Waiting for the Elastic Router to become healthy...
set HEALTHY=0
for /l %%i in (1,1,30) do (
    curl -sf http://localhost:8000/health >nul 2>&1
    if not errorlevel 1 (
        set HEALTHY=1
        goto :done_waiting
    )
    timeout /t 3 /nobreak >nul
)
:done_waiting

if "!HEALTHY!"=="1" (
    echo [GreenWeave] Elastic Router is healthy!
) else (
    echo [GreenWeave] WARNING: Elastic Router did not report healthy in time.
    echo [GreenWeave] Check logs with: %COMPOSE% logs elastic_router
)

echo.
echo [GreenWeave] GreenWeave is up:
echo     Dashboard:      http://localhost:8501
echo     Elastic Router: http://localhost:8000/health
echo     Redis:          localhost:6379
echo.
echo [GreenWeave] Tail logs with: %COMPOSE% logs -f
echo [GreenWeave] Stop the stack with: %COMPOSE% down

endlocal
