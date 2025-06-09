# API Printer Server

API Printer Server es una solución robusta para manejar diferentes tipos de impresoras a través de una interfaz HTTP. Soporta impresoras fiscales, térmicas ESCPOS y matriciales, ofreciendo una API unificada para todas las operaciones de impresión.

## Estructura del Proyecto

```
api_printer_server/
├── config/
│   └── config.json         # Configuración del servidor y modos de impresión
├── lib/
│   └── icons/             # Iconos para el ejecutable
│   └── drivers/           # Librerías externas
├── logs/                  # Directorio para archivos de log
├── src/
│   ├── fiscal/           # Implementaciones para impresoras fiscales
│   ├── handlers/         # Manejadores para diferentes tipos de impresoras
│   ├── interfaces/       # Interfaces base del sistema
│   ├── utils/           # Utilidades y helpers
│   ├── HttpServer.cs    # Servidor HTTP
│   └── Program.cs       # Punto de entrada de la aplicación
├── templates/
│   ├── escpos/         # Templates para impresoras ESCPOS
│   └── matriz/         # Templates para impresoras matriciales
└── www/               # Archivos de la interfaz web
```

## Características

- **Múltiples Tipos de Impresoras**:
  - Impresoras Fiscales (TFHKA, PNP)
  - Impresoras Térmicas ESCPOS
  - Impresoras Matriciales
  - Modo Proxy para reenvío de comandos
  - Modo Test para pruebas

- **Templates Personalizables**:
  - Formato flexible para ESCPOS y matriz
  - Soporte para múltiples diseños
  - Variables dinámicas
  - Comandos de formato incorporados

- **Interfaz Web**:
  - Monitor de estado en tiempo real
  - Información detallada del servidor
  - Estado de la impresora actual
  - Actualización automática

- **Sistema de Logs**:
  - Niveles configurables
  - Rotación diaria de archivos
  - Salida a archivo y consola
  - Formato detallado de mensajes

## Configuración

### config.json
```json
{
    "server": {
        "host": "localhost",
        "port": 8080
    },
    "settings": {
        "printer_mode": "FISCAL_TFHKA",  // Modos: FISCAL_TFHKA, FISCAL_PNP, TICKET, MATRIZ, PROXY, TEST
        "FISCAL_TFHKA": {
            "port": "COM1",
            "model": "PFK-32"
        },
        "FISCAL_PNP": {
            "port": "COM2",
            "model": "PNP-1000"
        },
        "TICKET": {
            "port": "COM3",
            "template": "default"
        },
        "MATRIZ": {
            "port": "LPT1",
            "template": "default"
        },
        "PROXY": {
            "target_url": "http://localhost:8081",
            "timeout": 30000,
            "auth_token": "optional-auth-token"
        },
        "TEST": {
            "simulate_errors": false,
            "error_frequency": 10
        },
        "LOGGING": {
            "enabled": true,
            "level": "INFO",
            "path": "./logs"
        }
    }
}
```

## API Endpoints

### POST /printer/invoice
Procesa e imprime una factura.

```json
{
    "customer_name": "John Doe",
    "customer_vat": "V12345678",
    "customer_address": "123 Main St",
    "customer_phone": "555-1234",
    "items": [
        {
            "item_name": "Product 1",
            "item_quantity": 2,
            "item_price": 10.50,
            "item_tax": 16,
            "item_discount": 0
        }
    ],
    "payments": [
        {
            "payment_method": "CASH",
            "payment_amount": 21.00
        }
    ]
}
```

### POST /printer/reportx
Genera el reporte X (lectura).

### POST /printer/reportz
Genera el reporte Z (cierre).

### GET /api/ping
Verifica el estado del servidor.

## Templates

### ESCPOS
- **default.template**: Diseño básico para tickets
- **invoice_detailed.template**: Diseño detallado con códigos QR y barras

### Matriz
- **default.template**: Formato estándar 80 columnas
- **invoice_wide.template**: Formato ancho 132 columnas

## Comandos de Formato

### ESCPOS
- `[center]`, `[right]`, `[left]`: Alineación
- `[bold]`, `[double-height]`: Formato de texto
- `[condensed]`: Texto condensado
- `[qr]`, `[barcode]`: Códigos QR y barras
- `[cut]`: Corte de papel

### Matriz
- `[condensed]`: Texto condensado
- `[fixed-width]`: Ancho fijo
- `[formfeed]`: Avance de página

## Requisitos

- Windows 7 o superior
- .NET Framework 4.8
- Puertos COM/LPT según el tipo de impresora
- Drivers específicos para impresoras fiscales

## Dependencias

### NuGet Packages
```powershell
Install-Package Newtonsoft.Json -Version 13.0.3
Install-Package NLog -Version 5.2.7
Install-Package Microsoft.Extensions.Logging -Version 8.0.0
Install-Package System.IO.Ports -Version 8.0.0
Install-Package QRCoder -Version 1.4.3
Install-Package ZXing.Net -Version 0.16.9
```

### Librerías Externas (Windows)
- TfhkaNet.dll - Driver The Factory HKA
- pnpdll.dll - Driver PNP

Las librerías externas deben colocarse en la carpeta `lib/drivers/` del proyecto.

## Instalación

1. Descargar el último release
2. Extraer en la ubicación deseada
3. Configurar `config.json` según necesidades
4. Ejecutar `ApiPrinterServer.exe`

## Interfaz Web

Acceder a `http://localhost:8080/` (o el puerto configurado) para ver:
- Estado del servidor
- Modo de impresora actual
- Estado detallado de la impresora
- Tiempo de actividad
- Estadísticas de uso

## Licencia

Este proyecto está licenciado bajo MIT License.
