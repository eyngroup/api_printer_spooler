from flask import Flask, request, jsonify
from flask_cors import CORS
from datetime import datetime
import os

app = Flask(__name__)
CORS(app)  # Permitir CORS para pruebas desde navegador

# Token de prueba esperado
TOKEN_PRUEBA = "TOKEN_DE_PRUEBA"
# RIF esperado para la validación
RIF_ESPERADO = "J305468524"

# Archivo para almacenar el correlativo
SECUENCIA_FILE = "secuencia_factura.txt"

# Campos obligatorios y sus tipos esperados
CAMPOS_OBLIGATORIOS = {
    "rif": str,
    "nombrecliente": str,
    "rifcedulacliente": str,
    "idtipocedulacliente": int,
    # "emailcliente": str,
    "direccioncliente": str,
    "telefonocliente": str,
    "idtipodocumento": int,
    "subtotal": float,
    "exento": float,
    "tasag": float,
    "baseg": float,
    "impuestog": float,
    "total": float,
    "numerointerno": str,
    "sendmail": int,
    "tipomoneda": int,
    "tasadecambio": float,
    "cuerpofactura": list
}
# Puedes agregar más campos obligatorios según lo requieras

def get_next_correlativo():
    # Si el archivo no existe, empieza en 6706 (ejemplo inicial)
    if not os.path.exists(SECUENCIA_FILE):
        correlativo = 6706
    else:
        with open(SECUENCIA_FILE, "r") as f:
            try:
                correlativo = int(f.read().strip())
            except Exception:
                correlativo = 6706
    correlativo += 1
    with open(SECUENCIA_FILE, "w") as f:
        f.write(str(correlativo))
    return correlativo

