# Módulo de Impresión ESC/POS

Este módulo permite imprimir tickets en impresoras térmicas usando el protocolo ESC/POS. El sistema es altamente configurable, permitiendo personalizar el formato de impresión mediante plantillas JSON.

## Características

- Impresión de tickets con formato personalizable
- Soporte para códigos de barras y QR
- Impresión de logos e imágenes
- Manejo de diferentes formatos de números y fechas
- Sistema de plantillas flexible basado en JSON

## Requisitos

### Framework
- .NET Framework 4.8

### Dependencias NuGet
- Newtonsoft.Json (13.0.3 o superior) - Para manejo de JSON

### Referencias del Sistema
- System
- System.Core
- System.Drawing (para procesamiento de imágenes)
- System.Xml.Linq
- System.Data.DataSetExtensions
- Microsoft.CSharp
- System.Data
- System.Net.Http
- System.Xml

### Hardware
- Impresora térmica compatible con ESC/POS (probado con POS-80C)

## Estructura de Archivos

### Comandos de Impresora
- `Commands/EscPosCommands.cs`: Implementa los comandos ESC/POS básicos
  - Formato de texto (negrita, subrayado, etc.)
  - Alineación
  - Impresión de imágenes
  - Códigos de barras y QR
  - Corte de papel

### Configuración
- `Config/PrinterConfig.cs`: Maneja la configuración del sistema
  - Carga de configuración desde JSON
  - Gestión de plantillas
  - Configuración de formatos

### Modelos de Datos
- `Models/PrintDocument.cs`: Define la estructura de datos para impresión
  - Información del documento
  - Datos del cliente
  - Items
  - Totales
  - Pagos

### Motor de Plantillas
- `Templates/TemplateEngine.cs`: Procesa las plantillas y genera comandos
  - Interpretación de plantillas JSON
  - Sustitución de variables
  - Generación de comandos ESC/POS

### Archivos de Configuración
- `config.json`: Configuración principal
```json
{
  "printer": {
    "name": "POS-80C",
    "charWidth": 48
  },
  "template": {
    "active": "simple",
    "templates": {
      "simple": "Templates/simple.template.json"
    }
  },
  "features": {
    "logo": {
      "enabled": true,
      "path": "Assets/logo.png",
      "maxWidth": 380
    },
    "barcode": {
      "enabled": true,
      "type": "CODE128",
      "height": 64,
      "width": 2,
      "hri": true
    },
    "qr": {
      "enabled": true,
      "size": 4,
      "correction": "M"
    }
  },
  "formatting": {
    "dateFormat": "dd/MM/yyyy",
    "numberFormat": {
      "decimals": 2,
      "decimalSeparator": ",",
      "thousandsSeparator": "."
    },
    "condensedMode": {
      "enabled": false,
      "columns": 56
    }
  }
}
```

### Plantillas
- `Templates/simple.template.json`: Plantilla de ejemplo
```json
{
  "name": "Simple",
  "description": "Plantilla básica para tickets",
  "sections": [
    {
      "type": "header",
      "align": "center",
      "items": [
        { "text": "{DocumentName}", "style": "bold" },
        { "text": "Fecha: {DocumentDate:dd/MM/yyyy}", "style": "normal" }
      ]
    },
    {
      "type": "items",
      "align": "left",
      "itemFormat": [
        { "text": "{ItemRef} - {ItemName}", "style": "normal" },
        { "text": "{ItemQuantity:N0} x {ItemPrice:N2} = {Total:N2}", "style": "normal" }
      ]
    }
  ]
}
```

### Datos de Entrada
- `invoice.json`: Estructura de datos esperada
```json
{
  "DocumentName": "FACTURA",
  "DocumentNumber": "A-001",
  "DocumentDate": "2025-01-01",
  "CustomerName": "Cliente Ejemplo",
  "CustomerVat": "J-12345678-9",
  "Items": [
    {
      "ItemRef": "001",
      "ItemName": "Producto 1",
      "ItemQuantity": 2,
      "ItemPrice": 10.50,
      "Total": 21.00
    }
  ],
  "Subtotal": 21.00,
  "TaxTotal": 3.36,
  "GrandTotal": 24.36
}
```

## Resultado Esperado

El sistema producirá un ticket impreso con:

1. Logo de la empresa (opcional)
2. Encabezado con datos del documento
3. Información del cliente
4. Lista de items con cantidades y precios
5. Subtotales y totales
6. Métodos de pago
7. Código de barras o QR (opcional)

La salida exacta dependerá de la plantilla configurada y los datos proporcionados en el JSON.

## Notas de Implementación

1. Las imágenes se procesan usando dithering Floyd-Steinberg para mejor calidad
2. Los números y fechas se formatean según la configuración regional
3. El sistema es extensible mediante la modificación de plantillas JSON
4. Todas las características (logo, códigos de barras, etc.) se pueden habilitar/deshabilitar desde la configuración

## Ejemplo de Uso

```csharp
// Cargar datos
var jsonData = File.ReadAllText("invoice.json");
var document = JsonConvert.DeserializeObject<PrintDocument>(jsonData);

// Inicializar motor de plantillas
var config = PrinterConfig.Instance;
var templateEngine = new TemplateEngine(config.GetActiveTemplate());

// Generar comandos
var commands = templateEngine.GenerateTicket(document);

// Imprimir
using (var printer = new UsbPrinterConnection(config.GetPrinterName()))
{
    printer.Write(commands);
}
```
