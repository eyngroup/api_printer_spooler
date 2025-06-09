@echo off
chcp 65001 > nul

echo Pulse una tecla para iniciar
pause > null

REM ECHO Inicio del tiempo
for /f "tokens=1-3 delims=:." %%a in ("%TIME%") do (
    set /a "start_milliseconds=(((%%a*60)+1%%b %% 100)*60+1%%c %% 100)*1000+1%TIME:~9,2% %% 1000"
)

REM ORIGINALES
IntTFHKA SendCmd(PE01LIBRE_01)
IntTFHKA SendCmd(PE02LIBRE_02)
IntTFHKA SendCmd(PE03LIBRE_03)
IntTFHKA SendCmd(PE04LIBRE_04)
IntTFHKA SendCmd(PE05LIBRE_05)
IntTFHKA SendCmd(PE06LIBRE_06)

IntTFHKA SendCmd(PE07LIBRE_07)
IntTFHKA SendCmd(PE08LIBRE_08)
IntTFHKA SendCmd(PE09LIBRE_09)
IntTFHKA SendCmd(PE10LIBRE_10)
IntTFHKA SendCmd(PE11LIBRE_11)
IntTFHKA SendCmd(PE12LIBRE_12)

IntTFHKA SendCmd(PE13LIBRE_13)
IntTFHKA SendCmd(PE14LIBRE_14)
IntTFHKA SendCmd(PE15LIBRE_15)
IntTFHKA SendCmd(PE16LIBRE_16)
IntTFHKA SendCmd(PE17LIBRE_17)
IntTFHKA SendCmd(PE18LIBRE_18)

IntTFHKA SendCmd(PE19LIBRE_19)
IntTFHKA SendCmd(PE20DIVISAS_1)
IntTFHKA SendCmd(PE21DIVISAS_2)
IntTFHKA SendCmd(PE22DIVISAS-3)
IntTFHKA SendCmd(PE23DIVISAS_4)
IntTFHKA SendCmd(PE24DIVISAS_5)

REM MODIFICACIONES
IntTFHKA SendCmd(PE01EfectivoBs)
IntTFHKA SendCmd(PE02EfectivoOtros)
IntTFHKA SendCmd(PE06CxC.Credito)

IntTFHKA SendCmd(PE07Deposito)
IntTFHKA SendCmd(PE08Transferencia)
IntTFHKA SendCmd(PE09T.Debito)
IntTFHKA SendCmd(PE10T.Credito)
IntTFHKA SendCmd(PE11PagoMovil)
IntTFHKA SendCmd(PE12BioPago)

IntTFHKA SendCmd(PE13CestaTicket)
IntTFHKA SendCmd(PE14Deposito)
IntTFHKA SendCmd(PE15Deposito)

IntTFHKA SendCmd(PE19Dif.IGTF)

IntTFHKA SendCmd(PE20DivisasUSD)
IntTFHKA SendCmd(PE21DivisasEUR)
IntTFHKA SendCmd(PE22DivisasOtros)



ECHO =====================
ECHO Programacion de FLAGS
ECHO =====================

ECHO Cerrar Cajero
IntTFHKA SendCmd("6")

REM ECHO Establecer Hora
REM IntTFHKA SendCmd("PF213000")

REM ECHO Establecer Fecha
REM IntTFHKA SendCmd("PG070124")

ECHO PJ2100 - Se mantiene la configuración estándar de los montos que maneja la impresora
ECHO  Precio del ítem 8 enteros + 2 decimales 0000000100   PAGO PARCIAL : 2010000000100
ECHO DESCUENTO Y RECARGO POR MONTO 7 enteros + 2 decimales  000000100
REM ECHO PJ2130 - Se mantiene la configuración estándar de los montos que maneja la impresora
REM ECHO  Precio del ítem (14 enteros + 2 decimales) 0000000000000100   PAGO PARCIAL : 2010000000000000100
REM ECHO DESCUENTO Y RECARGO POR MONTO 15 enteros + 2 decimales  00000000000000100
IntTFHKA SendCmd("PJ2100")

ECHO PJ3000 - Imprime el Codigo de Barra y no el número asociado 
REM ECHO PJ3001 - Imprime el código de barra con el número asociado bajo él código  
IntTFHKA SendCmd("PJ3000")

REM ECHO PJ4300 - Se activa el codigo de barra EAN13
ECHO PJ4302 - Se activa el codigo de barra CODE128
REM ECHO PJ4303 - Se activa el codigo de barra CODE39
REM ECHO PJ4304 - Se activa el codigo de barra QR
IntTFHKA SendCmd("PJ4302")

REM ECHO PJ5000 - Se desactiva para realizar cálculo del IGTF aplicando pagos en moneda extranjera
ECHO PJ5001 - Se activa para realizar cálculo del IGTF aplicando pagos en moneda extranjera
REM 199  Comando que es de uso obligatorio para cerrar los documentos fiscales (Factura de 
REM venta, Nota de Crédito, Nota de Débito) cuando el flag  50  está en  01. 
IntTFHKA SendCmd("PJ5001")

ECHO SE IMPRIME PROGRAMACION
IntTFHKA SendCmd("D")

REM ECHO Fin del tiempo
for /f "tokens=1-3 delims=:." %%a in ("%TIME%") do (
    set /a "end_milliseconds=(((%%a*60)+1%%b %% 100)*60+1%%c %% 100)*1000+1%TIME:~9,2% %% 1000"
)

set /a "elapsed_milliseconds=end_milliseconds-start_milliseconds"
echo El tiempo de procesamiento fue de %elapsed_milliseconds% milisegundos.

echo Pulse una tecla para concluir
pause > null
goto :eof