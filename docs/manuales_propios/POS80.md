# Manual propio: tiquera POS80 (80 mm, ESC/POS)

Comportamiento verificado en una tiquera térmica POS80 real. Impresora **no fiscal**.
Volver al [resumen del proyecto](../project.md).

## Conexión

- Linux: USB (Winbond "Virtual Com Port", producto "POS80 Printer USB") con driver `usblp`, dispositivo
  `/dev/usb/lp0` (`root:lp 660`). Requiere un permiso temporal (ACL) o pertenecer al grupo `lp`.
- Envío directo: `cat archivo.txt > /dev/usb/lp0`. El modo archivo del spooler genera exactamente esos bytes.
- Puede operar detrás de una segunda instancia del spooler en otro puerto (diario de notas).

## Juego de caracteres (`ESC t n`, numeración Epson)

| Método | Resultado |
|---|---|
| `ESC t 18` + UTF-8 (spooler anterior) | Caracteres corruptos |
| `ESC t 18` + CP850 | La tabla 18 es **PC852** (centroeuropeo): ñ sale como ą, ¡ como ş, ¿ como Ę |
| **`ESC t 2` + CP850** | **Correcto** (elegido: misma codificación que la matriz) |
| `ESC t 16` + CP1252 | Correcto |
| `ESC t 0` + CP437 | Sin mayúsculas acentuadas |
| `ESC t 19` + CP858 | Correcto |

El spooler usa `ESC t 2` (PC850) y codifica en CP850 todas las salidas, sin quitar acentos (commit `ff233e4`).

## Código de barras

Se imprime solo si el documento trae `delivery.delivery_barcode` **y** la configuración tiene
`barcode_enabled: true`. El tipo por defecto es CODE128; con `barcode_type: "qr"` se imprime un QR.

## Contenido del ticket (commit `f1cc37b`)

- Totales calculados con el modelo (descuentos, recargos y línea de ajustes), de modo que coinciden con lo cobrado
  en Odoo.
- Contador reservado, impreso y luego confirmado bajo un candado.
- El logo se imprime solo en modo directo y después del formateo.
