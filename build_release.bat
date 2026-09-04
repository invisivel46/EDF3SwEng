@echo off
setlocal
cd /d "%~dp0"
where python >nul 2>nul || (
  echo Python 3 is required to assemble the developer release.
  exit /b 1
)
python tools\scripts\package_release.py
if errorlevel 1 exit /b 1
echo.
echo Release created in dist\
