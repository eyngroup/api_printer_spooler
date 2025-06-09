from flask import Flask
from flask import request, jsonify
from flask_cors import CORS, cross_origin
from impresora import Principal

app = Flask(__name__)

cors = CORS(app, resources={r"/*": {"origins": "*"}})
app.config["DEBUG"] = True
app.config['CORS_HEADERS'] = 'Content-Type'
configuration = True


@app.route('/')
def hello_world():  # poner aquí el código de la aplicación
    return 'Proxy Ejecutándose Correctamente! - en pruebas - '


@app.route("/api/comando", methods=['POST', 'GET'])
def command():
    try:
        cmd = request.args.get('C', default="D", type=str)

        principal = Principal()
        principal.recognize_port()
        principal.open_port()
        result = principal.send_cmd(cmd)
        principal.close_port()
        return jsonify(result)
    except AttributeError as e:
        print(f"Error: {e}")
        return jsonify({"Error": "Impresora no conectada"}), 503


# @app.route("/api/config", methods=['POST', 'GET'])
# def config():
#     try:
#         principal = Principal()
#         principal.recognize_port()
#         principal.open_port()
#         reporte = principal.programing()
#         principal.close_port()
#         return jsonify(reporte)
#     except AttributeError as e:
#         print(f"Error: {e}")
#         return jsonify({"Error": "Impresora no conectada"}), 503


# @app.route('/api/factura', methods=['POST'])
# @cross_origin()
# def api_all():
#     """Función para facturar.
#         :return: Número de factura
#         :rtype: json
#         """
#     global configuration
#     estados = {'e': ' ', 'g': '!', 'r': '"', 'a': '#'}
#     codigos = []
#     data = request.get_json(force=True)
#     items = data.get("invoice").get("items")
#     data_cliente = data.get("invoice").get("client")
#     nombre_cliente = f"{data_cliente.get('name')} {data_cliente.get('surname')}"
#     direccion = data_cliente.get("address")
#     documento_cliente = data_cliente.get("document").get("document")
#     tipo_doc = data_cliente.get("document").get("documentType")
#     telefono_cliente = data_cliente.get("phone")
#     pagos = data.get("invoice").get("payments")
#     data_cajero = data.get("invoice").get("cashier")
#
#     for x in items:
#         exento = x.get("exempt")
#         precio = str(x.get('price'))
#         p_entero, p_decimal = precio.split('.')
#         cantidad = str(float(x.get('amount')))
#         c_entera, c_decimal = cantidad.split('.')
#         producto = x.get('name')
#         codigos.append(
#             f"{estados.get('e') if exento == True else estados.get('g')}{('0' * (8 - len(p_entero))) + p_entero}{p_decimal + ('0' * (2 - len(p_decimal)))}\
# {('0' * (5 - len(c_entera))) + c_entera}{c_decimal + ('0' * (3 - len(c_decimal)))}{producto}")
#     try:
#         principal = Principal()
#         principal.recognize_port()
#         principal.open_port()
#         factura_anterior = principal.printer.n_factura()
#         if configuration:
#             principal.printer.SendCmd('PJ2100')
#             configuration = False
#         principal.invoice(lista_productos=codigos, cliente=nombre_cliente,
#                           direccion=direccion, documento="-".join([tipo_doc, documento_cliente]),
#                           telefono=telefono_cliente,
#                           pago=pagos, cajero=data_cajero)
#         principal.close_port()
#         principal.open_port()
#         factura_n = principal.printer.n_factura()
#         principal.close_port()
#         if factura_anterior != factura_n:
#             return jsonify({'invoice_number': factura_n})
#         else:
#             print(f"Es esta mierda: {factura_n}")
#             return jsonify({'Error': 'Error de máquina fiscal'}), 418
#     except AttributeError as e:
#         print(f"Error: {e}")
#         return jsonify({"Error": "Impresora no conectada"}), 503
#

# @app.route("/api/imprimirx", methods=['POST', 'GET'])
# def imprimir_x():
#     try:
#         principal = Principal()
#         principal.recognize_port()
#         principal.open_port()
#         reporte = principal.get_report_x()
#         principal.close_port()
#         principal.open_port()
#         principal.print_report_x()
#         principal.close_port()
#         return jsonify(reporte)
#     except AttributeError as e:
#         print(f"Error: {e}")
#         return jsonify({"Error": "Impresora no conectada"}), 503


