@echo off
setlocal
cd /d "%~dp0"
where python >nul 2>nul
if errorlevel 1 (
  echo Python 3 is required. Install it from https://www.python.org/downloads/
  pause
  exit /b 1
)
python edf3_patch_builder.py
if errorlevel 1 pause
