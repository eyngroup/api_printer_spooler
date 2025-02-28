@echo off
SET PROJECT_ROOT=%~dp0..
cd /d "%PROJECT_ROOT%"
call .venv\Scripts\activate.bat
set PYTHONPATH=%PROJECT_ROOT%
python test/run_proxy.py
pause
