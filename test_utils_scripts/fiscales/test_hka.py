#!/usr/bin/env python
# -*- coding: utf-8 -*-

import time
from controllers.pfhka import FiscalPrinter
# from tfhka import tf_ve_ifpython

port_comm = "COM9"

print("PRUEBAS CON PFHKA.PY")
pf = FiscalPrinter(port=port_comm)
try:
    # Verificar que el puerto de comunicación se está abriendo correctamente
    if pf.open_port():
        # Verificar que se está chuequeando la conexión con la impresora
        estado = pf.get_status()
        print(estado)
        # Verificar el valor de las variables de Status&Error
        if estado["status_code"] == 96 and estado["error_code"] == 64:
            # Verificar que se están solicitando los status S1,S3,S5 para control interno del sistema

            # print("")
            # print(pf.get_s3())
            # print("")

            # Verificar que se lee el modelo de impresora que está conectada (comando SV)
            # print(pf.get_sv())

            time.sleep(1)
            list_command = [
                "PJ2100",
                "PJ5001",
                "PJ3001",
                "PJ4301",
                "PJ6301",
                "iR*V-12345678-1",
                "iS*Cliente de Mostrador",
                "i01Linea Adicional 01",
                "@Esto es un Comentario",
                " 000000010000001000Producto 1",
                "p-1000",
                " 000000010000001000Producto 2",
                "p+1000",
                " 000000010000001000Producto 3",
                "q+000001000",
                " 000000010000001000Producto 4",
                "q-000001000",
                " 000000010000001000Producto 5",
                "k",
                "3",
                "y1234567890128",
                "205000000000200",
                "211000000000100",
                "3",
                "101",
            ]

            # for cmd in list_command:
            #     result = pf.send_command(cmd)
            #     print(f"{cmd} - {result}")

            # print(pf.get_s2())
            # pf.send_command("101")

            # time.sleep(2)
            # result = pf.get_s1()
            # print(result)

            time.sleep(2)
            response = pf.send_cmd("U0X")
            print(response)
            time.sleep(2)

            # "", "I1Z", U0X I1X

            # result = pf.get_s1()
            # print(result)

            # time.sleep(2)
            # print(pf.get_s5())

    pf.close_port()

except Exception as e:
    pf.close_port
    print(e)


# print("PRUEBAS CON TFHKA.PY")
# printer = tf_ve_ifpython()
# try:
#     if printer.OpenFpctrl(port_comm):
#         estado = printer.ReadFpStatus()
#         print(f"Estado: {estado}")

#     printer.CloseFpctrl()

# except Exception as e:
#     printer.CloseFpctrl()
#     print(e)
