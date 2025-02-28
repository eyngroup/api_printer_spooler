# Configuración del Sistema

Este documento explica la estructura y opciones de configuración disponibles en el archivo `config.json`.

## Estructura General

El archivo de configuración está dividido en las siguientes secciones principales:

- Server
- Proxy
- Printers (Fiscal, Matrix, Ticket)
- Logging
- Security

## Secciones Detalladas

### Server

```json
{
    "server": {
        "server_mode": "SPOOLER",
        "server_host": "0.0.0.0",
        "server_port": 5000,
        "server_debug": false,
        "auto_browser": false
    }
}
```
#### Configuración del Servidor
- `server_mode`: Modo de operación del servidor. Puede ser "SPOOLER" o "PROXY".
- `server_host`: Dirección IP del servidor.
- `server_port`: Puerto del servidor.
- `server_debug`: Habilita el modo debug para desarrollo.
- `auto_browser`: Abrir navegador automáticamente al iniciar.

### Proxy

```json
{
    "proxy": {
        "proxy_enabled": false,
        "proxy_target": "http://localhost:5001"
    }
}
```
#### Configuración del Proxy
- `proxy_enabled`: Habilitar/deshabilitar modo proxy.
- `proxy_target`: URL del servidor destino. Ejemplo: `Ejemplo: `URL_ADDRESS:5001`

### Printers

#### Impresora Fiscal

```json
{
    "fiscal": {
        "fiscal_enabled": true,
        "fiscal_name": "TFHKA",
        "fiscal_port": "COM9",
        "fiscal_baudrate": 9600,
        "fiscal_timeout": 3
    }
}
```
##### Impresora Fiscal
- `fiscal_enabled`: Habilitar/deshabilitar impresora fiscal.
- `fiscal_name`: Modelo de impresora (TFHKA, PNP, RIGAZSA*, BEMATECH*).
- `fiscal_port`: Puerto serial.
- `fiscal_baudrate`: Velocidad de comunicación serial.
- `fiscal_timeout`: Tiempo de espera en segundos.

*Nota: Los modelos RIGAZSA y BEMATECH están en desarrollo y no disponibles actualmente.

#### Impresora Matriz

```json
{
    "matrix": {
        "matrix_enabled": false,
        "matrix_name": "EPSON LX-350",
        "matrix_port": "LX-350",
        "matrix_paper": "CARTA",
        "matrix_template": "template_matriz_carta.json",
        "matrix_file": "docs/print_output.txt",
        "matrix_direct": false,
        "matrix_use_escp": false
    }
}
```
##### Impresora Matriz
- `matrix_enabled`: Habilitar/deshabilitar impresora matriz.
- `matrix_name`: Nombre/modelo de la impresora. *USAR CONTROLADOR GENERICO PARA LAS IMPRESORAS*
- `matrix_port`: Puerto de impresora, se usa el nombre de la impresora.
- `matrix_paper`: Tipo de papel (CARTA, MEDIA_CARTA).
- `matrix_template`: Plantilla a usar.
- `matrix_file`: Archivo de salida si no es directa.
- `matrix_direct`: Impresión directa al puerto.
- `matrix_use_escp`: Usar comandos ESC/P.

#### Impresora de Ticket

```json
{
    "ticket": {
        "ticket_enabled": false,
        "ticket_name": "ROCCIO",
        "ticket_port": "POS-80C",
        "ticket_paper": "80mm",
        "ticket_template": "template_ticket_simple.json",
        "ticket_file": "docs/ticket_output.txt",
        "ticket_direct": false,
        "ticket_use_escpos": false,
        "logo_enabled": false,
        "logo_width": 300,
        "logo_height": 100,
        "barcode_enabled": false,
        "barcode_type": "QR"
    }
}
```
##### Impresora de Ticket
- `ticket_enabled`: Habilitar/deshabilitar impresora de tickets.
- `ticket_name`: Nombre/modelo de la impresora.
- `ticket_port`: Puerto de impresora, se usa el nombre de la impresora en Windows.
- `ticket_paper`: Ancho del papel (58mm, 80mm).
- `ticket_template`: Plantilla a usar.
- `ticket_file`: Archivo de salida si no es directa.
- `ticket_direct`: Impresión directa al puerto.
- `ticket_use_escpos`: Usar comandos ESC/POS.
##### Configuración de Logo
- `logo_enabled`: Habilitar logo en tickets. Requiere un archivo logo.bmp en formato monocromático (1-bit) en la carpeta resources.
- `logo_width`: Ancho del logo en píxeles. Debe mantener una proporción de 3:1 con el alto dependiendo de la imagen:
  - Base:   300 píxeles
  - Mínimo: 360 píxeles
  - Normal: 480 píxeles (recomendado)
  - Máximo: 720 píxeles
- `logo_height`: Alto del logo en píxeles. Debe ser aproximadamente 1/3 del ancho. Valores recomendados:
  - Base:   100 píxeles
  - Mínimo: 120 píxeles
  - Normal: 160 píxeles (recomendado)
  - Máximo: 240 píxeles

**Nota**: Para mantener la calidad de impresión, siempre escalar ambas dimensiones usando el mismo factor. Por ejemplo, para aumentar 25% usar: width=600, height=200.
##### Configuración de Código de Barras
- `barcode_enabled`: Habilitar códigos de barras.
- `barcode_type`: Tipo de código (QR, BARCODE, CODE128).

### Logging

```json
{
    "logging": {
        "log_output": false,
        "log_file": "printer_service",
        "log_level": "INFO",
        "log_format": "%(asctime)s - %(levelname)s - %(message)s",
        "log_days": 3
    }
}
```
##### Configuración de Logs
- `log_output`: Habilita la salida de logs en la consola.
- `log_file`: Nombre del archivo de log, sin extensión.
- `log_level`: Nivel de log, puede ser DEBUG, INFO, WARNING, ERROR o CRITICAL.
- `log_format`: Formato de los logs. "%(asctime)s | %(levelname)s | [%(threadName)s] | %(filename)s:%(lineno)d | %(funcName)s | %(message)s"
- `log_days`: Número de días que se mantienen los logs. Minimo 1 dia

### Security

```json
{
    "security": {
        "security_code": "1234"
    }
}
```
#### Configuración de Seguridad
- `security_code`: Código de seguridad para operaciones protegidas.

## Modos de Operación

### Modo SPOOLER

- Procesa documentos directamente
- Requiere configuración de al menos una impresora
- Valida tipos de documentos y formato

### Modo PROXY

- Reenvía solicitudes a otro servidor
- Requiere `proxy_enabled: true`
- Necesita URL válida en `proxy_target`

## Configuración de Impresoras

### Impresora Fiscal

- Soporta modelos TFHKA y PNP
- Requiere configuración de puerto serial correcta
- El timeout debe ajustarse según la velocidad de la impresora

### Impresora Matriz

- Soporta impresión directa o a archivo
- Comandos ESC/P opcionales para control avanzado
- Plantillas específicas para formato carta

### Impresora de Ticket

- Soporta diferentes anchos de papel
- Capacidad de imprimir logos y códigos QR
- Comandos ESC/POS para mejor control

## Valores Permitidos

### Server

- `server_mode`: ["SPOOLER", "PROXY"]

### Impresora Fiscal

- `fiscal_name`: ["TFHKA", "PNP", "RIGAZSA"*, "BEMATECH"*]
  *En desarrollo

### Impresora Matriz

- `matrix_paper`: ["CARTA", "MEDIA_CARTA"]

### Impresora de Ticket

- `barcode_type`: ["QR", "BARCODE", "CODE128"]

### Logging

- `log_level`: ["DEBUG", "INFO", "WARNING", "ERROR", "CRITICAL"]
- `log_format`: ["%(asctime)s, %(levelname)s, %(message)s", [%(threadName)s], %(filename)s:%(lineno)d, %(funcName)s"]

## Recomendaciones

1. **Seguridad**:
    - Cambiar el código de seguridad predeterminado
    - En producción, deshabilitar modo debug
    - Usar HTTPS en modo proxy

2. **Impresión**:
    - Verificar permisos de puertos COM
    - Probar plantillas antes de producción
    - Ajustar timeouts según necesidad

3. **Logging**:
    - En producción, usar nivel INFO o superior
    - Monitorear tamaño de logs
    - Rotar logs regularmente

4. **Red**:
    - Verificar firewall para puertos usados
    - En producción, limitar `server_host`
    - Configurar proxy con URL completa
