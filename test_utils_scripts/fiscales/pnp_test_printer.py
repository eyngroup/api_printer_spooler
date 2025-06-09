import pfpnp

pnp = pfpnp.FiscalPrinter("COM96")


def pf_credit():
    # Abrir factura fiscal (0x40)
    # [STX]E@[FS]MARIA DEL BARRIO[FS]V121234567[FS][127][FS][127][FS][127][FS][127][FS]T[FS][127][FS][127][ETX]0AF9
    """
    Inicio de datos (0x02), Número de secuencia (0x20 a 0x7F),
    Comandos (0x40), Separador de campo (0x1C),
    Campo 1: Razón social 1 máx. 38 caracteres, Separador de campo (0x1C),
    Campo 2: RIF del comprador Máx. 12 caracteres, Separador de campo (0x1C),
    Campo 3: Número de la factura en devolución, Separador de campo (0x1C),
    Campo 4: Serial de la máquina fiscal que realice la factura en devolución, Separador de campo (0x1C),
    Campo 5: Fecha de la factura en devolución, Separador de campo (0x1C),
    Campo 6: Hora de la factura en devolución, Separador de campo (0x1C),
    Campo 7: Para Factura (0x54) / Para Nota de Credito (0x44), Separador de campo (0x1C),
    Campo 8: Campo para uso futuro, Separador de campo (0x1C),
    Campo 9: Campo para uso futuro, Fin de datos (0x03), BCC (nnnn)
    """
    comando = b"\x02\x45\x40\x1cMARIA DEL BARRIO\x1cV121234567\x1c0000000001\x1cEOO9000001\x1c18/01/25\x1c\18:05\x1c\x44\x1c\x7f\x1c\x7f\x03"  # pylint: disable=C0301
    answer = pnp.pfsendcmd(comando)
    print(f"Respuesta: {answer}")

    # Imprimir Renglón en factura fiscal (0x42)
    """
    El monto total máximo de una línea es 9,999.999.999,99
    El campo “monto del ítem” NO incluye el “monto del impuesto”

    Inicio de datos (0x02), Número de secuencia (0x20 a 0x7F),
    Comandos (0x42), Separador de campo (0x1C), 
    Campo 1: Descripción de hasta 20 caracteres, Separador de campo (0x1C),
    Campo 2: Cantidad (nnnn.nnn) [se registra sin separador decimal], Separador de campo (0x1C),
    Campo 3: Monto del ítem (nnnnnn.nn) [se registra sin separador decimal], Separador de campo (0x1C),
    Campo 4: Tasa imponible (nnnn)[0000,0800,1600,3100] / 0001 = Percibido , Separador de campo (0x1C),
    Campo 5: Calificador de ítem de línea (0x4D) suma / (0x6D) resta, Separador de campo (0x1C),
    Campo 6: Campo para uso futuro, Separador de campo (0x1C),
    Campo 7: Campo para uso futuro, Separador de campo (0x1C),
    Campo 8: Campo para uso futuro, Fin de datos (0x03), BCC (nnnn)
    """

    # 2,000 unidades | 199,00 precio | 16,00 impuesto
    # [STX]6B[FS]Producto de Prueba N[FS]2000[FS]19900[FS]1600[FS]M[FS][127][FS][127][FS][127][ETX]0CD9
    comando = b"\x02\x36\x42\x1cProducto de Prueba N\x1c2000\x1c19900\x1c1600\x1c\x4d\x1c\x7f\x1c\x7f\x1c\x7f\x03"
    answer = pnp.pfsendcmd(comando)
    print(f"Respuesta: {answer}")

    # Imprimir texto en factura fiscal (0x41)  Máx. 40 caracteres [STX]FA[FS]SERIAL: ABC123EFD123[FS]S[ETX]09DD
    comando = b"\x02\x46\x41\x1cSERIAL: ABC123EFD123\x1c\x53\x03"
    answer = pnp.pfsendcmd(comando)
    print(f"Respuesta: {answer}")

    # Subtotal en factura fiscal (0x43) [STX]9E[FS]A[ETX]
    # [STX][34]E[FS]A[ETX]00C9
    comando = b"\x02\x39\x45\x1c\x41\x03"
    answer = pnp.pfsendcmd(comando)
    print(f"Respuesta: {answer}")

    # Cerrar factura fiscal (0x45) (\x4A) [STX]:E[FS]T[ETX]00F4
    # [STX][35]E[FS]T[ETX]00DD
    comando = b"\x02\x3a\x45\x1c\x41\x03"
    answer = pnp.pfsendcmd(comando)
    print(f"Respuesta: {answer}")

    return answer


