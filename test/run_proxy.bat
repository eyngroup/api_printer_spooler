@echo off
SET PROJECT_ROOT=%~dp0..
cd /d "%PROJECT_ROOT%"
call uv run test/run_proxy.py
pause
