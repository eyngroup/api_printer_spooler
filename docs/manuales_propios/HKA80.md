# Manual propio: TFHKA HKA80 (comportamiento verificado)

Documento elaborado a partir de pruebas controladas sobre una impresora fiscal HKA80, contrastado con el
*Manual de Protocolos y Comandos TFHKA v8.5.0* (`docs/manuales/`). Describe el comportamiento real observado y las
diferencias con el manual. Volver al [resumen del proyecto](../project.md).

Los datos de contribuyente que aparecen en los ejemplos son ficticios (RIF `J-00000000-0`, registro de máquina
`Z7C0000000`, `EMPRESA DEMO, C.A.`).

---

## 0. Reglas de seguridad (máquina en producción)

- **Nunca** enviar reporte Z (`I0Z`/`I*Z`), extracción `U0Z` ni reimpresiones de Z (`RZ...`, `Rz...`) en una máquina
  de producción. Un cierre Z es irreversible.
- Usar solo documentos de valor mínimo. **Toda factura o nota de débito de prueba debe anularse con una nota de
  crédito** por el mismo monto y las mismas formas de pago.
- Los comandos de escritura se envían **sin reintentos propios** durante las pruebas: un ACK perdido seguido de un
  reintento puede duplicar ítems o pagos.
- No modificar flags de configuración (comando `PJ`) que no estén documentados. Nunca tocar el flag 50 (IGTF).

## 1. Conexión

| Dato | Valor observado |
|---|---|
| Puerto (Linux) | Dispositivo `ttyACM*`: USB nativo **CDC-ACM** (sin adaptador USB-serial intermedio) |
| Permisos | El dispositivo suele ser `root:uucp 660`; requiere una ACL o pertenecer al grupo |
| Parámetros | 9600 baudios, 8 bits, paridad **par**, 1 bit de parada (los de `controllers/pfhka.py`) |
| Cable | Usar el cable **original**: un cable genérico no fue reconocido por el sistema |

Notas:

- La autodetección del spooler busca adaptadores Prolific/"USB Serial"; un puerto CDC-ACM nativo probablemente no
  es detectado (pendiente de verificar en Windows).
- En Linux, al desconectar y reconectar el USB con el spooler en ejecución, el dispositivo cambia de nombre
  (`ttyACM0` a `ttyACM1`) y se pierde la ACL. Una ruta estable es `/dev/serial/by-id/...`.

## 2. Tramas

- Comando: `STX (0x02) + comando + ETX (0x03) + LRC`, con LRC = XOR de comando + ETX.
- Escritura: la máquina responde **un byte**: `ACK (0x06)` aceptado o `NAK (0x15)` rechazado.
- Lectura (`S1`...`SV`): responde `STX + datos + ETX + LRC`. El manual (pág. 20, Tabla 10) indica que el host
  responde `ACK`; el driver actual no lo hace. Campos separados por `0x0A` (en `S2` también por espacio).
- `ENQ (0x05)`: responde 5 bytes `STX STS1 STS2 ETX LRC`, con LRC = `STS1 ^ STS2 ^ ETX`.

### Hallazgo: XON/XOFF y el LRC

Si el puerto se abre con `xonxoff=True` y el **LRC de una respuesta vale `0x13` (XOFF) o `0x11` (XON)**, el sistema
lo consume como control de flujo y **la trama llega sin su LRC** (observado: `S1` de 132 bytes en lugar de 133,
LRC esperado `0x13`). Además, un XOFF recibido suspende la transmisión del host hasta recibir XON. Como el LRC de
`S1` varía con la hora, ocurre aproximadamente en 1 de cada 256 lecturas. Es una hipótesis para fallas esporádicas;
el driver no se ha modificado por este motivo.

## 3. Estado rápido (ENQ)

| STS1 | STS2 | Significado observado |
|---|---|---|
| 96 (`0x60`) | 64 (`0x40`) | Lista, sin documento abierto (lo que exige el driver para imprimir) |
| 97 (`0x61`) | 64 (`0x40`) | Documento fiscal en curso (factura o nota abierta) |

Los datos del cliente (`iR*`, `iS*`, `iF*`, `iD*`, `iI*`) **no** abren el documento; lo abre el primer ítem.

## 4. Status S1: estructura real HKA80

Familia SRP812/DT230/HKA80/PP9/TD1140. Respuesta de 16 líneas:

