#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
Copyright © 2024, Iron Graterol
Licensed under the GNU Affero General Public License, version 3 or later.

Clase que maneja las solicitudes HTTP y las reenvía al servidor SPOOLER.
"""

import logging
from typing import Dict, Any, Tuple

import requests
from flask import request
from requests.exceptions import ConnectionError as RequestsConnectionError, Timeout


DEFAULT_TIMEOUT = 30  # segundos
HTTP_BAD_REQUEST = 400
HTTP_SERVICE_UNAVAILABLE = 503
HTTP_GATEWAY_TIMEOUT = 504
HTTP_INTERNAL_ERROR = 500

logger = logging.getLogger(__name__)


class ProxyHandler:  # pylint: disable=R0903
    """
    Manejador de proxy para reenviar solicitudes al servidor SPOOLER.
    Esta clase se encarga de gestionar el reenvío de solicitudes HTTP al
    servidor SPOOLER, manteniendo los headers, datos y cookies originales.
    Incluye manejo de errores y logging detallado de las operaciones.
    """

    def __init__(self, config: Dict[str, Any]) -> None:
        """
        Inicializa el manejador de proxy con la configuración proporcionada.
        Args:
            config: Diccionario con la configuración del proxy.
                   Debe contener 'proxy_target' y 'proxy_enabled'.
        """
        self.config: Dict[str, Any] = config
        self.target_url: str = config["proxy"]["proxy_target"]
        self.enabled: bool = config["proxy"]["proxy_enabled"]

    def handle_request(self) -> Tuple[Dict[str, Any], int]:
        """
        Maneja una solicitud HTTP y la reenvía al servidor SPOOLER.
        Returns:
            Tuple[Dict[str, Any], int]: Un tuple conteniendo la respuesta en formato JSON
            y el código de estado HTTP.
        Raises:
            RequestsConnectionError: Si no se puede establecer conexión con el servidor SPOOLER.
            Timeout: Si la conexión excede el tiempo de espera.
            RequestException: Para otros errores relacionados con la solicitud.
        """
        if not self.enabled:
            return {
                "status": "error",
                "message": "Proxy no está habilitado",
            }, HTTP_BAD_REQUEST

        try:
            self._log_request()
            response = self._forward_request()
            self._log_response(response)
            return response.json(), response.status_code

        except RequestsConnectionError:
            error_msg = f"No se pudo conectar al servidor SPOOLER: {self.target_url}"
            logger.error(error_msg)
            return {"status": "error", "message": error_msg}, HTTP_SERVICE_UNAVAILABLE

        except Timeout:
            error_msg = f"Timeout al conectar con el servidor SPOOLER: {self.target_url}"
            logger.error(error_msg)
            return {"status": "error", "message": error_msg}, HTTP_GATEWAY_TIMEOUT

        except Exception as e:
            error_msg = f"Error al procesar solicitud proxy: {str(e)}"
            logger.error(error_msg, exc_info=True)
            return {"status": "error", "message": error_msg}, HTTP_INTERNAL_ERROR

    def _log_request(self) -> None:
        """Registra los detalles de la solicitud entrante."""
        logger.info("Reenviando solicitud a: %s", self.target_url)
        logger.debug("Método: %s", request.method)
        logger.debug("Headers: %s", dict(request.headers))
        logger.debug("Datos: %s", request.get_json() if request.is_json else request.data)

    def _forward_request(self) -> requests.Response:
        """
        Reenvía la solicitud al servidor SPOOLER.
        Returns:
            requests.Response: La respuesta del servidor SPOOLER.
        """
        return requests.request(
            method=request.method,
            url=self.target_url,
            headers={key: value for key, value in request.headers if key != "Host"},
            data=request.get_data(),
            cookies=request.cookies,
            allow_redirects=False,
            timeout=DEFAULT_TIMEOUT,
        )

    def _log_response(self, response: requests.Response) -> None:
        """
        Registra los detalles de la respuesta recibida.
        Args:
            response: La respuesta recibida del servidor SPOOLER.
        """
        logger.info("Respuesta recibida del SPOOLER: %s", response.status_code)
        logger.debug("Respuesta: %s", response.text)
