from flask import Flask, render_template, make_response, jsonify, request
from flask_cors import CORS
import configparser
import logging
import serial.tools.list_ports
import socket
import webbrowser
from datetime import datetime
from controllers import tfhka

hka = tfhka.Tfhka()
app = Flask(__name__)
CORS(app)  # Esto habilitará CORS para todas las rutas

fecha_actual = datetime.now().strftime('%Y-%m-%d')
logging.basicConfig(
    filename=f"log_{fecha_actual}.log",
    level=logging.INFO,
    filemode='a',
    format='%(asctime)s %(levelname)s:%(name)s: %(message)s',
    datefmt='%H:%M:%S',
    encoding='utf-8'  # Agrega esta línea para especificar la codificación
)

logging.getLogger('werkzeug').setLevel(logging.ERROR)

config = configparser.ConfigParser()
config.read('config.ini')

# Obtain configuration values
auto_ip = config.getboolean("server", "auto_ip")
auto_com = config.getboolean("server", "auto_com")
auto_browser = config.getboolean("server", "auto_browser")
test = config.getboolean("server", "debug")
host_ip = config.get("server", "host")
port_ip = config.getint("server", "port")
port_com = config.get("server", "com")


def open_browser():
    url = f"http://{host_ip}:{port_ip}"
    webbrowser.open(url)


def get_ip():
    s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    try:
        s.connect(('10.255.255.255', 1))
        local_ip = s.getsockname()[0]
    except Exception as e:
        logging.warning(e)
        local_ip = '127.0.0.1'
    finally:
        s.close()
    logging.warning(f"Selected IP Address: http://{local_ip}:{port_ip}")
    return local_ip


def get_com():
    list_ports = serial.tools.list_ports.comports()
    available_ports = [puerto.device for puerto in list_ports]
    if len(available_ports) == 0:
        available_ports = ["COM12", "COM11", "COM10", "COM9", "COM8", "COM7", "COM6", "COM5", "COM4", "COM3"]
        for port in available_ports:
            try:
                resp = hka.OpenFpctrl(port)
                if resp:
                    logging.warning(f"COM Port Selected: {port}")
                    return port
            except Exception as e:
                logging.error(e)
                return None

    port = available_ports[0]
    logging.warning(f"COM Port Available: {port}")
    return port


def status_description(status):
    status_dict = {
        "12": 'En modo fiscal, carga completa de la memoria fiscal y emisión de documentos no fiscales',
        "11": 'En modo fiscal, carga completa de la memoria fiscal y emisión de documentos fiscales',
        "10": 'En modo fiscal, carga completa de la memoria fiscal y en espera',
        "9": 'En modo fiscal, cercana carga completa de la memoria fiscal y en emisión de documentos no fiscales',
        "8": 'En modo fiscal, cercana carga completa de la memoria fiscal y en emisión de documentos no fiscales',
        "7": 'En modo fiscal, cercana carga completa de la memoria fiscal y en espera',
        "6": 'En modo fiscal y en emisión de documentos no fiscales',
        "5": 'En modo fiscal y en emisión de documentos fiscales',
        "4": 'En modo fiscal y en espera',
        "3": 'En modo prueba y en emisión de documentos no fiscales',
        "2": 'En modo prueba y en emisión de documentos fiscales',
        "1": 'En modo prueba y en espera',
        "0": 'Status Desconocido'
    }
    return status_dict.get(status, 'Status Unknown')


@app.route('/')
def home():
    logging.info("Proxy Server Home Page")
    return render_template('index.html')


