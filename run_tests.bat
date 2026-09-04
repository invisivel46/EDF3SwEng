@echo off
setlocal
cd /d "%~dp0"
python -m unittest discover -s tests -v
if errorlevel 1 pause
