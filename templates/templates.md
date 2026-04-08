# Templates de Impresión

Este proyecto mantiene una sola plantilla activa y documentada:

- `templates/template_fiscal_printer.json`

Todo el material anterior no fiscal y cualquier persistencia de estado dentro de templates fue retirado del branch fiscal-only.

## Template Fiscal (`template_fiscal_printer.json`)

### Estructura actual

```json
{
  "fiscal": {
    "model": "SRP-350",
    "serial": "Z1B1234567",
    "name_note": "Nota de Despacho"
  },
  "format": {
    "include_partner_address": true,
    "partner_address_lines": 3,
    "include_partner_phone": false,
    "include_partner_email": false,
    "include_document_number": false,
    "include_document_reference": true,
    "include_document_date": false,
    "include_document_name": true,
    "include_document_cashier": true,
    "include_item_reference": true,
    "include_item_comment": false,
    "include_payment_subtotal": false,
    "include_delivery_comments": false,
    "include_delivery_barcode": true,
    "include_operator_mail": true,
    "include_exchange_rate": true
  }
}
```

## Sección `fiscal`

- `model`: modelo o referencia comercial usada en la plantilla.
- `serial`: serial fiscal del equipo.
- `name_note`: nombre que se utilizará para documentos de entrega o notas no fiscales emitidas por el equipo fiscal.

## Sección `format`

### Datos del cliente

- `include_partner_address`: incluye dirección del cliente.
- `partner_address_lines`: máximo de líneas de dirección a usar en cabecera.
- `include_partner_phone`: incluye teléfono.
- `include_partner_email`: incluye correo del cliente.

### Datos del documento

- `include_document_number`: incluye número del documento origen.
- `include_document_reference`: incluye referencia del documento.
- `include_document_date`: incluye fecha del documento.
- `include_document_name`: incluye nombre del documento.
- `include_document_cashier`: incluye cajero / vendedor / usuario.

### Datos de ítems y pagos

- `include_item_reference`: incluye código o referencia del ítem.
- `include_item_comment`: incluye comentario del ítem.
- `include_payment_subtotal`: incluye subtotal de pagos cuando el driver lo soporta.

### Datos de entrega y footer

- `include_delivery_comments`: incluye comentarios de entrega.
- `include_delivery_barcode`: incluye código de barras o dato equivalente de entrega.
- `include_operator_mail`: incluye el `operator_id` del bloque `operation_metadata` en el footer.
- `include_exchange_rate`: incluye tasa de cambio cuando el documento trae ese dato y el driver lo usa.

## Consideraciones por driver

### TFHKA

- Usa índices dinámicos `i00` a `i09` para la cabecera.
- Soporta dirección multilínea usando `partner_address_lines`.
- El footer puede incluir comentarios de entrega, correo de operador y tasa de cambio.
- `include_delivery_barcode` y `include_payment_subtotal` tienen sentido principalmente en este flujo.

### PNP

- Tiene restricciones más estrechas sobre la cantidad de datos opcionales que conviene incluir.
- Antes de activar muchos campos opcionales, validar en hardware real.

## Balance de líneas en cabecera TFHKA

La cabecera fiscal comparte espacio entre dirección, teléfono, email y datos del documento. Mientras más líneas se asignen a la dirección, menos campos adicionales caben en `i00` a `i09`.

Orden de prioridad usado por el sistema:

1. Dirección
2. Teléfono
3. Email
4. Número de documento
5. Referencia
6. Fecha
7. Nombre del documento
8. Cajero

### Ejemplo

```text
i00AV. PRINCIPAL 123
i01SAN CRISTOBAL, TACHIRA
i02VENEZUELA
i03TEL:04141234567
i04EMAIL:cliente@test.com
i05REF:0004-001-0002
```

### Referencia rápida

| `partner_address_lines` | Espacio restante aproximado |
|-------------------------|-----------------------------|
| `2` | alto |
| `3` | medio |
| `4` | limitado |

## Recomendaciones de uso

- Cambiar un solo bloque de opciones por vez cuando se esté ajustando salida fiscal.
- Validar siempre en el equipo fiscal real después de modificar la plantilla.
- Mantener sincronizado este documento con cualquier nuevo campo agregado al JSON.
- No usar el template para persistir estado runtime.

## Verificación mínima tras cambios en template

- impresión de factura
- impresión de nota o documento de entrega
- validación de cabecera multilínea
- validación de footer
- validación de barcode o tasa de cambio si fueron activados