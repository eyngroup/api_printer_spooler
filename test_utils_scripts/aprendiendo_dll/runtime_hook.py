import os
import sys
import logging

logger = logging.getLogger(__name__)


def initialize_runtime():
    try:
        # Configurar variables de entorno para Python.NET
        os.environ["PYTHONNET_RUNTIME"] = "netfx"
        os.environ["PYTHONNET_FRAMEWORK"] = "net45"
        os.environ["PYTHONNET_PYTHING"] = "python"

        # Importar pythonnet después de configurar las variables
        import pythonnet

        # Cargar el runtime usando la función directa
        pythonnet.load("netfx")
        logger.info("Runtime de .NET inicializado en el hook")

        # Importar clr después de configurar el runtime
        import clr

    except Exception as e:
        logger.error(f"Error inicializando runtime en el hook: {str(e)}")


initialize_runtime()
