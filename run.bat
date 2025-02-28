@echo off

for /f "delims=" %%i in ('python -c "import struct; print(struct.calcsize('P') * 8)"') do set "PYTHON_ARCH=%%i"
if not "%PYTHON_ARCH%"=="32" (
    echo Python no es de 32 bits. Por favor, instale la version de 32 bits.
    exit /b 1
)

for /f "delims=" %%i in ('python --version') do set "PYTHON_VERSION=%%i"
if not "%PYTHON_VERSION%"=="Python 3.10.11" (
    echo La versión de Python no es 3.10.11. Por favor, instale Python 3.10.11 o superior.
    exit /b 1
)

if not exist ".venv" (
    python -m venv .venv
)

call .venv\Scripts\activate
python.exe -m pip install --upgrade pip

call .venv\Scripts\activate
pip install -r requirements.txt

if exist "build" (
    rmdir /s /q build
)

call .venv\Scripts\activate
python.exe setup.py build

echo Proceso completado.
