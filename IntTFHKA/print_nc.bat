@echo off
echo Pulse una tecla para iniciar
pause > null

REM echo Inicio del tiempo
for /f "tokens=1-3 delims=:." %%a in ("%TIME%") do (
    set /a "start_milliseconds=(((%%a*60)+1%%b %% 100)*60+1%%c %% 100)*1000+1%TIME:~9,2% %% 1000"
)

REM Inicio del bloque de código aquí
IntTFHKA SendCmd(iF*0000210041)
IntTFHKA SendCmd(iD*05/05/2023)
IntTFHKA SendCmd(iI*Z1F0008536)
IntTFHKA SendCmd(iR*V12345678)
IntTFHKA SendCmd(iS*CLIENTE)
IntTFHKA SendCmd(d1000000000002589200000000000001000Producto General)
IntTFHKA SendCmd(3)
IntTFHKA SendCmd(101)
IntTFHKA SendCmd(199)
REM Fin del bloque de código aquí

REM echo Fin del tiempo
for /f "tokens=1-3 delims=:." %%a in ("%TIME%") do (
    set /a "end_milliseconds=(((%%a*60)+1%%b %% 100)*60+1%%c %% 100)*1000+1%TIME:~9,2% %% 1000"
)

set /a "elapsed_milliseconds=end_milliseconds-start_milliseconds"
echo El tiempo de procesamiento fue de %elapsed_milliseconds% milisegundos.

echo Pulse una tecla para concluir
pause > null
goto :eof