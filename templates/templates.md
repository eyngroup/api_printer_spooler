# Templates de Impresión

## Template Ticket Simple (template_ticket_simple.json)

### Header (Encabezado)

```json
{
    "header": {
        "title": "======",
        "subtitle": "RIF: J-12345678-9",
        "company": "NOMBRE DE LA EMPRESA",
        "address": "Av. Principal, Local 1",
        "phone": "Telf: (0212) 555-5555",
        "type": "*",
        "name": "NUMERO"
    }
}
```
#### Campos del Header
- `title`: Título principal del documento.
- `subtitle`: Subtítulo o información adicional.
- `company`: Nombre completo de la empresa.
- `address`: Dirección completa de la empresa.
- `phone`: Teléfono de contacto.
- `type`: Tipo de documento deseado "Nota", "Entrega", Etc. (* = usa el tipo del documento recibido).
- `name`: Nombre del documento.

### Footer (Pie de Página)

```json
{
    "footer": {
        "message": "¡Gracias por su Compra!",
        "legal": "Documento NO Fiscal"
    }
}
```
#### Campos del Footer
- `message`: Mensaje de agradecimiento o finalización del documento.
- `legal`: Texto legal o información adicional.

### Format (Formato)

```json
{
    "format": {
        "width": 48,                          // Ancho total del ticket en caracteres
        "separator": "-",                     // Carácter usado para líneas separadoras
        "show_customer_address": false,       // Mostrar dirección del cliente
        "show_customer_phone": false,         // Mostrar teléfono del cliente
        "show_document_name": false,          // Mostrar nombre del documento
        "show_document_number": false,        // Mostrar número del documento
        "show_items_header": false,           // Mostrar encabezado de items
        "combine_item_ref": true,             // Combinar referencia con descripción
        "width_item_description": 15,         // Ancho máximo para descripción de items
        "qr": {
            "size": 6,                        // Tamaño del código QR (1-16)
            "error_level": "M",               // Nivel de corrección de errores
            "model": 1                        // Modelo de QR (1 o 2)
        }
    }
}
```
#### Campos del Format
- `width`: Ancho total del ticket en caracteres.
- `separator`: Carácter usado para líneas separadoras.
- `show_customer_address`: Mostrar dirección del cliente.
- `show_customer_phone`: Mostrar teléfono del cliente.
- `show_document_name`: Mostrar nombre del documento.
- `show_document_number`: Mostrar número del documento.
- `show_items_header`: Mostrar encabezado de items.
- `combine_item_ref`: Combinar referencia (Codigo) con descripción del item.
- `width_item_description`: Ancho máximo para descripción de items.
#### Configuración de QR
- `size`: Tamaño del código QR (1-16).
- `error_level`: Nivel de corrección de errores ("L", "M", "Q", "H").
- `model`: Modelo de QR (1 o 2).

#### Opciones de QR

##### Tamaño (size)

- Rango: 1-16
- Recomendado: 6
- Menor número = QR más pequeño
- Mayor número = QR más grande y más legible

##### Nivel de Error (error_level)

- "L" (Low): 7% de corrección
- "M" (Medium): 15% de corrección (recomendado)
- "Q" (Quality): 25% de corrección
- "H" (High): 30% de corrección

##### Modelo (model)

- 1: Modelo original (menor capacidad)
- 2: Modelo mejorado (mayor capacidad)


### Ejemplos de Configuración

#### Configuración para Ticket Estrecho (58mm)

```json
{
    "format": {
        "width": 32,                          // Ancho reducido para papel de 58mm
        "width_item_description": 12,         // Descripción más corta
        "qr": {
            "size": 4                         // QR más pequeño para papel estrecho
        }
    }
}
```

#### Configuración para Ticket Ancho (80mm)

```json
{
    "format": {
        "width": 48,                          // Ancho estándar para papel de 80mm
        "width_item_description": 20,         // Descripción más amplia
        "qr": {
            "size": 6                         // QR tamaño estándar
        }
    }
}
```

#### Configuración QR para Alta Calidad

```json
{
    "format": {
        "qr": {
            "size": 8,                        // Tamaño grande para mejor lectura
            "error_level": "H",               // Máxima corrección de errores
            "model": 2                        // Modelo mejorado
        }
    }
}
```

#### Configuración QR para Tamaño Pequeño

```json
{
    "format": {
        "qr": {
            "size": 4,                        // Tamaño reducido
            "error_level": "L",               // Mínima corrección de errores
            "model": 1                        // Modelo básico
        }
    }
}
```

## Template Matriz Carta (template_matriz_carta.json)

### Header Específico