@app.route('/api/printer_config', methods=['GET'])
def printer_config():
    user_string = request.args.get('user_string', default="", type=str)
    try:
        if not user_string:
            raise ValueError("Parameter cannot be empty")
        if user_string.isdigit():
            raise ValueError("Parameter cannot be a number")
        pf_open: bool = hka.OpenFpctrl(port_com)

        if pf_open:
            if user_string == "ALL":
                res = hka.SendCmd("PE01Efectivo")
                logging.warning(f"Command: PE01Efectivo ; Result: {res}")
                res = hka.SendCmd("PE02EfectivoBs")
                logging.warning(f"Command: PE02EfectivoBs ; Result: {res}")
                res = hka.SendCmd("PE03EfectivoOtro")
                logging.warning(f"Command: PE03EfectivoOtro ; Result: {res}")
                res = hka.SendCmd("PE04CryptoMoneda")
                logging.warning(f"Command: PE04CryptoMoneda ; Result: {res}")
                res = hka.SendCmd("PE05CxCobrar")
                logging.warning(f"Command: PE05CxCobrar ; Result: {res}")
                res = hka.SendCmd("PE06Deposito")
                logging.warning(f"Command: PE06Deposito ; Result: {res}")
                res = hka.SendCmd("PE07Transferencia")
                logging.warning(f"Command: PE07Transferencia ; Result: {res}")
                res = hka.SendCmd("PE08Cheque")
                logging.warning(f"Command: PE08Cheque ; Result: {res}")
                res = hka.SendCmd("PE09TDebito")
                logging.warning(f"Command: PE09TDebito ; Result: {res}")
                res = hka.SendCmd("PE10TCredito")
                logging.warning(f"Command: PE10TCredito ; Result: {res}")
                res = hka.SendCmd("PE11PagoMovil")
                logging.warning(f"Command: PE11PagoMovil ; Result: {res}")
                res = hka.SendCmd("PE12BioPago")
                logging.warning(f"Command: PE12BioPago ; Result: {res}")
                res = hka.SendCmd("PE13PagoElectronico")
                logging.warning(f"Command: PE17PagoElectronico ; Result: {res}")
                res = hka.SendCmd("PE14CestaTicket")
                logging.warning(f"Command: PE14CestaTicket ; Result: {res}")
                res = hka.SendCmd("PE15NoAsignado")
                logging.warning(f"Command: PE15NoAsignado ; Result: {res}")
                res = hka.SendCmd("PE16NoAsignado")
                logging.warning(f"Command: PE16NoAsignado ; Result: {res}")
                res = hka.SendCmd("PE17NoAsignado")
                logging.warning(f"Command: PE17NoAsignado ; Result: {res}")
                res = hka.SendCmd("PE18NoAsignado")
                logging.warning(f"Command: PE18NoAsignado ; Result: {res}")
                res = hka.SendCmd("PE19DifIGTF")
                logging.warning(f"Command: PE19DifIGTF ; Result: {res}")
                res = hka.SendCmd("PE20Divisas")
                logging.warning(f"Command: PE20Divisas ; Result: {res}")
                res = hka.SendCmd("PE21DivisasUSD")
                logging.warning(f"Command: PE21DivisasUSD ; Result: {res}")
                res = hka.SendCmd("PE22DivisasEUR")
                logging.warning(f"Command: PE22DivisasEUR ; Result: {res}")
                res = hka.SendCmd("PE23DivisasPES")
                logging.warning(f"Command: PE23DivisasPES ; Result: {res}")
                res = hka.SendCmd("PE24DivisasOtros")
                logging.warning(f"Command: PE24DivisasOtros ; Result: {res}")

                res = hka.SendCmd("6")
                logging.warning(f"Command: Close Cashier ; Result: {res}")

                now = datetime.now()
                hora_formateada = "PF" + now.strftime('%H%M%S')
                res = hka.SendCmd(hora_formateada)
                logging.warning(f"Command: Set Time {hora_formateada} ; Result: {res}")

                fecha_formateada = "PG" + now.strftime('%d%m%y')
                res = hka.SendCmd(fecha_formateada)
                logging.warning(f"Command: Set Date {fecha_formateada} ; Result: {res}")

                res = hka.SendCmd("PJ2100")
                logging.warning(f"Command: PJ2100 ; Result: {res}")

                res = hka.SendCmd("PJ3000")
                logging.warning(f"Command: PJ3000 ; Result: {res}")

                res = hka.SendCmd("PJ4302")
                logging.warning(f"Command: PJ4302 ; Result: {res}")

                res = hka.SendCmd("PJ5000")
                logging.warning(f"Command: PJ5000 ; Result: {res}")

                # res = hka.SendCmd("PT11600108001310010300")
                # logging.warning(f"Command: TAX ; Result: {res}")

                # res = hka.SendCmd("PJ3500")
                # logging.warning(f"Command: PJ3500 ; Result: {res}")

                res = hka.SendCmd("D")
                logging.warning(f"Command: D ; Result: {res}")
            else:
                res = hka.SendCmd(user_string)

            flag = hka.GetS3PrinterData().AllSystemFlags()
            # Payment = hka.GetS4PrinterData().AllMeansOfPayment()
            hka.CloseFpctrl()
            logging.warning(f"Command: {user_string} ; Flags: {flag}")
            status = {"status": f"Command: {user_string} ; Result: {res}"}
            return make_response(jsonify(status), 200)
        logging.error(f"Connection Fault, Command '{user_string}' NOT Processed")
        return "No connection with printer"
    except ValueError as ve:
        return str(ve)
    except Exception as e:
        hka.CloseFpctrl()
        logging.critical(type(e).__name__)
        return str(e)


