@echo off
setlocal
cd /d "%~dp0"
title ScamShield - Startup
echo.
echo ScamShield - isolated startup
echo -----------------------------
where py >nul 2>nul
if errorlevel 1 (
  echo Python Launcher was not found. Install Python 3.12 from python.org.
  pause
  exit /b 1
)
if not exist ".venv\Scripts\python.exe" (
  echo Creating a dedicated Python 3.12 environment...
  py -3.12 -m venv .venv
  if errorlevel 1 (
    echo Could not create environment. Install Python 3.12 and try again.
    pause
    exit /b 1
  )
)
echo Installing pinned dependencies...
".venv\Scripts\python.exe" -m pip install --upgrade pip
if errorlevel 1 goto failed
".venv\Scripts\python.exe" -m pip install -r requirements.txt
if errorlevel 1 goto failed
echo Starting ScamShield. Keep this window open.
echo Open http://127.0.0.1:8000 if the browser does not open automatically.
".venv\Scripts\python.exe" run.py
if errorlevel 1 goto failed
exit /b 0
:failed
echo Startup failed. Copy the last 20 lines from this window for diagnosis.
pause
exit /b 1