def pf_invoice():
    # Abrir factura fiscal (0x40) [STX]E@[FS]MARIA DEL BARRIO[FS]V121234567[FS][127][FS][127][FS][127][FS][127][FS]T[FS][127][FS][127][ETX]0AF9
    """
    Inicio de datos (0x02), Número de secuencia (0x20 a 0x7F),
    Comandos (0x40), Separador de campo (0x1C),
    Campo 1: Razón social 1 máx. 38 caracteres, Separador de campo (0x1C),
    Campo 2: RIF del comprador Máx. 12 caracteres, Separador de campo (0x1C),
    Campo 3: Número de la factura en devolución, Separador de campo (0x1C),
    Campo 4: Serial de la máquina fiscal que realice la factura en devolución, Separador de campo (0x1C),
    Campo 5: Fecha de la factura en devolución, Separador de campo (0x1C),
    Campo 6: Hora de la factura en devolución, Separador de campo (0x1C),
    Campo 7: Para Factura (0x54) / Para Nota de Credito (0x44), Separador de campo (0x1C),
    Campo 8: Campo para uso futuro, Separador de campo (0x1C),
    Campo 9: Campo para uso futuro, Fin de datos (0x03), BCC (nnnn)
    """
    comando = (
        b"\x02\x45\x40\x1cMARIA DEL BARRIO\x1cV121234567\x1c\x7f\x1c\x7f\x1c\x7f\x1c\x7f\x1c\x54\x1c\x7f\x1c\x7f\x03"
    )
    answer = pnp.pfsendcmd(comando)
    print(f"Respuesta: {answer}")

    # Imprimir texto en factura fiscal (0x41)  Máx. 40 caracteres [STX]FA[FS]ESTE TEXTO ES ADICIONAL EN FISCAL[FS]S[ETX]09DD
    comando = b"\x02\x46\x41\x1cESTE TEXTO ES ADICIONAL EN FISCAL\x1c\x53\x03"
    answer = pnp.pfsendcmd(comando)
    print(f"Respuesta: {answer}")

    # Imprimir Renglón en factura fiscal (0x42)
    """
    El monto total máximo de una línea es 9,999.999.999,99
    El campo “monto del ítem” NO incluye el “monto del impuesto”

    Inicio de datos (0x02), Número de secuencia (0x20 a 0x7F),
    Comandos (0x42), Separador de campo (0x1C), 
    Campo 1: Descripción de hasta 20 caracteres, Separador de campo (0x1C),
    Campo 2: Cantidad (nnnn.nnn) [se registra sin separador decimal], Separador de campo (0x1C),
    Campo 3: Monto del ítem (nnnnnn.nn) [se registra sin separador decimal], Separador de campo (0x1C),
    Campo 4: Tasa imponible (nnnn)[0000,0800,1600,3100] / 0001 = Percibido , Separador de campo (0x1C),
    Campo 5: Calificador de ítem de línea (0x4D) suma / (0x6D) resta, Separador de campo (0x1C),
    Campo 6: Campo para uso futuro, Separador de campo (0x1C),
    Campo 7: Campo para uso futuro, Separador de campo (0x1C),
    Campo 8: Campo para uso futuro, Fin de datos (0x03), BCC (nnnn)
    """
    # 2,000 unidades | 199,00 precio | 16,00 impuesto [STX]6B[FS]Producto de Prueba N[FS]2000[FS]19900[FS]1600[FS]M[FS][127][FS][127][FS][127][ETX]0CD9
    comando = b"\x02\x36\x42\x1cProducto de Prueba N\x1c2000\x1c19900\x1c1600\x1c\x4d\x1c\x7f\x1c\x7f\x1c\x7f\x03"
    answer = pnp.pfsendcmd(comando)
    print(f"Respuesta: {answer}")

    # 5,000 unidades | 3,99 precio | 16,00 impuesto [STX]7B[FS]Producto de Prueba 2[FS]5000[FS]399[FS]1600[FS]M[FS][127][FS][127][FS][127][ETX]0C63
    comando = b"\x02\x37\x42\x1cProducto de Prueba 2\x1c5000\x1c399\x1c1600\x1c\x4d\x1c\x7f\x1c\x7f\x1c\x7f\x03"
    answer = pnp.pfsendcmd(comando)
    print(f"Respuesta: {answer}")

    # 1,355 unidades | 1,88 precio | 00,00 impuesto [STX]8B[FS]Producto de Prueba 3[FS]1355[FS]188[FS]0000[FS]M[FS][127][FS][127][FS][127][ETX]0C63
    comando = b"\x02\x38\x42\x1cProducto de Prueba 3\x1c1355\x1c188\x1c0000\x1c\x4d\x1c\x7f\x1c\x7f\x1c\x7f\x03"
    answer = pnp.pfsendcmd(comando)
    print(f"Respuesta: {answer}")

    # Subtotal en factura fiscal (0x43) [STX]9E[FS]A[ETX]
    # Este comando es útil para verificar que los montos acumulados en la impresora fiscal, a través del proceso de facturación,
    # concuerdan con los llevados por el software en el host. Luego de este comando se pueden emitir comandos de impresión de ítem adicionales.

    comando = b"\x02\x39\x45\x1c\x41\x03"
    answer = pnp.pfsendcmd(comando)
    print(f"Respuesta: {answer}")

    # Cerrar factura fiscal (0x45) (0x4A) SIN IGTF [STX]:E[FS]T[ETX]00F4
    # Cerrar factura fiscal (0x45) (0x4A) CON IGTF [STX]:E[FS]U[FS]100[ETX]00F4
    # Command qualifier options:
    # A - Indicates partial closure of active fiscal document
    # B - Indicates partial closure of invoice with IGTF added
    # T - Closes the active fiscal document
    # U - Closes the active fiscal document and adds IGTF

    comando = b"\x02\x3a\x45\x1c\x41\x03"
    answer = pnp.pfsendcmd(comando)
    print(f"Respuesta: {answer}")

    return answer