| # | Campo | Ejemplo |
|---|---|---|
| 0 | Status y cajero (`S1` + `00`) | `00` |
| 1 | Subtotal de ventas del día (15+2) | `00000000000100000` |
| 2 | Última factura | `00000100` |
| 3 | Facturas del día | `00004` |
| 4 | Última nota de débito | `00000005` |
| 5 | Notas de débito del día | `00000` |
| 6 | Última nota de crédito | `00000050` |
| 7 | Notas de crédito del día | `00001` |
| 8 | Último documento no fiscal | `00000201` |
| 9 | Documentos no fiscales del día | `00001` |
| 10 | **Contador de reportes de memoria fiscal** | `0002` |
| 11 | **Contador de cierres Z** | `0147` |
| 12 | RIF | `J-00000000-0` |
| 13 | Registro de máquina | `Z7C0000000` |
| 14 | Hora `HHMMSS` | `124028` |
| 15 | Fecha `DDMMYY` | `091026` |

**Discrepancia con el manual (pág. 54):** el manual lista *Cierres Z* antes de *Reportes de memoria fiscal*. La
máquina los devuelve **en el orden contrario**; el driver (`get_s1`) usa el orden correcto (un contador de Z alto es
coherente con el número de facturas; el de reportes de memoria, bajo).

Comportamiento observado:

- El *subtotal de ventas* sube con la **base de la factura sin IGTF**.
- Una **nota de crédito no modifica** el subtotal de ventas.

## 5. Status S2: documento en curso (clave para el total con IGTF)

Formato reducido (flag 63 = `00`): montos de **13 dígitos (11 + 2)**, separados por espacio y `0x0A`.

| # | Manual (pág. 55) | Significado real observado |
|---|---|---|
| 0 | Subtotal de bases imponibles | Base del documento |
| 1 | Subtotal de impuesto | IVA del documento |
| 2 | "Para uso futuro" | **Total del documento con IGTF** (coincide con el `TOTAL` impreso) |
| 3 | Cantidad de artículos | Devolvió `000000` con 1 artículo (no fiable) |
| 4 | Monto a pagar | **Saldo pendiente** (baja a 0 al pagar); no es el total |
| 5 | Cantidad de pagos | Pagos registrados |
| 6 | Tipo de documento | 0 = ninguno, 1 = factura, 2 = nota de crédito, 3 = nota de débito |

Secuencia con una factura exenta de Bs 1,00 pagada con divisa (código 20):

| Momento | Base | IVA | Campo 2 | Monto a pagar | Pagos | Tipo |
|---|---|---|---|---|---|---|
| Tras el ítem | 1,00 | 0,00 | **1,03** | 1,00 | 0 | 1 |
| Tras el pago `120` | 1,00 | 0,00 | **1,03** | 0,00 | 1 | 1 |
| Tras el cierre `199` | 0 | 0 | 0 | 0 | 0 | 0 |

Secuencia con **pago mixto** (exenta de Bs 2,00: Bs 1,00 en efectivo, código 01, y el resto en divisa, código 20):

| Momento | Base | Campo 2 | Monto a pagar | Pagos |
|---|---|---|---|---|
| Tras el ítem (sin pagos) | 2,00 | **2,06** (proyecta todo en divisa) | 2,00 | 0 |
| Tras el pago parcial en Bs `201000000000100` | 2,00 | **2,00** | 1,00 | 1 |
| Tras el pago total en divisa `120` | 2,00 | **2,03** (IGTF real del 3 % sobre 1,00) | 0,00 | 2 |

La nota de crédito equivalente muestra exactamente la misma secuencia.

Conclusiones:

- El campo 2 es **dinámico**: sin pagos proyecta el total como si todo se pagara en divisa y se recalcula tras cada
  pago. **Solo es el total real una vez registrados todos los pagos.**
- El **total impreso con IGTF** es el **campo 2 de S2 leído después del último pago y antes del `199`**. Tras el
  cierre, S2 vuelve a cero. El spooler usa este valor como `data.total`.
- Formato de pago parcial: `2` + código (2) + monto (10+2); por ejemplo `201000000000100` = código 01, Bs 1,00.

## 6. Status S3: tasas y flags

