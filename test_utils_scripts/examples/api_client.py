import requests
import json
import os
from urllib3.exceptions import NewConnectionError
from requests.exceptions import ConnectionError, HTTPError, Timeout

# Default configuration
DEFAULT_SERVER = "localhost"
DEFAULT_PORT = 5051

class APIClient:
    def __init__(self, server=DEFAULT_SERVER, port=DEFAULT_PORT):
        """
        Initialize the API client with server configuration
        Args:
            server (str): Server address (default: localhost)
            port (int): Server port (default: 5051)
        """
        self.server = server
        self.port = port
        self.base_url = f"http://{self.server}:{self.port}/api"

    def _handle_request_error(self, e, endpoint):
        """
        Handle different types of request errors and return user-friendly messages
        """
        if isinstance(e, ConnectionError) or isinstance(e, NewConnectionError):
            return f"Error de conexión: No se pudo conectar al servidor {self.server}:{self.port}.\nPosibles causas:\n- El servidor no está iniciado\n- El puerto {self.port} está cerrado\n- La dirección del servidor es incorrecta"
        elif isinstance(e, Timeout):
            return f"Error: El servidor {self.server}:{self.port} no respondió a tiempo"
        elif isinstance(e, HTTPError):
            return f"Error HTTP {e.response.status_code}: {e.response.reason}"
        else:
            return f"Error inesperado al conectar con {endpoint}: {str(e)}"

    def _format_response(self, response_data):
        """
        Format the response data for better readability
        """
        return json.dumps(response_data, indent=2, ensure_ascii=False)

    def get_report(self):
        """
        Sends a GET request to the report_x endpoint
        Returns the response from the server
        """
        url = f"{self.base_url}/report_x"
        try:
            response = requests.get(url, timeout=10)
            response.raise_for_status()
            return response.json()
        except Exception as e:
            error_msg = self._handle_request_error(e, "report_x")
            print(error_msg)
            return None

    def send_printer_data(self, json_file_path="data.json"):
        """
        Sends a POST request to the printers endpoint with JSON data
        Args:
            json_file_path (str): Path to the JSON file containing the data to send
        Returns:
            The response from the server
        """
        url = f"{self.base_url}/printers"
        
        try:
            # Check if JSON file exists
            if not os.path.exists(json_file_path):
                print(f"Error: No se encontró el archivo JSON en: {json_file_path}")
                return None
            
            # Read JSON file
            try:
                with open(json_file_path, 'r', encoding='utf-8') as file:
                    data = json.load(file)
            except json.JSONDecodeError as e:
                print(f"Error: El archivo JSON no tiene un formato válido: {str(e)}")
                return None
            except Exception as e:
                print(f"Error al leer el archivo JSON: {str(e)}")
                return None
            
            # Send POST request
            response = requests.post(url, json=data, timeout=10)
            response.raise_for_status()
            
            return response.json()
        except Exception as e:
            error_msg = self._handle_request_error(e, "printers")
            print(error_msg)
            return None


if __name__ == "__main__":
    # Example usage
    # You can customize the server and port here
    client = APIClient(server="localhost", port=5051)
    
    # print("Conectando al servidor...")
    # report_response = client.get_report()
    # if report_response:
    #     print("\nRespuesta del servidor:")
    #     print("-" * 50)
    #     print(client._format_response(report_response))
    #     print("-" * 50)
    
    print("\nEnviando datos de impresora...")
    printer_response = client.send_printer_data()
    if printer_response:
        print("\nRespuesta del servidor:")
        print("-" * 50)
        print(client._format_response(printer_response))
        print("-" * 50)
