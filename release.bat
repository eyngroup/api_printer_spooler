@echo off
rem Empaqueta la compilacion para publicarla en un Release de GitHub.
rem Requiere haber ejecutado antes run.bat (genera build\ApiPS).
rem Genera dist\ApiPS-<version>.zip y dist\ApiPS-<version>.zip.sha256 (version tomada de handy\version.py).

uv --version || (
    echo Error: UV no esta instalado. Por favor, instale UV y vuelva a intentar.
    exit /b 1
)

uv run python scripts\make_release.py %*
if errorlevel 1 exit /b 1

echo Proceso completado.
