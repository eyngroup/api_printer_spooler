from flask import Flask, request, jsonify
from flask_cors import CORS
import logging
from threading import Thread, Event
import signal
import sys
from datetime import datetime
import json
import os
from logging.handlers import RotatingFileHandler

# Crear directorio para logs si no existe
if not os.path.exists('logs'):
    os.makedirs('logs')
if not os.path.exists('logs/requests'):
    os.makedirs('logs/requests')

# Configuración de logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Agregar manejador para archivo
file_handler = RotatingFileHandler(
    'logs/api_server.log',
    maxBytes=10485760,  # 10MB
    backupCount=10      # Mantener hasta 10 archivos de respaldo
)
file_handler.setFormatter(logging.Formatter(
    '%(asctime)s %(levelname)s: %(message)s [in %(pathname)s:%(lineno)d]'
))
logger.addHandler(file_handler)

app = Flask(__name__)
CORS(app)

# Evento para controlar la ejecución de los hilos
shutdown_event = Event()
threads = []

def save_request_data(data, path):
    """Guarda los datos de la solicitud en un archivo JSON"""
    if data:
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S_%f')
        filename = f"logs/requests/request_{timestamp}_{path.replace('/', '_')}.json"
        try:
            with open(filename, 'w', encoding='utf-8') as f:
                json.dump({
                    'timestamp': datetime.now().isoformat(),
                    'path': path,
                    'data': data
                }, f, indent=2, ensure_ascii=False)
        except Exception as e:
            logger.error(f"Error guardando datos de solicitud: {e}")

def log_request_info():
    """Función auxiliar para registrar información de la solicitud"""
    info = f"""
    Ruta solicitada: {request.path}
    Método: {request.method}
    Headers: {dict(request.headers)}
    Datos JSON: {request.get_json(silent=True)}
    Datos Form: {request.form.to_dict() if request.form else None}
    Query Params: {request.args.to_dict()}
    """
    logger.info(info)
    
    # Guardar datos JSON si existen
    json_data = request.get_json(silent=True)
    if json_data:
        save_request_data(json_data, request.path)
    
    # Decodificar datos binarios si existen
    try:
        binary_data = request.get_data()
        if binary_data:
            decoded_data = binary_data.decode('utf-8', errors='replace')
            logger.info(f"Datos binarios decodificados: {decoded_data}")
            save_request_data(decoded_data, request.path)
    except Exception as e:
        logger.error(f"Error decodificando datos binarios: {e}")

def shutdown_server():
    """Función para detener el servidor Flask"""
    func = request.environ.get('werkzeug.server.shutdown')
    if func is None:
        raise RuntimeError('No ejecutándose con el servidor de desarrollo Werkzeug')
    func()

@app.route('/shutdown', methods=['POST'])
def shutdown():
    """Ruta para detener el servidor de forma controlada"""
    log_request_info()
    logger.info("Iniciando apagado forzado del servidor...")
    os._exit(0)

@app.route('/print_pos_ticket', methods=['POST'])
def print_pos_ticket():
    """Ruta específica para recibir datos de impresoras ESC/POS"""
    log_request_info()
    
    try:
        binary_data = request.get_data()
        if binary_data:
            decoded_data = binary_data.decode('utf-8', errors='replace')
            logger.info(f"Datos ESC/POS decodificados: {decoded_data}")
            save_request_data(decoded_data, '/print_pos_ticket')
        return jsonify({"status": "received", "message": "Datos ESC/POS recibidos"}), 200
    except Exception as e:
        logger.error(f"Error procesando datos ESC/POS: {e}")
        return jsonify({"status": "error", "message": "Error procesando datos ESC/POS"}), 500

# Ruta comodín para capturar cualquier ruta
@app.route('/<path:path>', methods=['GET', 'POST', 'PUT', 'DELETE'])
def catch_all(path):
    log_request_info()
    return jsonify({
        "status": "received",
        "message": "Solicitud recibida",
        "path": request.path,
        "method": request.method,
        "data": request.get_json(silent=True)
    }), 200

def run_server(port):
    """Función para ejecutar el servidor en un puerto específico"""
    logger.info(f"Iniciando servidor en puerto {port}")
    try:
        # Ruta hacia los certificados SSL
        context = ('certificate.pem', 'key.pem')
        app.run(host='0.0.0.0', port=port, debug=False, use_reloader=False, ssl_context=context)
    except Exception as e:
        logger.error(f"Error en servidor puerto {port}: {e}")
    finally:
        logger.info(f"Servidor en puerto {port} detenido")

def signal_handler(signum, frame):
    """Manejador de señales para CTRL+C"""
    logger.info("Señal de interrupción recibida. Forzando cierre...")
    os._exit(0)

if __name__ == '__main__':
    # Registrar el manejador de señales
    signal.signal(signal.SIGINT, signal_handler)
    signal.signal(signal.SIGTERM, signal_handler)
    
    logger.info("Iniciando servidor API...")
    
    # Lista de puertos en los que queremos ejecutar el servidor
    ports = [5050]
    
    # Crear un hilo para cada puerto
    for port in ports:
        thread = Thread(target=run_server, args=(port,))
        threads.append(thread)
        thread.start()
    
    try:
        # Mantener el programa principal ejecutándose
        while not shutdown_event.is_set():
            shutdown_event.wait(1)
    except KeyboardInterrupt:
        logger.info("Interrupción de teclado detectada")
    finally:
        # Asegurarse de que todos los hilos se detengan
        shutdown_event.set()
        for thread in threads:
            thread.join()
        logger.info("Servidor detenido correctamente")
