@echo off
chcp 65001 > nul

echo Pulse una tecla para iniciar
pause > null

REM ECHO Inicio del tiempo
for /f "tokens=1-3 delims=:." %%a in ("%TIME%") do (
    set /a "start_milliseconds=(((%%a*60)+1%%b %% 100)*60+1%%c %% 100)*1000+1%TIME:~9,2% %% 1000"
)

REM IntTFHKA SendCmd("PJ2100")
REM IntTFHKA SendCmd("PJ3000")
REM IntTFHKA SendCmd("PJ4302")
REM IntTFHKA SendCmd("PJ5000")

ECHO SE IMPRIME PROGRAMACION
IntTFHKA SendCmd("D")
REM IntTFHKA SendCmd("I0X")
REM ECHO IntTFHKA SendCmd("I0Z")


REM ECHO Fin del tiempo
for /f "tokens=1-3 delims=:." %%a in ("%TIME%") do (
    set /a "end_milliseconds=(((%%a*60)+1%%b %% 100)*60+1%%c %% 100)*1000+1%TIME:~9,2% %% 1000"
)

set /a "elapsed_milliseconds=end_milliseconds-start_milliseconds"
echo El tiempo de procesamiento fue de %elapsed_milliseconds% milisegundos.

echo Pulse una tecla para concluir
pause > null
goto :eof