@app.route('/api/printer_status', methods=['GET'])
def printer_status():
    var1, var2, var3 = 0, 0, 0
    try:
        pf_open: bool = hka.OpenFpctrl(port_com)
        if pf_open:
            res = hka.ReadFpStatus()
            var1, var2, var3 = res.split(maxsplit=2)
            hka.CloseFpctrl()

        var1 = status_description(var1)
        logging.warning(f"{var1} {var2} {var3}")
        return make_response(jsonify({"message": f"{var1} {var2} {var3}"}), 200)
    except Exception as e:
        hka.CloseFpctrl()
        logging.critical(type(e).__name__)
        return make_response(jsonify({"error": str(e)}), 400)


@app.route('/api/printer_model', methods=['GET'])
def printer_model():
    models = {
        "Z7C": "HKA80", "Z7A": "HKA112", "Z1A": "SRP-270", "Z1B": "SRP-350", "Z1E": "SRP-280",
        "Z1F": "SRP-812", "ZPA": "HSP7000", "Z6A": "TALLY 1125", "Z6B": "DT-230", "Z6C": "TALLY 1140",
        "ZYA": "P3100DL", "ZZH": "PP9", "ZZP": "PP9-PLUS"
    }
    try:
        pf_open: bool = hka.OpenFpctrl(port_com)
        if pf_open:
            model = hka.GetSVPrinterData()
            tipo = model.Pmodel()
            logging.warning(f"Model Type: {tipo}")
            model_name = models.get(tipo, "Unknown")
            hka.CloseFpctrl()
        else:
            model_name = "No Connection"

        logging.warning(f"Printer Model Result: {model_name}")
        status = {"message": f"Printer Model: {model_name}"}
        return make_response(jsonify(status), 200)
    except Exception as e:
        hka.CloseFpctrl()
        logging.critical(type(e).__name__)
        return make_response(jsonify({"error": str(e)}), 400)


@app.route('/api/printer_x', methods=['GET'])
def printer_x():
    try:
        pf_open: bool = hka.OpenFpctrl(port_com)
        if pf_open:
            hka.SendCmd("I0X")
            hka.CloseFpctrl()
        logging.warning(f"X Report Printing: {pf_open}")
        status = {"message": f"Print Report X: {pf_open}"}
        return make_response(jsonify(status), 200)
    except Exception as e:
        hka.CloseFpctrl()
        logging.critical(type(e).__name__)
        return make_response(jsonify({"error": str(e)}), 400)


@app.route('/api/printer_z', methods=['GET'])
def printer_z():
    try:
        pf_open: bool = hka.OpenFpctrl(port_com)
        if pf_open:
            hka.SendCmd("I0Z")
            hka.CloseFpctrl()
        logging.warning(f"Z Report Printing: {pf_open}")
        status = {"message": f"Print Report X Z: {pf_open}"}
        return make_response(jsonify(status), 200)
    except Exception as e:
        hka.CloseFpctrl()
        logging.critical(type(e).__name__)
        return make_response(jsonify({"error": str(e)}), 400)


