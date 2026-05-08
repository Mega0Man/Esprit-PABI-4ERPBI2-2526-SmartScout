@echo off
setlocal EnableDelayedExpansion

:: ============================================================
::  MLOps — Run All Services
::  Opens MLflow + each FastAPI server + Unified Dashboard
::  in their own titled console windows, then opens browser.
:: ============================================================

title MLOps Launcher

color 0A

echo.
echo  ============================================================
echo    MLOps -- Starting All Services
echo  ============================================================
echo.

:: ── 1. Sanity-check: Python available? ──────────────────────
python --version >nul 2>&1
if errorlevel 1 (
    color 0C
    echo  [ERROR] Python not found on PATH.
    echo          Make sure your virtual environment is activated.
    echo.
    pause
    exit /b 1
)

:: ── 2. Sanity-check: uvicorn + mlflow available? ────────────
uvicorn --version >nul 2>&1
if errorlevel 1 (
    color 0E
    echo  [WARN]  uvicorn not found. FastAPI services may fail.
    echo.
    color 0A
)

mlflow --version >nul 2>&1
if errorlevel 1 (
    color 0E
    echo  [WARN]  mlflow not found. Run: pip install mlflow
    echo.
    color 0A
)

echo  Launching services in separate windows...
echo.

:: ── 3. MLflow shared server (start FIRST) ───────────────────
echo  [1/6] MLflow Server  (port 5000)
start "MLflow Server :5000" cmd /k ^
  "cd /d %~dp0..\mlflow && mlflow server --host 0.0.0.0 --port 5000 --backend-store-uri sqlite:///mlflow.db --default-artifact-root ./mlartifacts"

echo  Waiting for MLflow to initialise...
timeout /t 4 /nobreak >nul

:: ── 4. FastAPI services ──────────────────────────────────────
echo  [2/6] Scout Forecast FastAPI  (port 8001)
start "Scout Forecast :8001" cmd /k ^
  "cd /d %~dp0..\scout_forecast\scout_forecast && uvicorn api.main:app --host 0.0.0.0 --port 8001"

timeout /t 2 /nobreak >nul

echo  [3/6] Anomaly Detection FastAPI  (port 8004)
start "Anomaly Detection :8004" cmd /k ^
  "cd /d %~dp0..\ML_Models\annomalie && uvicorn api.main:app --host 0.0.0.0 --port 8004"

timeout /t 2 /nobreak >nul

echo  [4/6] Classification FastAPI  (port 8005)
start "Classification :8005" cmd /k ^
  "cd /d %~dp0..\ML_Models\classification && uvicorn api.main:app --host 0.0.0.0 --port 8005"

timeout /t 2 /nobreak >nul

echo  [5/6] Recommendation FastAPI  (port 8006)
start "Recommendation :8006" cmd /k ^
  "cd /d %~dp0..\ML_Models\recommandation && uvicorn api.main:app --host 0.0.0.0 --port 8006"

timeout /t 2 /nobreak >nul

echo  [6/6] Unified Dashboard  (port 5555)
start "Unified Dashboard :5555" cmd /k ^
  "cd /d %~dp0 && python app.py"

:: ── 5. Wait for dashboard to be ready ───────────────────────
echo.
echo  Waiting for Unified Dashboard to be ready...

set READY=0
for /L %%i in (1,1,20) do (
    if !READY!==0 (
        timeout /t 1 /nobreak >nul
        powershell -Command "try { $r=(Invoke-WebRequest -Uri 'http://localhost:5555' -UseBasicParsing -TimeoutSec 1).StatusCode; if ($r -lt 500) { exit 0 } else { exit 1 } } catch { exit 1 }" >nul 2>&1
        if !errorlevel!==0 set READY=1
    )
)

:: ── 6. Summary ──────────────────────────────────────────────
echo.
echo  ============================================================
echo    All services started:
echo  ============================================================
echo.
echo    MLflow UI           --^>  http://localhost:5000
echo    Scout Forecast API  --^>  http://localhost:8001
echo    Anomaly Detection   --^>  http://localhost:8004
echo    Classification      --^>  http://localhost:8005
echo    Recommendation      --^>  http://localhost:8006
echo    Unified Dashboard   --^>  http://localhost:5555
echo.

if !READY!==1 (
    echo  Opening browser...
    start "" "http://localhost:5555"
    start "" "http://localhost:5000"
) else (
    color 0E
    echo  [WARN] Dashboard did not respond -- try manually.
    color 0A
)

echo  ============================================================
echo   Close each window individually to stop a service.
echo  ============================================================
echo.
pause
endlocal