# @app.route("/api/obtenerx", methods=['POST', 'GET'])
# def obtener_x():
#     try:
#         principal = Principal()
#         principal.recognize_port()
#         principal.open_port()
#         principal.get_report_x()
#         principal.close_port()
#         return jsonify({'report_x': True})
#     except AttributeError as e:
#         print(f"Error: {e}")
#         return jsonify({"Error": "Impresora no conectada"}), 503


# @app.route("/api/imprimirz", methods=['POST', 'GET'])
# def imprimir_z():
#     try:
#         principal = Principal()
#         principal.recognize_port()
#         principal.open_port()
#         principal.print_report_z()
#         principal.close_port()
#         return jsonify({"report_z": True})
#     except AttributeError as e:
#         print(f"Error: {e}")
#         return jsonify({"Error": "Impresora no conectada"}), 503


# @app.route("/api/reimprimir", methods=['POST'])
# def reimprimir():
#     """Función para reimprimir una factura."""
#     data = request.get_json(force=True)
#     n_factura = data.get("invoiceNumber")
#     try:
#         principal = Principal()
#         principal.recognize_port()
#         principal.open_port()
#         principal.reprint_invoices(n_factura)
#         principal.close_port()
#         return jsonify({"Executed": True})
#     except AttributeError as e:
#         print(f"Error: {e}")
#         return jsonify({"Error": 'Error en Maquina Fiscal'})

#
# @app.route('/api/devolucion', methods=['POST'])
# @cross_origin()
# def devolucion():
#     """Función para devolucion.
#         :return: Número de devolucion
#         :rtype: json
#         """
#     estados = {'e': '0', 'g': '1', 'r': '2', 'a': '3'}
#     codigos = []
#     data = request.get_json(force=True)
#     items = data.get("invoice").get("items")
#     data_cliente = data.get("invoice").get("client")
#     nombre_cliente = f"{data_cliente.get('name')} {data_cliente.get('surname')}"
#     direccion = data_cliente.get("address")
#     documento_cliente = data_cliente.get("document").get("document")
#     tipo_doc = data_cliente.get("document").get("documentType")
#     telefono_cliente = data_cliente.get("phone")
#     pagos = data.get("invoice").get("payments")
#     data_cajero = data.get("invoice").get("cashier")
#     n_factura = data.get('invoice').get('invoiceNumber')
#     serial = data.get('invoice').get('cashier').get('serial')
#     for x in items:
#         exento = x.get("exempt")
#         precio = str(x.get('price'))
#         p_entero, p_decimal = precio.split('.')
#         cantidad = str(float(x.get('amount')))
#         c_entera, c_decimal = cantidad.split('.')
#         producto = x.get('name')
#         codigos.append(
#             f"d{estados.get('e') if exento == True else estados.get('g')}{('0' * (8 - len(p_entero))) + p_entero}{p_decimal + ('0' * (2 - len(p_decimal)))}\
# {('0' * (5 - len(c_entera))) + c_entera}{c_decimal + ('0' * (3 - len(c_decimal)))}{producto}")
#     try:
#         principal = Principal()
#         principal.recognize_port()
#         principal.open_port()
#         nota_anterior = principal.printer.n_nota_credito()
#         principal.note_credit(lista_productos=codigos, cliente=nombre_cliente, direccion=direccion,
#                               documento="-".join([tipo_doc, documento_cliente]),
#                               telefono=telefono_cliente, pago=pagos, cajero=data_cajero, n_factura=n_factura,
#                               serial=serial)
#         principal.close_port()
#         principal.open_port()
#         nota_n = principal.printer.n_nota_credito()
#         principal.close_port()
#         print(nota_n)
#         if nota_anterior != nota_n:
#             return jsonify({'invoice_number': nota_n})
#         else:
#             return jsonify({'Error': 'Error de máquina fiscal'}), 418
#     except AttributeError as e:
#         print(f"Error: {e}")
#         return jsonify({"Error": "Impresora no conectada"}), 503


if __name__ == '__main__':
    app.run(host="127.0.0.1", port=5000)
