@echo off
echo Pulse una tecla para iniciar
pause > null

REM Inicio del bloque de código aquí

REM FIN DEL CAJERO
REM IntTFHKA SendCmd("6")

REM HORA
REM IntTFHKA SendCmd("PF213000")

REM FECHA
REM IntTFHKA SendCmd("PG070124")

REM PROGRAMACION FLAGS

ECHO Se mantiene la configuración estándar de los montos que maneja la impresora
IntTFHKA SendCmd("PJ2100")

ECHO Se activa para realizar cálculo del IGTF aplicando pagos en moneda extranjera
IntTFHKA SendCmd("PJ5001")

ECHO Imprime el código de barra con el número asociado bajo él código
IntTFHKA SendCmd("PJ3001")

ECHO Se activa el codigo de barra CODE128
IntTFHKA SendCmd("PJ4300")

REM ECHO Se activa el codigo de barra QR
REM IntTFHKA SendCmd("PJ4304")

ECHO SE IMPRIME PROGRAMACION
IntTFHKA SendCmd("D")

REM Fin del bloque de código aquí


echo Pulse una tecla para concluir
pause > null
goto :eof