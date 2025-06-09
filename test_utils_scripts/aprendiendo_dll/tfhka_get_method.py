import clr
import sys

try:
    clr.AddReference(r"C:\DevProjets\API\api_printer_server\library\TfhkaNet.dll")
    from TfhkaNet.IF.VE import Tfhka

    impresora = Tfhka()

    # Obtener todos los métodos y atributos de la clase Tfhka
    methods = [method for method in dir(impresora) if callable(getattr(impresora, method))]
    attributes = [
        attr for attr in dir(impresora) if not callable(getattr(impresora, attr)) and not attr.startswith("__")
    ]

    print("Métodos disponibles en la clase Tfhka:")
    for method in methods:
        print(method)

    print("\nAtributos disponibles en la clase Tfhka:")
    for attr in attributes:
        print(attr)

except Exception as e:
    print(f"Ocurrió un error: {e}", file=sys.stderr)
