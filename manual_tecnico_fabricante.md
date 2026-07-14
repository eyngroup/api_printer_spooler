# Manual Técnico del Fabricante (Desarrollo)

## 1. Introducción y Objetivos del Proyecto
*   Este proyecto proporciona un **Servidor API REST** diseñado para optimizar el proceso de impresión fiscal, funcionando como un **Middleware de Impresión Fiscal**. Recibe datos en formato JSON, los procesa y los adapta para su impresión en dispositivos fiscales a través de conexión serial, asegurando precisión, cumplimiento normativo y eficiencia en la generación de documentos fiscales.
*   Su objetivo principal es servir como un middleware robusto y eficiente para la **impresión en dispositivos fiscales**, facilitando la integración entre sistemas de punto de venta (POS) o ERP y las impresoras fiscales homologadas.

## 2. Arquitectura del Sistema
*   Descripción general y diagrama (se puede agregar una imagen posteriormente que ilustre los componentes principales y sus interacciones).
*   Modos de operación: El sistema puede operar como **API de Impresión directa** o como **Servidor Proxy** para reenviar solicitudes a otro servidor de impresión.
*   El sistema está desarrollado inicialmente para ejecutarse en arquitecturas **x86 bajo el sistema operativo Windows**.

## 3. Tecnologías Utilizadas
*   Lenguaje principal (Python y librerías como Flask, PySerial, PyWin32).
*   Formatos de datos (JSON).
*   Tecnologías frontend (HTML, CSS, JavaScript).

## 4. Estructura del Proyecto
*   Descripción de directorios y archivos clave (se puede agregar una imagen o una estructura de árbol posteriormente).
*   El archivo principal de inicio de la aplicación es `main.py`, ubicado en la raíz del proyecto. Este script es responsable de inicializar y ejecutar el servidor Flask.
*   Para la versión ejecutable, los archivos de configuración cruciales que el usuario o el sistema de despliegue debe considerar son:
    *   `config/config.json`: Contiene la configuración general del servidor, la impresora, el proxy y el logging.
    *   `templates/template_fiscal_printer.json`: Define la plantilla o mapeo de campos para la comunicación con la impresora fiscal, permitiendo adaptar la estructura de datos JSON a los comandos específicos del hardware fiscal.

## 5. Flujo de Datos y Procesos Internos
El flujo de datos y los procesos internos del sistema se centran en la recepción, procesamiento y respuesta de las solicitudes de impresión fiscal. A continuación, se describe el ciclo general:

1.  **Recepción de Solicitud:**
    *   El cliente (sistema POS, ERP, etc.) envía una solicitud HTTP POST al endpoint `/api/printers` (o el configurado) del servidor API.
    *   La solicitud debe contener un cuerpo en formato JSON con los datos del documento a imprimir (factura, nota de crédito/débito), información del cliente, ítems, pagos, etc., siguiendo la estructura definida (ver `project.md` para el ejemplo de solicitud).

2.  **Validación Inicial y Autenticación (si aplica):**
    *   La API primero valida la estructura básica del JSON y la presencia de campos obligatorios.
    *   Se pueden aplicar mecanismos de autenticación (ej. tokens, API keys, no detallado en `project.md` pero una práctica común) para verificar la identidad del cliente.

3.  **Determinación del Modo de Operación:**
    *   El sistema verifica la configuración (`server.server_mode` en `config.json`) para determinar si opera en modo `API` (impresión directa) o `PROXY`.

4.  **Procesamiento en Modo API:**
    *   **Adaptación de Datos:** El middleware procesa el JSON recibido. Utiliza la plantilla definida en `templates/template_fiscal_printer.json` para mapear los campos del JSON a los comandos y formatos específicos requeridos por el modelo de impresora fiscal configurado (`printers.fiscal.fiscal_name`).
    *   **Comunicación con la Impresora Fiscal:**
        *   Se establece una conexión con la impresora fiscal a través del puerto serial configurado (`printers.fiscal.fiscal_port`) y con los parámetros de comunicación (baudrate, timeout).
        *   Se envían los comandos fiscales correspondientes para registrar los datos del cliente, los ítems (descripción, cantidad, precio, impuesto), los métodos de pago, y finalmente, para emitir el documento fiscal.
        *   El sistema maneja la secuencia de comandos necesaria, incluyendo la apertura de documentos, registro de ítems, aplicación de descuentos, y cierre del documento fiscal.
    *   **Manejo de Errores de Impresión:** Si ocurren errores durante la comunicación o el proceso de impresión (ej. impresora offline, falta de papel, error fiscal), el sistema captura estos errores.
    *   **Obtención de Datos Fiscales:** Tras una impresión exitosa, la impresora fiscal devuelve datos como el número de documento fiscal impreso, el número de serie de la máquina y el número de reporte Z (si aplica). El middleware captura esta información.