def pf_note():
    """Abrir documento no fiscal (\x48)"""
    comando = b"\x02\x44\x48\x03"
    answer = pnp.pfsendcmd(comando)
    print(f"Respuesta: {answer}")

    # Imprimir texto en documento no fiscal (\x49)
    comando = b"\x02\x45\x49\x1clinea de prueba numero 1\x03"
    answer = pnp.pfsendcmd(comando)
    print(f"Respuesta: {answer}")

    # Imprimir texto en documento no fiscal (\x49)
    comando = b"\x02\x46\x49\x1clinea de prueba numero 2\x03"
    answer = pnp.pfsendcmd(comando)
    print(f"Respuesta: {answer}")

    # Imprimir texto en documento no fiscal (\x49)
    comando = b"\x02\x35\x49\x1clinea de prueba numero 3\x03"
    answer = pnp.pfsendcmd(comando)
    print(f"Respuesta: {answer}")

    # Cerrar documento no fiscal (\x4A)
    comando = b"\x02\x36\x4a\x1c\x7f\x03"
    answer = pnp.pfsendcmd(comando)
    print(f"Respuesta: {answer}")

    return answer


def pf_report_x():
    """Reporte Z - Reporte X (\x39)"""
    comando = b"\x02\x45\x39\x1c\x58\x1c\x54\x03"
    answer = pnp.pfsendcmd(comando)
    print(f"Respuesta: {answer}")


def pf_report_z():
    """Reporte Z - Reporte X (\x39)"""
    comando = b"\x02\x45\x39\x1c\x5a\x1c\x54\x03"
    answer = pnp.pfsendcmd(comando)
    print(f"Respuesta: {answer}")


def pf_reset():
    """Reiniciado vía software"""
    comando = b"\x02\x07\x08\x09\x0a\x0b\x0c\x0d\x0e\x0f\x10\x11\x12\x13\x14\x15\x16\x17\x03"
    answer = pnp.pfsendcmd(comando)
    print(f"Respuesta: {answer}")


def pf_status_if():
    """Utilizado para evaluar el estado fiscal"""
    # [STX]E8[FS]N[ETX]00EC
    comando = b"\x02\x45\x38\x1c\x4e\x03"
    answer = pnp.pfsendcmd(comando)
    # [STX]E8[FS]0080[FS]0600[FS]0[FS]00[FS]45[FS]250118[FS]224950[FS]0[FS]0[FS]0[FS]0[ETX]0765
    print(f"Respuesta: {answer}")


def pf_serial():
    """Utilizado para el serial"""
    # [STX]E[128][ETX]00CA
    comando = b"\x02\x45\x80\x03"
    answer = pnp.pfsendcmd(comando)
    # [STX]E[128][ETX]0080[FS]0600[FS]EOO9000001[FS]J-29366870-0[FS]26.5[FS]1df0de[FS]22003c000947313037363132[FS]B[ETX]0FCB
    print(f"Respuesta: {answer}")