- Tasas (tipo 2 = excluido): `21600` = 16,00 %, `20800` = 8,00 %, `23100` = 31,00 %.
- **No** devuelve el campo "Valor IGTF" descrito para la familia HKA80.
- Flags (128 caracteres = 64 flags de 2 dígitos). Con valor distinto de cero en la máquina verificada:
  **30** = `01`, **43** = `02`, **50** = `01` (IGTF habilitado: medios de pago 20-24 y cierre `199` obligatorio),
  **63** = `00` (estructuras reducidas, montos 11+2).

## 7. Otros status

- **S4**: 24 acumulados diarios por medio de pago, de 13 dígitos (11+2). No incluye nombres.
- **S5**: RIF, registro de máquina, número de memoria de auditoría, capacidad y espacio libre en MB, documentos
  registrados.
- **SV**: modelo (`Z7C`) y país (`VE`).
- **U0X** (extracción de reporte X sin imprimir): la máquina respondió `05 15` (ENQ + NAK), es decir, lo rechazó.
  Pendiente averiguar la secuencia correcta.

## 8. Factura: secuencia real (flag 50 = 01)

| Paso | Comando | Respuesta |
|---|---|---|
| RIF del cliente | `iR*V000000000` | ACK |
| Razón social | `iS*CLIENTE DE PRUEBA` | ACK |
| Ítem exento | ` 000000010000001000PRODUCTO DE PRUEBA` | ACK |
| Pago total en divisa (código 20) | `120` | ACK |
| Cierre con IGTF | `199` | ACK |

Formato de ítem: `<tasa><precio 8+2><cantidad 5+3><descripción>`. Tasa en factura: `' '` exento, `!` general,
`"` reducida, `#` adicional.

Ticket impreso: `EXENTO Bs 1,00` · `Divisa Bs 1,03` · `BI IGTF3,00% Bs 1,00 IGTF3,00% Bs 0,03` ·
**`TOTAL Bs 1,03`**.

- El pago total (`1` + código) en divisa **agrega el IGTF automáticamente** sobre el saldo.
- Con flag 50 = `01` el documento queda abierto tras el pago (estado 97) hasta recibir el `199`. El `199` es
  **obligatorio** para cerrar toda factura, nota de crédito y nota de débito, con cualquier forma de pago (manual,
  Tablas 29 y 31); el driver lo envía siempre que el flag 50 vale `01`.
- Tras el `199` conviene esperar unos 3 s antes del siguiente comando; el estado vuelve a 96/64.

## 9. Nota de crédito: secuencia real

| Paso | Comando | Respuesta |
|---|---|---|
| Factura afectada | `iF*00000100` | ACK |
| Fecha afectada (`DD/MM/YY`) | `iD*09/10/26` | ACK |
| Registro de máquina | `iI*Z7C0000000` | ACK |
| RIF / razón social | `iR*...` / `iS*...` | ACK |
| Ítem exento | `d0000000010000001000PRODUCTO DE PRUEBA` | ACK |
| Pago total en divisa | `120` | ACK |
| Cierre | `199` | ACK |

El ticket de la nota imprime el número y la fecha de la factura afectada, el serial de la máquina, RIF y razón
social, y la misma estructura de pagos e IGTF.

## 10. Tasas de impuesto por tipo de documento

| Tasa | Factura | Nota de crédito | Nota de débito |
|---|---|---|---|
| Exento | `' '` | `d0` | `` `0 `` |
| General 16 % | `!` | `d1` | `` `1 `` |
| Reducida 8 % | `"` | `d2` | `` `2 `` |
| Adicional 31 % | `#` | `d3` | **`` `3 ``** |