5.  **Procesamiento en Modo Proxy:**
    *   Si `proxy.proxy_enabled` es `true` y el modo es `PROXY`, la API reenvía la solicitud JSON original al servidor de impresión destino especificado en `proxy.proxy_target`.
    *   Espera la respuesta del servidor proxy y la retransmite tal cual al cliente original.
    *   La validación fiscal y la interacción directa con la impresora son responsabilidad del servidor destino en este modo.

6.  **Generación de Respuesta:**
    *   **Respuesta Exitosa (Modo API):** Se construye una respuesta JSON con `"status": true`, un mensaje descriptivo, y los datos fiscales obtenidos de la impresora (fecha, número de documento, serial de máquina, reporte Z).
    *   **Respuesta de Error:** Si ocurre un error en cualquier etapa, se construye una respuesta JSON con `"status": false` y un mensaje descriptivo del error.
    *   La respuesta se envía de vuelta al cliente.

7.  **Registro (Logging):**
    *   Todas las operaciones significativas, solicitudes, respuestas, errores y estados de la impresora se registran en archivos de log según la configuración de logging (ver Sección 9), facilitando la auditoría y depuración.

## 6. Configuración del Entorno de Desarrollo
*   **Python:** Se requiere **Python 3.10 (64-bit)** o una versión compatible superior. Es crucial que sea la versión de 64 bits.
*   **Entorno Virtual:** Se recomienda encarecidamente utilizar un entorno virtual (por ejemplo, `venv`) para aislar las dependencias del proyecto y evitar conflictos con otros paquetes de Python instalados en el sistema.
*   **Dependencias:** Todas las bibliotecas de Python necesarias para el proyecto están listadas en el archivo `requirements.txt`. Estas se pueden instalar ejecutando el comando `pip install -r requirements.txt` dentro del entorno virtual activado.

## 7. Proceso de Construcción del Ejecutable
*   Para construir el ejecutable autocontenido para Windows, se proporciona el script `run.bat` en la raíz del proyecto.
*   Este script debe ser ejecutado desde una **ventana de comandos de Windows (cmd.exe)**. No se garantiza su funcionamiento si se ejecuta desde PowerShell u otros intérpretes de comandos.
*   El script `run.bat` automatiza los siguientes pasos:
    1.  Verificación de la versión y arquitectura de Python instalada.
    2.  Creación de un entorno virtual (directorio `.venv`) si no existe.
    3.  Activación del entorno virtual.
    4.  Actualización de `pip` a su última versión.
    5.  Instalación de todas las dependencias listadas en `requirements.txt`.
    6.  Limpieza de cualquier directorio `build` preexistente.
    7.  Ejecución de `python setup.py build` para generar los archivos necesarios que conforman el ejecutable.
*   Una vez finalizado el proceso, los archivos compilados se encontrarán típicamente dentro del subdirectorio `build\exe.win-amd64-3.10` (la ruta exacta puede variar ligeramente según la configuración de `cx_Freeze`).

