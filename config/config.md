# Configuración del Sistema

Este documento describe el archivo `config/config.json` en su estado actual **fiscal-only**.

## Estructura General

El archivo se organiza en cinco secciones:

- `server`
- `proxy`
- `printers`
- `logging`
- `security`

## Ejemplo Completo

```json
{
    "server": {
        "allowed_origins": [
            "^http://localhost(:\\d+)?$",
            "^http://127\\.0\\.0\\.1(:\\d+)?$",
            "^http://\\[::1\\](:\\d+)?$",
            "^http://192\\.168\\.\\d{1,3}\\.\\d{1,3}(:\\d+)?$",
            "^http://10\\.\\d{1,3}\\.\\d{1,3}\\.\\d{1,3}(:\\d+)?$",
            "^https://.*\\.odoo\\.com$",
            "^https://sys\\.clidair\\.com$"
        ],
        "auto_browser": false,
        "scan_serial_port": true,
        "server_debug": true,
        "server_host": "localhost",
        "server_mode": "SPOOLER",
        "server_port": 5051
    },
    "proxy": {
        "proxy_enabled": false,
        "proxy_target": "http://localhost:5000/api/printers"
    },
    "printers": {
        "fiscal": {
            "fiscal_barcode_type": "CODE128",
            "fiscal_baudrate": 9600,
            "fiscal_enabled": true,
            "fiscal_name": "TFHKA",
            "fiscal_port": "/dev/ttyACM0",
            "fiscal_timeout": 2
        }
    },
    "logging": {
        "log_days": 5,
        "log_file": "printer_spooler",
        "log_format": "\"%(asctime)s | %(levelname)s | %(message)s\"",
        "log_level": "DEBUG",
        "log_output": true
    },
    "security": {
        "security_code": ""
    }
}
```

## Secciones Detalladas

### `server`

Campos principales:

- `server_mode`: modo de operación. Valores válidos: `SPOOLER`, `PROXY`.
- `server_host`: host o IP donde escucha Flask.
- `server_port`: puerto TCP del servicio.
- `server_debug`: activa modo debug.
- `auto_browser`: abre automáticamente el dashboard al iniciar.
- `scan_serial_port`: intenta detectar y actualizar el puerto fiscal al iniciar.
- `allowed_origins`: lista de expresiones regulares para CORS. Es una opción operativa usada por la API aunque no forme parte estricta del schema validado.

### `proxy`

Campos:

- `proxy_enabled`: habilita lógica de reenvío.
- `proxy_target`: URL absoluta del spooler remoto.

Notas:

- En modo `PROXY`, el servidor reenvía las solicitudes de impresión al `proxy_target`.
- El endpoint destino habitual es `/api/printers`.

### `printers`

La rama fiscal-only mantiene una única subsección: `printers.fiscal`.

```json
{
    "printers": {
        "fiscal": {
            "fiscal_enabled": true,
            "fiscal_name": "TFHKA",
            "fiscal_port": "COM3",
            "fiscal_baudrate": 9600,
            "fiscal_timeout": 2,
            "fiscal_barcode_type": "CODE128"
        }
    }
}
```

Campos:

- `fiscal_enabled`: habilita o deshabilita la impresora fiscal.
- `fiscal_name`: nombre del modelo fiscal.
- `fiscal_port`: puerto serial.
- `fiscal_baudrate`: velocidad serial.
- `fiscal_timeout`: timeout en segundos.
- `fiscal_barcode_type`: tipo de código de barras para el pie del documento fiscal.

#### Modelos válidos en configuración

Según el schema, se aceptan:

- `TFHKA`
- `PNP`
- `RIGAZSA`
- `BEMATECH`

#### Modelos activos en runtime

Los drivers operativos actuales de esta rama son:

- `TFHKA`
- `PNP`

#### Tipos de código de barras válidos

- `QR`
- `BARCODE`
- `CODE128`
- `EAN13`
- `ITF`
- `CODE39`
- `PDF417`

#### Nota sobre `fiscal_barcode_type`

En el flujo fiscal actual este valor se utiliza para alinear el formato del código de barras configurado con el comportamiento esperado del equipo y sus reglas auxiliares.

### `logging`

Campos:

- `log_output`: muestra logs en consola.
- `log_file`: nombre base del archivo de log.
- `log_level`: uno de `DEBUG`, `INFO`, `WARNING`, `ERROR`, `CRITICAL`.
- `log_format`: plantilla de formato.
- `log_days`: días de retención.

### `security`

```json
{
    "security": {
        "security_code": ""
    }
}
```

Campo:

- `security_code`: campo conservado en la configuración por compatibilidad de estructura.

#### Comportamiento real de autenticación

La validación del endpoint `POST /api/auth/validate` usa este orden:

1. Variable de entorno `PRINTER_SECURITY_CODE`
2. Fallback interno a `0205`

Actualmente **no toma el valor desde `config.json`** al validar la autenticación.

## Recomendaciones Operativas

### Seguridad

- Definir `PRINTER_SECURITY_CODE` en el entorno del proceso.
- Desactivar `server_debug` en producción.
- Si el proxy atraviesa redes no confiables, usar transporte seguro.

### Impresión Fiscal

- Verificar permisos sobre el puerto serial.
- Ajustar `fiscal_timeout` según el modelo y el entorno.
- Confirmar que `fiscal_name` coincida con el driver realmente soportado.
- Mantener sincronizado `fiscal_barcode_type` con la configuración física esperada del equipo.

### Red

- Si habrá acceso desde otros equipos, no usar `localhost` en `server_host`.
- Abrir el puerto configurado en firewall.
- En modo proxy, validar que `proxy_target` apunte al endpoint `/api/printers` del spooler remoto.

### Validación mínima después de cambios

- `GET /api/status`
- `POST /api/config`
- `POST /api/printers`
- `GET /api/report_x`
- `GET /api/report_z`