@app.route('/api/total_daily', methods=['GET'])
def total_daily():
    try:
        pf_open: bool = hka.OpenFpctrl(port_com)
        if pf_open:
            get_s1 = hka.GetS1PrinterData()
            report = get_s1.TotalDailySales()
            hka.CloseFpctrl()
            info = {
                "Número de Registro impresora fiscal": get_s1.RegisteredMachineNumber(),
                "RIF registrado de la maquina": get_s1.Rif(),
                "Cant. de Facturas Emitidas en el día": get_s1.QuantityOfInvoicesToday(),
                "Cantidad de Documentos No Fiscales": get_s1.QuantityNonFiscalDocuments(),
                "Contador de Reportes Diarios (Z)": get_s1.DailyClosureCounter()
            }
            logging.warning(f"Total Accumulated Amount for the Day= {report}")
            return "INFORMACIÓN DE ESTATUS S1 DE LA IMPRESORA FISCAL:  " + ' | '.join(
                f"{key}: {value}" for key, value in info.items())
        else:
            logging.error(f"Connection failure for totals")
            return {"message": f"No connection to printer to view totals"}
    except Exception as e:
        hka.CloseFpctrl()
        logging.critical(type(e).__name__)
        return make_response(jsonify({"error": str(e)}), 400)


@app.route('/api/invoice', methods=['POST'])
def invoice():
    data = request.get_json()
    print(data)

    if 'params' in data:
        if data['params']['type']:
            type_value = data['params']['type'][0]
        else:
            type_value = 'FAV'
        cmd_list = data['params']['cmd']
    else:
        #type_value = data['type'][0]
        cmd_list = data['cmd']
    # type_value = 'FAV'

    try:
        pf_open: bool = hka.OpenFpctrl(port_com)
        if pf_open:
            logging.info("˅" * 40)
            logging.info(f"Port {port_com} Open")
            for i in cmd_list:
                resp = hka.SendCmd(i)
                logging.info(f"{resp} {i}")
                print(f"{resp} {i}")

            get_s1 = hka.GetS1PrinterData()
            printer_serial = get_s1.RegisteredMachineNumber()
            if printer_serial == "":
                printer_serial = "Z1A1234567"
            printer_report_z = get_s1.DailyClosureCounter() + 1
            if printer_report_z == 1 or printer_report_z == 0:
                printer_report_z = 99999999
            if type_value == "FAV":
                printer_last_number = get_s1.LastInvoiceNumber()
            elif type_value == "CRE":
                printer_last_number = get_s1.LastNCNumber()
            elif type_value == "DEB":
                printer_last_number = get_s1.LastDebtNoteNumber()
            else:
                printer_last_number = 0

            if printer_last_number == 0:
                printer_last_number = 99999999

            printer_date = get_s1.CurrentPrinterDate()
            formatted_date = datetime.strptime(printer_date, '%d-%m-%Y').strftime('%Y-%m-%d')

            response_json = {
                "PrinterSerial": printer_serial, "PrinterCounterZ": printer_report_z,
                "PrinterNumber": printer_last_number, "PrinterDate": formatted_date,
                "PrinterBase": 0, "PrinterTax": 0, "PrinterIgt": 0
            }

            logging.info(f"Number: {type_value}{printer_last_number}")
            hka.CloseFpctrl()
            logging.info(f"Port {port_com} Closed")
            # logging.info("˄" * 20)
            logging.info("=" * 40)
            # return make_response(jsonify(response_json, ensure_ascii=False), 200)
            return make_response(response_json, 200)

        logging.error(f"Failure to communicate with port; {port_com}")
        status = {"message": "No connection to printer"}
        return make_response(jsonify(status), 400)

    except Exception as e:
        hka.CloseFpctrl()
        logging.critical(e)
        logging.critical(type(e).__name__)
        return make_response(jsonify({"error": str(e)}), 400)


if __name__ == '__main__':
    if auto_com:
        port_com = get_com()
    if auto_ip:
        host_ip = get_ip()
    if auto_browser:
        open_browser()
    print(f"http://{host_ip}:{port_ip}", port_com)
    app.run(host=host_ip, port=port_ip, debug=test)
