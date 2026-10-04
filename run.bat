@echo off
rem Verificar la instalación de UV
uv --version || (
    echo Error: UV no está instalado. Por favor, instale UV y vuelva a intentar.
    exit /b 1
)

rem Sincronizar dependencias del entorno con UV
call uv sync

rem Limpiar directorio build si existe
if exist "build" (
    rmdir /s /q build
)

rem Construir el ejecutable con setup.py usando UV
uv run python setup.py build

echo Proceso completado.