@app.route('/facturacion', methods=['POST'])
def facturacion():
    print("\n--- Nueva petición recibida ---")
    print("Método:", request.method)
    print("Endpoint:", request.path)
    print("Headers:", dict(request.headers))
    print("Body:", request.get_data(as_text=True))

    # Validar Content-Type
    if not request.is_json:
        print("ERROR: Content-Type incorrecto")
        resp = {"success": False, "error": {"code": 5, "message": "Content-Type debe ser application/json"}, "data": None}
        print("Respuesta enviada:", resp)
        return jsonify(resp), 400

    # Validar Authorization header
    auth_header = request.headers.get('Authorization', '')
    print("Authorization header recibido:", auth_header)
    if not auth_header.startswith('Bearer '):
        print("ERROR: Falta o formato incorrecto en Authorization header")
        resp = {"success": False, "error": {"code": 1, "message": "Token no válido"}, "data": None}
        print("Respuesta enviada:", resp)
        return jsonify(resp), 401

    token = auth_header.split('Bearer ')[-1]
    print("Token recibido:", token)
    if token != TOKEN_PRUEBA:
        print("ERROR: Token inválido")
        resp = {"success": False, "error": {"code": 1, "message": "Token no válido"}, "data": None}
        print("Respuesta enviada:", resp)
        return jsonify(resp), 401

    # Obtener el JSON recibido
    data = request.get_json()
    print("JSON recibido:", data)

    # Validar campos obligatorios y tipos
    for campo, tipo in CAMPOS_OBLIGATORIOS.items():
        if campo not in data or data[campo] in (None, ""):
            print(f"ERROR: Falta campo obligatorio: {campo}")
            resp = {
                "success": False,
                "error": {"code": 5, "message": f"Valor <{campo}> es requerido"},
                "data": None
            }
            print("Respuesta enviada:", resp)
            return jsonify(resp), 400
        # Validar tipo de dato
        if campo != "cuerpofactura":
            if not isinstance(data[campo], tipo):
                # Permitir que float acepte int
                if tipo == float and isinstance(data[campo], int):
                    pass
                else:
                    print(f"ERROR: Tipo incorrecto para campo {campo}")
                    resp = {
                        "success": False,
                        "error": {"code": 2, "message": f"Valor <{campo}> no válido"},
                        "data": None
                    }
                    print("Respuesta enviada:", resp)
                    return jsonify(resp), 400

    # Validar rif corresponde al token
    if data["rif"].replace("-", "").upper() != RIF_ESPERADO.upper():
        print(f"ERROR: RIF no corresponde al token. Esperado: {RIF_ESPERADO}, Recibido: {data['rif']}")
        resp = {
            "success": False,
            "error": {"code": 3, "message": "RIF no corresponde al token"},
            "data": None
        }
        print("Respuesta enviada:", resp)
        return jsonify(resp), 400

    # Validar cuerpofactura
    if not isinstance(data["cuerpofactura"], list) or len(data["cuerpofactura"]) == 0:
        print("ERROR: cuerpofactura debe ser una lista no vacía")
        resp = {
            "success": False,
            "error": {"code": 5, "message": "Valor <cuerpofactura> es requerido"},
            "data": None
        }
        print("Respuesta enviada:", resp)
        return jsonify(resp), 400

    for idx, item in enumerate(data["cuerpofactura"]):
        # Validar campos obligatorios del item
        for campo_item in ["codigo", "descripcion", "precio", "cantidad", "tasa", "impuesto", "descuento", "exento", "monto"]:
            if campo_item not in item or item[campo_item] in (None, ""):
                print(f"ERROR: Falta campo obligatorio en cuerpofactura[{idx}]: {campo_item}")
                resp = {
                    "success": False,
                    "error": {"code": 5, "message": f"Valor <cuerpofactura[{idx}].{campo_item}> es requerido"},
                    "data": None
                }
                print("Respuesta enviada:", resp)
                return jsonify(resp), 400
        # Validar tipo de dato en montos
        for campo_num in ["precio", "cantidad", "tasa", "impuesto", "descuento", "monto"]:
            valor = item[campo_num]
            if not isinstance(valor, (float, int)):
                print(f"ERROR: Tipo incorrecto para campo cuerpofactura[{idx}].{campo_num}")
                resp = {
                    "success": False,
                    "error": {"code": 2, "message": f"Valor <cuerpofactura[{idx}].{campo_num}> no válido"},
                    "data": None
                }
                print("Respuesta enviada:", resp)
                return jsonify(resp), 400
        # Validar cálculo de impuesto
        precio = float(item["precio"])
        cantidad = float(item["cantidad"])
        tasa = float(item["tasa"])
        impuesto_esperado = round(precio * cantidad * tasa / 100, 2)
        impuesto_recibido = round(float(item["impuesto"]), 2)
        if impuesto_esperado != impuesto_recibido:
            print(f"ERROR: Impuesto mal calculado en cuerpofactura[{idx}]: esperado {impuesto_esperado}, recibido {impuesto_recibido}")
            resp = {
                "success": False,
                "error": {"code": 4, "message": f"Valores <impuesto> mal calculado en cuerpofactura[{idx}]"},
                "data": None
            }
            print("Respuesta enviada:", resp)
            return jsonify(resp), 400

    # Generar fecha y hora actual
    now = datetime.now()
    fecha = now.strftime("%Y%m%d")
    hora = now.strftime("%H:%M:%S")

    # Generar correlativo y numerodocumento únicos
    correlativo_num = get_next_correlativo()
    correlativo_str = f"{correlativo_num:08d}"
    numerodocumento = f"00-{correlativo_str}"

    # Responder con éxito
    response = {
        "success": True,
        "error": None,
        "data": {
            "numerodocumento": numerodocumento,
            "correlativo": correlativo_str,
            "fecha": fecha,
            "hora": hora
        }
    }
    print("Respuesta enviada:", response)
    return jsonify(response), 200

if __name__ == '__main__':
    import sys

    # Permitir especificar el puerto por argumento de línea de comandos
    port = 5000
    if len(sys.argv) > 1:
        try:
            port = int(sys.argv[1])
        except ValueError:
            print("Puerto inválido, usando 5000 por defecto.")

    app.run(host='0.0.0.0', port=port, debug=True)