import os

contenido_epson = """
\033@  # Inicializar la impresora
Este es un documento de prueba con comandos Epson.
\033E  # Activar negrita
Texto en negrita
\033F  # Desactivar negrita
Texto normal
"""

directorio_trabajo = "C:\\PrtWrk\\PRT1"

nombre_archivo = "prueba_epson.txt"
ruta_archivo = os.path.join(directorio_trabajo, nombre_archivo)

with open(ruta_archivo, "w", encoding="ascii") as archivo:
    archivo.write(contenido_epson)

print(f"Archivo {nombre_archivo} enviado a {directorio_trabajo}")