Verificado con una nota de débito al 31 %: base 1,00, impuesto 0,31, tipo de documento 3. Antes de la corrección
(commit `0b4140f`) el driver enviaba `` `2 `` (8 %) para el 31 % en notas de débito.

## 11. Comportamiento ante fallas

### 11.1 Tapa abierta o sin papel antes de imprimir

- ENQ: `STS1 = 0x60`; `STS2` = `0x43` (fin de papel + error mecánico) o `0x42` (error mecánico en la entrega de
  papel). **No existe un código propio de "tapa abierta"** y no se distingue de la falta de papel.
- `S1` se lee con normalidad.
- Al conectar, el driver envía `7` (CANCEL); la máquina responde NAK porque no hay documento abierto, y `send_cmd`
  reintenta. El spooler responde error con `data.Estado` y `data.Error` reales (commit `8c562d4`) y el trabajo
  queda `failed` (reintento permitido).
- Al cerrar la tapa la máquina vuelve sola a `0x60/0x40`.

### 11.2 Tapa abierta a mitad del documento

- El documento se conserva (S2 sin cambios). Un pago enviado con la tapa abierta recibe **NAK** y no se registra.
- Al cerrar la tapa el documento sigue abierto y se puede continuar con normalidad.
- `7` (CANCEL) imprime "FACTURA ANULADA" y **consume un número fiscal** (documento anulado con monto 0, sin
  cambio en el subtotal de ventas). No requiere nota de crédito.

### 11.3 Corte de energía a mitad del documento

La HKA80 **conserva el documento abierto** tras apagar y encender (S2 intacto) y permite completarlo con `120` +
`199`. Es una diferencia con PNP, que cancela la factura abierta al encender (manual PNP, pág. 9). Al encender no
imprime nada; el USB nativo desaparece y reaparece (se pierde la ACL en Linux).

Consecuencia para el driver: `check_status()` envía CANCEL cuando la máquina no está lista, incluida la condición
de documento abierto (`0x61`); por tanto, la primera solicitud tras un corte puede cancelar un documento que se
podía continuar y consumir un número.

### 11.4 USB desconectado durante la impresión

Si el cable se corta justo después de enviar el `199`, la máquina **sí recibe el cierre y emite el documento**,
pero el spooler ve un error de lectura. Sin conciliación, el trabajo quedaría `failed` y un reintento de Odoo
reimprimiría. La única fuente de verdad es el contador de la máquina (S1). Por eso el spooler guarda el contador
antes de imprimir y concilia ante dudas (ver [Idempotencia y recuperación](../project.md#idempotencia-y-recuperación)).

Tras reconectar el USB con el spooler en ejecución, el singleton del driver conserva el puerto roto y todas las
solicitudes fallan (`CTS en falso`, código 128) hasta reiniciar el spooler; solo los errores 114/137 descartan la
instancia.

## 12. Comandos directos y reimpresiones (`/api/command`)

Reimpresión por número (manual, pág. 49): `RF/RC/RD/RT/RX/RZ/RR/RY/RE/RS/RA/RN/R@` + inicio (7 dígitos) + fin
(7 dígitos). `RU00000000000000` reimprime el último documento. Por fecha (pág. 50): minúsculas `Rf/Rc/.../R*` +
`0DDMMYY0DDMMYY`. Por RIF/C.I.: `RK<rif>`. `RZ`/`Rz` reimprimen Z y no deben usarse en producción.

| Prueba | Resultado |
|---|---|
| `RU00000000000000` | ACK en el primer intento; imprime copia del último documento registrado (aunque estuviera anulado). `status: true`. |
| `RF000` (mal formado) | NAK repetido y CANCEL con NAK; no imprime nada. El spooler responde `status: false` y la lista de comandos rechazados (commit `329aa5e`). |

PNP no tiene comandos `R...`; su equivalente es `0xBA` (ver [Pendientes](../project.md#pendientes)).

## 13. Respuesta a Odoo

- Éxito: `data.document_number`, `machine_serial`, `machine_report`, `document_date` y `total` (campo 2 de S2 antes
  del `199`, commit `f40d5fc`). La numeración se lee de los contadores de S1.
- Falla (tapa abierta): HTTP 400 con
  `{"status": false, "message": "Impresora no disponible - Estado: ..., Error: ...", "data": {"Estado": "...", "Error": "..."}}`.
- `/api/ping`: devuelve el serial real de la máquina (`S5`, sin CANCEL, sin crear instancia ni modificar el
  template) con respaldo en el serial configurado (commit `2bd8ffb`).

## 14. Observaciones del driver (sin cambios)

El driver está ajustado para producción y no se modifica salvo necesidad explícita y crítica. Observaciones:

- `_read_status` lee solo los bytes disponibles tras 0,5 s (tramas largas podrían truncarse).
- El host no envía ACK tras las lecturas (la Tabla 10 del manual indica que debería).
- `send_cmd` reintenta hasta 3 veces ante falta de ACK: riesgo de duplicar un ítem o pago.
- `S4`, `S2E` y `S21-25` no pasan por `_read_status`.
- El encabezado del siguiente documento se pre-imprime al terminar cada ticket; abrir la tapa o mover el papel lo
  descuadra. Es configurable en la impresora, pero el flag no figura en la Tabla 72 del manual v8.5.0 (ver
  [Pendientes](../project.md#pendientes)).
