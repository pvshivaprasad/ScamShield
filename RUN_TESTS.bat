@echo off
setlocal
cd /d "%~dp0"
if not exist ".venv\Scripts\python.exe" (
  echo Run START_SCAMSHIELD.bat first to create the environment.
  pause
  exit /b 1
)
".venv\Scripts\python.exe" -m pytest -q
if errorlevel 1 pause
endlocal
