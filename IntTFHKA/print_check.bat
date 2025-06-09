@echo off
echo Pulse una tecla para iniciar
pause > null

REM echo Inicio del tiempo
for /f "tokens=1-3 delims=:." %%a in ("%TIME%") do (
    set /a "start_milliseconds=(((%%a*60)+1%%b %% 100)*60+1%%c %% 100)*1000+1%TIME:~9,2% %% 1000"
)

REM Inicio del bloque de código aquí
IntTFHKA CheckFprinter()
IntTFHKA SendCmd(3)
IntTFHKA SendCmd(101)
IntTFHKA CheckFprinter()
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