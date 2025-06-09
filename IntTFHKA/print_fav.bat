@echo off
echo Pulse una tecla para iniciar
pause > null

REM echo Inicio del tiempo
for /f "tokens=1-3 delims=:." %%a in ("%TIME%") do (
    set /a "start_milliseconds=(((%%a*60)+1%%b %% 100)*60+1%%c %% 100)*1000+1%TIME:~9,2% %% 1000"
)

REM Inicio del bloque de código aquí
IntTFHKA SendCmd(iR*V131328526)
IntTFHKA SendCmd(iS*Maria Juana)
IntTFHKA SendCmd(i00DIR: Calle Unica de Siempre Viva Cruce de)
IntTFHKA SendCmd(i01TEL: 04148754142)
IntTFHKA SendCmd(i02REF: INV2023040001)
IntTFHKA SendCmd( 000000030000001000PRODUCTO EXENTO)
IntTFHKA SendCmd(101)
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