```json
{
    "header": {
        // ... campos comunes ...
        "columns": [
            "CODIGO",                         // Columna para código de producto
            "DESCRIPCION",                    // Columna para descripción
            "CANT",                           // Columna para cantidad
            "PRECIO",                         // Columna para precio unitario
            "TOTAL"                           // Columna para total
        ],
        "column_widths": [
            8,                                // Ancho para código
            40,                               // Ancho para descripción
            6,                                // Ancho para cantidad
            13,                               // Ancho para precio
            13                                // Ancho para total
        ],
        "column_format": [
            "s",                              // s = string (texto)
            "s",                              // s = string (texto)
            "f",                              // f = float (número decimal)
            "f",                              // f = float (número decimal)
            "f"                               // f = float (número decimal)
        ]
    }
}
```
#### Campos del Header
- `columns`: Nombres de las columnas para la matriz.
- `column_widths`: Ancho de cada columna en caracteres.
- `column_format`: Formato de cada columna ("s" para texto, "f" para número decimal).


### Format Específico

```json
{
    "format": {
        "page_width": 80,
        "margin_left": 5,
        "margin_top": 3,
        "margin_bottom": 3,
        "show_items_comment": false,
        "show_payments": false,
        "show_delivery_comment": false,
        "separator": "="
    }
}
```
#### Campos del Format
- `page_width`: Ancho total de la página en caracteres.
- `margin_left`: Margen izquierdo en caracteres.
- `margin_top`: Margen superior en líneas.
- `margin_bottom`: Margen inferior en líneas.
- `show_items_comment`: Mostrar comentarios de items.
- `show_payments`: Mostrar sección de pagos.
- `show_delivery_comment`: Mostrar comentarios de entrega.
- `separator`: Carácter para separadores.

## Template Impresoras Fiscales (template_fiscal_printer.json)

### Datos Específicos

```json
{
  "fiscal": {
    "model": "PF-300",
    "serial": "EOO9000001",
    "name_note": "Nota de Entrega"
  },
  "format": {
    "include_partner_address": false,
    "include_partner_phone": false,
    "include_partner_email": false,
    "include_document_number": false,
    "include_document_date": false,
    "include_document_name": false,
    "include_document_cashier": false,
    "include_item_reference": false,
    "include_item_comment": false,
    "include_payment_subtotal": false,
    "include_delivery_comments": false,
    "include_delivery_barcode": false
  }
}
```
#### Campos de Impresoras Fiscales
- `model`: Modelo fiscal registrado.
- `serial`: Número de serie fiscal.
- `name_note`: Título para Documentos NO Fiscales.
#### Campos de Formato
- `include_partner_address`: Habilitar/Deshabilitar dirección del cliente.
- `include_partner_phone`: Habilitar/Deshabilitar teléfono de cliente.
- `include_partner_email`: Habilitar/Deshabilitar email del cliente.
- `include_document_number`: Habilitar/Deshabilitar número del documento original.
- `include_document_date`: Habilitar/Deshabilitar fecha del documento original.
- `include_document_name`: Habilitar/Deshabilitar nombre del documento original.
- `include_document_cashier`: Habilitar/Deshabilitar nombre de cajero/vendedor/usuario.
- `include_item_reference`: Habilitar/Deshabilitar código del ítem.
- `include_item_comment`: Habilitar/Deshabilitar comentario del ítem.
- `include_payment_subtotal`: Habilitar/Deshabilitar subtotal de pagos.
- `include_delivery_comments`: Habilitar/Deshabilitar comentarios de entrega.
- `include_delivery_barcode`: Habilitar/Deshabilitar código de barras.

#### Obervaciones
- `include_payment_subtotal`: Solo disponible para impresoras fiscales TFHKA.
- `include_delivery_barcode`: Solo disponible para impresoras fiscales TFHKA.
- Impresoras PNP solo soportan 3 includes de los siguiente: `address`, `phone`, `email`, `number`, `date`, `name`, `cashier`.
- Impresoras PNP solo soportan 20 item con el include `comment`.
- Impresoras PNP solo soportan 3 lineas del include `delivery_comments`.

# Section Counter (Contador)

```json
{
    "counter": {
        "document_date": "2025-01-12",
        "document_invoice": "00000237",
        "document_credit": "00000322",
        "document_debit": "00000408",
        "document_note": "00000500",
        "machine_report": "0022",
        "machine_serial": "Z1B1234567"
    }
}
```
## Campos del Contador
- `document_date`: Fecha actual de la impresora, si no toma el dia ctual.
- `document_invoice`: Contador interno de facturas. Numeros de control.
- `document_credit`: Contador interno de notas de crédito. Numeros de control.
- `document_debit`: Contador interno de notas de débito. Numeros de control.
- `document_note`: Contador interno de notas de entrega. Numeros de control.
- `machine_report`: Número del ultimo reporte de la impresora.
- `machine_serial`: Número serial de la impresora.