## 8. Manejo de CORS
*   Para controlar el acceso a la API desde navegadores y prevenir ataques CSRF, se utiliza la extensión [Flask-CORS](https://flask-cors.readthedocs.io/).
*   La configuración de los orígenes permitidos (`allowed_origins`) se encuentra en el archivo `server_api.py`. Se emplean **expresiones regulares** para definir de manera flexible los dominios, IPs o patrones que tienen permiso para realizar solicitudes a la API. Esto permite, por ejemplo:
    *   Permitir `localhost` y `127.0.0.1` en cualquier puerto para desarrollo local.
    *   Permitir direcciones IPv6 locales como `[::1]`.
    *   Permitir rangos de direcciones IP privadas (ej. `192.168.x.x`, `10.x.x.x`).
    *   Permitir subdominios específicos de un dominio principal (ej. `https://*.odoo.com`).
*   La opción `supports_credentials=True` está habilitada, lo que permite que el navegador envíe cookies o cabeceras de autenticación en las peticiones CORS. Esto es relevante si la API utiliza mecanismos de autenticación basados en cookies o tokens enviados en cabeceras. Es importante notar que al usar `supports_credentials=True`, no se puede utilizar el comodín `*` como origen permitido, lo que refuerza la necesidad de definir orígenes específicos o patrones mediante expresiones regulares.

## 9. Sistema de Logging
*   El sistema cuenta con un módulo de logging configurable para registrar eventos, errores y actividad general de la API.
*   **Configuración:** Los parámetros de logging se definen en el archivo `config.json` bajo la sección `"logging"`:
    *   `"log_output"`: (Booleano) Si es `true`, los logs también se mostrarán en la consola además de guardarse en archivo.
    *   `"log_file"`: (String) Nombre base para los archivos de log (ej. `"api_fiscal"`). El sistema añadirá la fecha al nombre del archivo, creando uno nuevo cada día (ej. `api_fiscal_YYYY-MM-DD.log`).
    *   `"log_level"`: (String) Nivel de severidad para los logs. Valores comunes son `"DEBUG"` (muy detallado, útil para desarrollo), `"INFO"` (eventos generales, recomendado para producción), `"WARNING"`, `"ERROR"`, `"CRITICAL"`.
    *   `"log_format"`: (String) Define el formato de cada entrada de log. Utiliza placeholders estándar de Python logging (ej. `"%(asctime)s | %(levelname)s | %(message)s"`).
    *   `"log_days"`: (Integer) Número de días que se conservarán los archivos de log. El sistema eliminará automáticamente los logs más antiguos que este periodo. Se recomienda no exceder los 15 días para evitar un consumo excesivo de disco, dado que se genera un archivo por día.
*   **Ubicación:** Los archivos de log se almacenan en un subdirectorio llamado `logs` dentro del directorio principal de la aplicación.
*   **Uso:** El logging se integra en toda la aplicación para registrar inicios de sesión, solicitudes recibidas, errores durante el procesamiento, estado de la impresora, etc., facilitando la depuración y auditoría.

## 10. Consideraciones de Seguridad
*   **Código de Seguridad:** La aplicación utiliza un código de seguridad (`security.security_code` en `config.json`) para proteger ciertas operaciones sensibles (ej. impresión de reportes Z, acceso al editor de configuración). Es **crucial cambiar el valor predeterminado** de este código por uno robusto y mantenerlo confidencial.
*   **Manejo de CORS:** Como se detalló en la sección 8, se utiliza Flask-CORS con una configuración basada en expresiones regulares para los orígenes permitidos. Esto ayuda a prevenir que sitios no autorizados realicen solicitudes a la API desde navegadores. La opción `supports_credentials=True` está activa, lo que es relevante si se implementan mecanismos de autenticación basados en cookies o tokens en cabeceras.
*   **Modo Debug:** El modo debug del servidor (`server.server_debug` en `config.json`) debe estar **deshabilitado en entornos de producción**. Habilitarlo puede exponer información sensible sobre la aplicación en caso de errores.
*   **Validación de Entradas:** Aunque no se detalla explícitamente en la documentación revisada, es una práctica estándar y recomendada que la API valide y sanitice todas las entradas recibidas en las solicitudes JSON para prevenir vulnerabilidades como inyección de comandos o procesamiento de datos malformados.
*   **Exposición de Endpoints:** Limitar la exposición de endpoints administrativos o de configuración solo a redes internas o IPs autorizadas si es posible.
*   **Actualizaciones de Dependencias:** Mantener las dependencias del proyecto (listadas en `requirements.txt`) actualizadas para mitigar vulnerabilidades conocidas en las librerías utilizadas.
*   **HTTPS:** Para entornos de producción, se recomienda encarecidamente desplegar la API detrás de un proxy inverso (como Nginx o Apache) que gestione HTTPS, asegurando que la comunicación entre el cliente y el servidor esté cifrada.