def pf_document_cancel():
    """Utilizado para cancelar un documento fiscal"""
    # [STX]7D[FS][FS][FS]C[FS][127][ETX]01B2
    comando = b"\x02\x45\x44\x1c\x1c\x1c\x43\x1c\x7f\x03"
    answer = pnp.pfsendcmd(comando)
    # [STX]7D[FS]0080[FS]8620[FS]ERROR 0[ETX]0446
    print(f"Respuesta: {answer}")


def pf_paper_cut():
    """Utilizado para el corte de papel"""
    # [STX]EK[ETX]0085
    comando = b"\x02\x45\x4b\x03"
    answer = pnp.pfsendcmd(comando)
    print(f"Respuesta: {answer}")


def pf_paper_feed():
    """Utilizado para avanzar el papel"""
    comando = b"\x02\x45\x50\x03"
    answer = pnp.pfsendcmd(comando)
    print(f"Respuesta: {answer}")


def pf_header_footer():
    """
    Este comando almacena una linea de datos fijos que aparece en el encabezado o pie de pág.
    Solo hasta un máximo de 2 lineas para el encabezado y para el pie de pag.
    """
    # Encabezados (0x5D) Pie de página (0x5E)
    comando = b"\x02\x45\x5d\x1cNumero de linea de datos fijos\x1cTexto fiscal de hasta 40 caracteres\x03"
    answer = pnp.pfsendcmd(comando)
    print(f"Respuesta: {answer}")


def pf_barcode():
    """Generar codigo de barras"""
    # Generar Código de Barra (0x54)
    comando = b"\x02\x45\x54\x1cCodigo de Barra Numerico\x03"
    answer = pnp.pfsendcmd(comando)
    print(f"Respuesta: {answer}")


print("=" * 80)
pnp.pfopen()

pf_serial()

pnp.pfclose()
print("=" * 80)

# Numeric characters
CHAR_0 = "\x30"  # 0	Número 0
CHAR_1 = "\x31"  # 1	Número 1
CHAR_2 = "\x32"  # 2	Número 2
CHAR_3 = "\x33"  # 3	Número 3
CHAR_4 = "\x34"  # 4	Número 4
CHAR_5 = "\x35"  # 5	Número 5
CHAR_6 = "\x36"  # 6	Número 6
CHAR_7 = "\x37"  # 7	Número 7
CHAR_8 = "\x38"  # 8	Número 8
CHAR_9 = "\x39"  # 9	Número 9

# Special and uppercase characters
CHAR_AA = "\x40"  # @	Arroba
CHAR_A = "\x41"  # A	Letra A mayúscula
CHAR_B = "\x42"  # B	Letra B mayúscula
CHAR_C = "\x43"  # C	Letra C mayúscula
CHAR_D = "\x44"  # D	Letra D mayúscula
CHAR_E = "\x45"  # E	Letra E mayúscula
CHAR_F = "\x46"  # F	Letra F mayúscula
CHAR_G = "\x47"  # G	Letra G mayúscula
CHAR_H = "\x48"  # H	Letra H mayúscula
CHAR_I = "\x49"  # I	Letra I mayúscula
CHAR_J = "\x4a"  # J	Letra J mayúscula
CHAR_K = "\x4b"  # K	Letra K mayúscula
CHAR_L = "\x4c"  # L	Letra L mayúscula
CHAR_M = "\x4d"  # M	Letra M mayúscula
CHAR_N = "\x4e"  # N	Letra N mayúscula
CHAR_O = "\x4f"  # O	Letra O mayúscula
CHAR_P = "\x50"  # P	Letra P mayúscula
CHAR_Q = "\x51"  # Q	Letra Q mayúscula
CHAR_R = "\x52"  # R	Letra R mayúscula
CHAR_S = "\x53"  # S	Letra S mayúscula
CHAR_T = "\x54"  # T	Letra T mayúscula
CHAR_U = "\x55"  # U	Letra U mayúscula
CHAR_V = "\x56"  # V	Letra V mayúscula
CHAR_W = "\x57"  # W	Letra W mayúscula
CHAR_X = "\x58"  # X	Letra X mayúscula
CHAR_Y = "\x59"  # Y	Letra Y mayúscula
CHAR_Z = "\x5a"  # Z	Letra Z mayúscula

# Control characters
STX = "\x02"  # Inicio de datos
SEC = "\x20"  # Número de secuencia
SEP = "\x1c"  # Separador de campo
ETX = "\x03"  # Fin de datos
DEL = "\x7f"
