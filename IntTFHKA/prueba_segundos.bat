@echo off
echo Pulse una tecla para iniciar
pause > null

for /f "tokens=1-3 delims=:." %%a in ("%TIME%") do (
    set /a "start_seconds=(((%%a*60)+1%%b %% 100)*60)+1%%c %% 100"
)

REM Inicio del bloque de código aquí
IntTFHKA SendCmd(iR*V131328526)
IntTFHKA SendCmd(iS*Maria Juana)
IntTFHKA SendCmd(i00DIR: Calle Unica de Siempre Viva Cruce de)
IntTFHKA SendCmd(i01TEL: 04148754142)
IntTFHKA SendCmd(i02REF: INV2023040001)
IntTFHKA SendCmd(!000000000000010000000000000001000P02 Producto General)
IntTFHKA SendCmd(!000000000000010000000000000001000P02 Producto General)
IntTFHKA SendCmd(!000000000000010000000000000001000P02 Producto General)
IntTFHKA SendCmd(!000000000000010000000000000001000P02 Producto General)
IntTFHKA SendCmd(!000000000000010000000000000001000P02 Producto General)
IntTFHKA SendCmd(3)
IntTFHKA SendCmd(20500000000000000200)
IntTFHKA SendCmd(20300000000000000100)
IntTFHKA SendCmd(101)
IntTFHKA SendCmd(199)
REM Fin del bloque de código aquí

for /f "tokens=1-3 delims=:." %%a in ("%TIME%") do (
    set /a "end_seconds=(((%%a*60)+1%%b %% 100)*60)+1%%c %% 100"
)

set /a "elapsed_seconds=end_seconds-start_seconds"
echo El tiempo de procesamiento fue de %elapsed_seconds% segundos.
echo Pulse una tecla para concluir
pause > null
goto :eof