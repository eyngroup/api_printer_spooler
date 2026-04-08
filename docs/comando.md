**==> picture [95 x 43] intentionally omitted <==**

**MANUAL DE PROTOCOLOS Y COMANDOS V8.5.0 INTEGRACIÓN**

Código: **MIA-CINT-01** Versión N° **8.5.0** Fecha: **23/08/2022** Página  2

The Factory HKA, C.A.

## MANUAL DE PROTOCOLOS Y COMANDOS

## VERSIÓN 8.5.0 - VENEZUELA

The Factory HKA

La California Norte, Callejón Gutiérrez Edif. Riva, PB Ofic. 2-1, Caracas - Venezuela Teléfono (212) 237.4112 • 2398176 Departamento de Soporte e Integración integration@thefactoryhka.com

**The Factory HKA, C.A. VENEZUELA**

**==> picture [95 x 43] intentionally omitted <==**

**MANUAL DE PROTOCOLOS Y COMANDOS** Código: **MIA-CINT-01 V8.5.0** Versión N° **8.5.0** Fecha: **23/08/2022 INTEGRACIÓN** Página  3

## CONTROL DE CAMBIO

|Versión<br>N.º|Fecha de<br>Actualización|Editado Por|Descripción de cambio|
|---|---|---|---|
|8.5.0|23/08/2022|Integración|Cambio  de  formato,  incorporación  de  IGTF,<br>impuesto  percibido,  uso  de  los  fag  21,  63,  50  y<br>actualización de tablas de estatus.|


**The Factory HKA, C.A. VENEZUELA**

||**MANUAL DE PROTOCOLOS Y COMANDOS**<br>**V8.5.0**|Código:**MIA-CINT-01**|
|---|---|---|
|||Versión N°**8.5.0**|
||**INTEGRACIÓN**|Fecha:**23/08/2022**|
|||Página  4|
||||
|ÍNDICE DE CONTENIDO<br>**OBJETIVO**<br>**ALCANCE**<br>**PRECAUCIONES DURANTE SU MANIPULACIÓN**<br>**CONCEPTOS BÁSICOS**<br>¿QUÉ ES UNA IMPRESORA FISCAL?<br>¿CÓMO ESTÁ CONSTITUIDA LA IMPRESORA FISCAL?<br>MEMORIA FISCAL<br>MEMORIA AUDITORIA<br>MEMORIA DE TRABAJO<br>MODO ENTRENAMIENTO<br>MODO FISCAL<br>DOCUMENTOS QUE EMITE LA IMPRESORA FISCAL<br>**COMUNICACIÓN ENTRE EL PC Y LA IMPRESORA FISCAL**<br>**PROTOCOLO DE COMUNICACIÓN**<br>**CONFIGURACIÓN**<br>**ESTRUCTURA DE LA TRAMA DE COMUNICACIÓN**<br>**CONTROL DE TRÁFICO Y TRAMA DE COMUNICACIÓN**<br>CARACTERES DE CONTROL<br>RECEPCIÓN DE ACK (0X06)<br>RECEPCIÓN DE NAK (0X15)<br>SECUENCIA DE COMANDOS DE COMUNICACIÓN<br>LEER ESTADO<br>COMANDOS SIMPLES<br>COMANDO DE LECTURA<br>COMANDO DE LECTURA DE INFORMACIÓN|||


**The Factory HKA, C.A. VENEZUELA**

|**MANUAL DE PROTOCOLOS Y COMANDOS**<br>**V8.5.0**|Código:**MIA-CINT-01**<br>Versión N°**8.5.0**|||
|---|---|---|---|
|**INTEGRACIÓN**|Fecha:**23/08/2022**|||
||Página  5|||
|||||
|**COMANDOS PARA LA PROGRAMACIÓN DE LA IMPRESORA FISCAL**||**20**||
|INICIO Y FIN DE CAJERO||21||
|MEDIOS DE PAGO||22||
|PROGRAMACIÓN DE HORA Y FECHA||23||
|PROGRAMACIÓN Y REGISTRO DE TASAS DE IMPUESTO||23||
|ENCABEZADO Y PIE DE PÁGINA||24||
|BANDERAS DE PROGRAMACIÓN (FLAGS)||24||
|CONFIGURACIÓN DEL (FLAG 21)||25||
|**MANEJO DEL VISOR O DISPLAY DE PRECIOS DEL CLIENTE**||**27**||
|APERTURA DE GAVETA Y RETIRO/FONDO DE CAJA||27||
|IMPRIMIR PROGRAMACIÓN||28||
|**CÓDIGO DE BARRAS**||**29**||
|**TABLA DE CARACTERES**||**30**||
|**COMANDOS PARA GENERAR DOCUMENTOS FISCALES**||**32**||
|COMANDOS PARA EL REGISTRO DE UN ÍTEM EN UNA FACTURA||32||
|EJEMPLO PARA GENERAR UNA FACTURA||33||
|COMANDOS PARA GENERAR UNA NOTA DE CRÉDITO (DEVOLUCIÓN)||35||
|EJEMPLO PARA GENERAR UNA NOTA DE CRÉDITO (DEVOLUCIÓN)||36||
|COMANDOS PARA GENERAR UNA NOTA DE DÉBITO||38||
|EJEMPLO PARA GENERAR UNA NOTA DE DÉBITO||39||
|**COMANDOS PARA GENERAR DOCUMENTOS NO FISCALES**||**41**||
|**COMANDOS GENERALES**||**42**||
|TABLA DE IMPRESORA QUE ACEPTAN COMANDOS GENERALES||42||
|EJEMPLO DE COMANDOS GENERALES PARA REALIZAR UNA FACTURA||43||
|EJEMPLO DE COMANDOS GENERALES PARA REALIZAR UNA NOTA DE CRÉDITO||45||
|EJEMPLO DE COMANDOS GENERALES PARA REALIZAR UNA NOTA DE DÉBITO||47||


**The Factory HKA, C.A. VENEZUELA**

||**MANUAL DE PROTOCOLOS Y COMANDOS**<br>**V8.5.0**|Código:**MIA-CINT-01**|
|---|---|---|
|||Versión N°**8.5.0**|
||**INTEGRACIÓN**|Fecha:**23/08/2022**|
|||Página  6|
||||
|**REIMPRESIÓN DE DOCUMENTOS DE LA MEMORIA DE AUDITORIA**<br>REIMPRESIÓN POR RANGO DE NÚMERO<br>REIMPRESIÓN POR RANGO DE FECHA<br>REIMPRESIÓN POR NÚMERO DE CÉDULA O RIF<br>**EXTRACCIÓN DE DOCUMENTOS DE LA MEMORIA DE AUDITORIA**<br>EXTRACCIÓN POR RANGO DE NÚMERO<br>EXTRACCIÓN POR RANGO DE FECHA<br>EXTRACCIÓN POR NÚMERO DE CÉDULA O RIF<br>**LEER STATUS DE INFORMACIÓN**<br>STATUS S1<br>STATUS S2<br>ESTRUCTURA DE LA TRAMA DEL STATUS S2E<br>ESTRUCTURA DE LA TRAMA DEL STATUS S21<br>ESTRUCTURA DE LA TRAMA DEL STATUS S22<br>ESTRUCTURA DE LA TRAMA DEL STATUS S23<br>ESTRUCTURA DE LA TRAMA DEL STATUS S24<br>ESTRUCTURA DE LA TRAMA DEL STATUS S25<br>STATUS S3<br>STATUS S4<br>STATUS S5<br>STATUS S8E<br>STATUS S8P<br>STATUS SV<br>**IMPRIMIR REPORTES**<br>IMPRIMIR REPORTE DE MEMORIA FISCAL POR NÚMERO<br>IMPRIMIR REPORTE DE MEMORIA FISCAL POR FECHA|||


**The Factory HKA, C.A. VENEZUELA**

||**MANUAL DE PROTOCOLOS Y COMANDOS**<br>**V8.5.0**|Código:**MIA-CINT-01**|
|---|---|---|
|||Versión N°**8.5.0**|
||**INTEGRACIÓN**|Fecha:**23/08/2022**|
|||Página  7|
||||
|**EXTRACCIÓN DE REPORTES**<br>REPORTE X<br>REPORTE Z<br>**EXTRACCIÓN DE REPORTES DE LA MEMORIA DE AUDITORIA**<br>EXTRACCIÓN POR RANGO DE NÚMERO<br>EXTRACCIÓN POR FECHA<br>EXTRACCIÓN DETALLADA POR DOCUMENTO<br>RESUMEN DE LAS ESTRUCTURAS DE LAS TRAMAS (S1 - S2)<br>RESUMEN DE LAS ESTRUCTURAS DE LAS TRAMAS (S3 - S4 - S5)<br>RESUMEN DE LAS ESTRUCTURAS DE LAS TRAMAS (X,Z)<br>**TABLA DE FLAG DE CONFIGURACIÓN DEL USUARIO**<br>**CONFIGURACIÓN DEL IMPUESTO IGTF**<br>**SUGERENCIAS DE PROGRAMACIÓN PARA DESARROLLAR SU SISTEMA**<br>**TEST PARA AUTOEVALUAR INTEGRACIÓN DE SISTEMA ADMINISTRATIVO**|||


**The Factory HKA, C.A. VENEZUELA**

||**MANUAL DE PROTOCOLOS Y COMANDOS**<br>**V8.5.0**|Código:**MIA-CINT-01**|
|---|---|---|
|||Versión N°**8.5.0**|
||**INTEGRACIÓN**|Fecha:**23/08/2022**|
|||Página  8|


## **1. OBJETIVO**

El  presente  documento  tiene  como  propósito  brindar  información  técnica,  a  las  personas naturales  y  jurídicas  que  desarrollan  software  para  permitir  la  conectividad  con  las  máquinas fiscales,  acerca  de  los  comandos  y  funcionalidades  de  los  cuales  disponen  las  impresoras fiscales que comercializa The Factory HKA C.A. a través de sus distribuidores autorizados.

## **2. ALCANCE**

Este  documento  contempla  la  información  necesaria  para  iniciar  un  desarrollo  que  utilice directamente  la  comunicación  del  puerto  serial  de  la  impresora.  Igualmente,  expone  ejemplos junto  a  los  comandos  necesarios  para  generar  documentos  fiscales  y  no  fiscales,  así  como  la estructura de las extracciones referente a los reportes que puede generar la impresora fiscal.

**The Factory HKA, C.A. VENEZUELA**

**MANUAL DE PROTOCOLOS Y COMANDOS V8.5.0 INTEGRACIÓN**

**==> picture [95 x 43] intentionally omitted <==**

Código: **MIA-CINT-01** Versión N° **8.5.0** Fecha: **23/08/2022** Página  9

## **3. PRECAUCIONES DURANTE SU MANIPULACIÓN**

**==> picture [474 x 486] intentionally omitted <==**

**----- Start of picture text -----**<br>
 NO ENCHUFE VARIOS EQUIPOS A UNA<br> NO MANIPULE EL CABLE CON LAS MANOS<br> MISMA TOMA DE CORRIENTE AL MISMO<br> TIEMPO.<br> HÚMEDAS.<br> EVITE QUE EL CABLE SE DOBLE EN<br> SI LA IMPRESORA GENERA HUMO, OLOR O<br> ÁNGULOS MAYORES A 90° O QUE ESTÉ<br> RUIDOS EXTRAÑOS, APAGUE Y<br> DEBAJO DE OBJETOS PESADOS.<br> DESCONECTE. LLAME A SU DISTRIBUIDOR<br> PARA REPARACIONES.<br> NO INTENTE DESMONTAR O REPARAR LA   NO DEJE CAER AGUA U OTROS OBJETOS<br> IMPRESORA. LLAME A SU DISTRIBUIDOR SI   SOBRE LA IMPRESORA. SI ESTO SUCEDE,<br> NECESITA ESTOS SERVICIOS.   DESCONECTE Y LLAME A SU DISTRIBUIDOR.<br>**----- End of picture text -----**<br>


Imagen 1. Precaución Durante su Manipulación

**The Factory HKA, C.A. VENEZUELA**

**MANUAL DE PROTOCOLOS Y COMANDOS V8.5.0 INTEGRACIÓN**

**==> picture [95 x 43] intentionally omitted <==**

Código: **MIA-CINT-01** Versión N° **8.5.0** Fecha: **23/08/2022** Página  10

## **4. CONCEPTOS BÁSICOS**

Algunos  conceptos  básicos  que  pueden  ayudar  a  manejar  las  impresoras  fiscales  son  los siguientes:

## **4.1. ¿QUÉ ES UNA IMPRESORA FISCAL?**

Es  una  unidad  de  impresión  autorizada  por  el  Servicio  Nacional  Integrado  de  Administración Aduanera  y  Tributaria  (SENIAT)  para  la  emisión  de  documentos  fiscales  tales  como:  Facturas, Notas  de  Crédito,  Notas  de  Débito,  Reporte  Z  y  Documentos  No  Fiscales,  Reporte  de  Memoria Fiscal,  en  virtud  del  cumplimiento  o  exigencias  que  se  establecen  en  la  ley  para  el  manejo  de impresoras fiscales.

## **4.2. ¿CÓMO ESTÁ CONSTITUIDA LA IMPRESORA FISCAL?**

La impresora fiscal está constituida por los siguientes módulos:

**==> picture [314 x 181] intentionally omitted <==**

Imagen 2. Estructura de la Impresora Fiscal

La  impresora  fiscal  está  compuesta  por  ciertos  componentes  de  hardware  que  la  distinguen  de una  impresora  regular.  Por  lo  general,  dichos  componentes  se  ubican  sobre  una  única  placa base  distinta  a  la  del  módulo  de  impresión  y  comprende  una  memoria  fiscal,  una  memoria  de trabajo y una memoria de auditoría.

A  la  integración  de  un  software  sobre  un  hardware  para  ejecutar  alguna  acción  determinada,  se le  denomina  Firmware.  La  impresora  fiscal  está  controlada  por  dicho  software,  quien  regula  su correcto  funcionamiento  (particularmente  sobre  los  componentes  principales:  memorias  Fiscal, de  Auditoría  y  de  Trabajo).  Todos  estos  componentes  serán  descritos  con  mayor  detalle  en  las siguientes secciones de este manual.

**The Factory HKA, C.A. VENEZUELA**

**MANUAL DE PROTOCOLOS Y COMANDOS V8.5.0 INTEGRACIÓN**

**==> picture [95 x 43] intentionally omitted <==**

Código: **MIA-CINT-01** Versión N° **8.5.0** Fecha: **23/08/2022** Página  11

## **4.3. MEMORIA FISCAL**

Dispositivo  electrónico  de  almacenamiento,  con  capacidad  de  2000,  su  función  es  almacenar  la información  contenida  en  los  reportes  Z  emitidos  por  el  equipo.  Es  el  único  tipo  de  documentos que almacena. Se encuentra adherida al chasis de la impresora.

## **4.4. MEMORIA AUDITORIA**

Tiene  una  capacidad  de  almacenamiento  de  2 GB.  En  este  dispositivo  se  almacenan electrónicamente  todas  las  transacciones  realizadas  a  través  de  la  impresora  fiscal  (incluyendo las copias de todos los documentos impresos y copias de copias).

## **4.5. MEMORIA DE TRABAJO**

Tiene  una  capacidad  de  almacenamiento  que  varía  dependiendo  del  modelo  de  la  impresora fiscal.  Se  encuentra  integrada  al  módulo  fiscal.  Su  función  es  almacenar  la  información  fiscal  de una  jornada  laboral,  en  ella  se  almacenan  los  contadores  y  los  acumuladores  de  ventas  (estos últimos, se inicializan a cero al hacer un reporte Z).

## **4.6. MODO ENTRENAMIENTO**

Es  el  modo  de  una  impresora  antes  de  su  fiscalización.  En  este  estado,  ni  la  memoria  fiscal  ni  la de  auditoría  están  activas;  es  decir,  no  graban  información,  por  lo  que  no  se  pueden  generar Reportes Históricos ni reimpresiones de la memoria de auditoría o lecturas del status S1.

## **4.7. MODO FISCAL**

Es  el  modo  de  una  impresora  una  vez  se  ha  cargado  la  data  fiscal  mediante  el  uso  del Fiscalizador  (aplicación).  Luego  de  la  fiscalización,  ambas  memorias  son  activadas  y  no  pueden devolverse  al  modo  entrenamiento.  En  este  punto,  todos  los  documentos  emitidos  tienen  un carácter legal ante el ente regulador.

## **4.8. DOCUMENTOS QUE EMITE LA IMPRESORA FISCAL**

Los  documentos  que  emite  la  impresora  cumplen  con  todas  las  exigencias  de  Ley  establecidas, además  genera  otros  documentos  con  fines  de  control  administrativo.  Estos  documentos  se dividen en:

**The Factory HKA, C.A. VENEZUELA**

**==> picture [95 x 43] intentionally omitted <==**

**MANUAL DE PROTOCOLOS Y COMANDOS** Código: **MIA-CINT-01 V8.5.0** Versión N° **8.5.0** Fecha: **23/08/2022 INTEGRACIÓN** Página  12

**==> picture [316 x 203] intentionally omitted <==**

Imagen 3. Documentos emitidos por la impresora fiscal

## **5. COMUNICACIÓN ENTRE EL PC Y LA IMPRESORA FISCAL**

El  protocolo  de  comunicación  de  las  impresoras  fiscales  se  basa  en  el  estándar  RS232  de comunicación  serial.  Para  esto,  es  necesaria  una  interfaz  de  aplicación  que  gestione  este protocolo,  esto  es,  que  sea  capaz  de  enviar  los  comandos  desde  el  computador  hacia  la impresora  e  interpretar  las  respuestas  que  está  retorna.  Estos  comandos  corresponden  a protocolos seriales almacenados en el firmware de la impresora.

Los  comandos  de  estos  protocolos  pueden  ser  enviados  a  la  impresora  de  dos  maneras: directamente  a  través  del  manejo  del  puerto  serial  (llamado  Protocolo  Directo),  o  utilizando interfaces  de  programación  de  aplicaciones  (API,  Application  Programming  Interface)  las  cuales dependen  del  sistema  operativo  a  utilizar  y  del  lenguaje  de  programación  utilizado  para desarrollar el Sistema Administrativo que estará asociado la impresora.

**==> picture [62 x 59] intentionally omitted <==**

**==> picture [107 x 36] intentionally omitted <==**

**==> picture [71 x 49] intentionally omitted <==**

**==> picture [46 x 30] intentionally omitted <==**

**==> picture [34 x 30] intentionally omitted <==**

**==> picture [63 x 38] intentionally omitted <==**

**==> picture [63 x 38] intentionally omitted <==**

**==> picture [46 x 41] intentionally omitted <==**

**==> picture [43 x 38] intentionally omitted <==**

Imagen 4. Interfaz de Aplicación

**The Factory HKA, C.A. VENEZUELA**

||**MANUAL DE PROTOCOLOS Y COMANDOS**<br>**V8.5.0**|Código:**MIA-CINT-01**|
|---|---|---|
|||Versión N°**8.5.0**|
||**INTEGRACIÓN**|Fecha:**23/08/2022**|
|||Página  13|


Actualmente,  The  Factory  HKA  posee  una  amplia  gama  de  herramientas  de  integración  que contienen  estas  API’s  para  los  diferentes  lenguajes  de  programación  y  sistemas  operativos disponibles.

En  la  siguiente  tabla  se  muestran  los  diferentes  lenguajes  soportados  por  las  herramientas  de desarrollo  de  The  Factory  HKA.  En  la  siguiente  tabla  se  muestran  los  diferentes  lenguajes soportados por las herramientas de desarrollo de The Factory HKA:

|**Sistema Opera�vo**|**Tecnología**|**Libreria**|**Lenguajes del Demo**|
|---|---|---|---|
|Windows|**Win32**|**Tfhkaif (DLL)**|**Delphi - VB6 - C# - FoxPro -**<br>**PowerBuilder - VBA**|
||**.NET**|**Tfhka.Net (DLL)**|**C# - Visual Basic**|
||**JAVA**|**TfhkaJava64 (JAR)**|**JAVA**|
||**Python**|**Tfhka.py (DLL)**|**Python 2.7**|
||**CONSOLA**|**IntTfhka**|**Aplicación + PHP**|
||**PHP**|**TfhkaPHPTCP**|**PHP**|
|||||
|Linux / UNIX|**CONSOLA**|**Tfnulx**|**Aplicación + PHP**|
||**JAVA**|**TfhkaJava64 (JAR)**|**JAVA**|


Tabla 1. Librerías y demostraciones.

## **6. PROTOCOLO DE COMUNICACIÓN**

El  Protocolo  de  Comunicación  es  la  manera  en  que  la  computadora  realiza  el  intercambio  de datos  con  la  impresora.  Basado  en  el  estándar  serial  RS232,  el  Protocolo  de  Comunicación  está estructurado  mediante  una  trama  conformada  por  una  señal  de  inicio  (0x02h)  seguida  de  los caracteres  que  conforman  los  comandos  y  datos  a  enviar  a  la  impresora,  luego  un  carácter  de fin de trama (0x03h) y una señal de detección de errores.

De  igual  manera,  si  la  impresora  ha  de  retornar  algún  valor,  lo  hará  en  una  trama  conformada  de manera idéntica a la anteriormente descrita.

**The Factory HKA, C.A. VENEZUELA**

||**MANUAL DE PROTOCOLOS Y COMANDOS**<br>**V8.5.0**|Código:**MIA-CINT-01**|
|---|---|---|
|||Versión N°**8.5.0**|
||**INTEGRACIÓN**|Fecha:**23/08/2022**|
|||Página  14|


## **7. CONFIGURACIÓN**

El  protocolo  utilizado  para  enviar  información  a  la  impresora  es  el  Serial  RS232.  La  imagen  N.º5 muestra las señales de control usadas en el protocolo.

**==> picture [105 x 94] intentionally omitted <==**

**==> picture [117 x 91] intentionally omitted <==**

Imagen 5. Señales de control.

|**Conector RJ11**<br>**Pinou**<br>**t del**<br>**RJ11**<br>**Color**<br>**Señal**<br>**Control**<br>**1**<br>Blanco<br>CTS<br>**2**<br>-<br>-<br>**3**<br>Amarillo<br>Tierra<br>**4**<br>Rojo<br>Rx<br>**5**<br>Verde<br>Tx<br>**6**<br>Azul<br>RTS|**Pinout para conector DB9**<br>**Pin**<br>**Señal**<br>**En Inglés**<br>**Siglas**<br>**Tipo de**<br>**Señal**<br>**Función**<br>**2**<br>Receptor<br>de datos<br>Received<br>Data<br>RxD<br>Entrada<br>Pin de<br>recepción de<br>datos<br>**3**<br>Transmisor<br>de datos<br>Transmitted<br>Data<br>TxD<br>Salida<br>Pin de<br>transmisión de<br>datos<br>**5**<br>Señal de<br>tierra<br>Common<br>Ground<br>SG<br>-<br>Tierra<br>**7**<br>Solicitud<br>de envío<br>Request to<br>send<br>RTS<br>Salida<br>El PC puede<br>recibir datos<br>(porque no<br>está ocupado)<br>**8**<br>Listo para<br>enviar<br>Clear to<br>Send<br>CTS<br>Entrada<br>El aparato<br>conectado<br>puede recibir<br>datos|
|---|---|
|Tabla 2. Señales de control.||


Tabla 2. Señales de control.

**The Factory HKA, C.A. VENEZUELA**

||**MANUAL DE PROTOCOLOS Y COMANDOS**<br>**V8.5.0**|Código:**MIA-CINT-01**|
|---|---|---|
|||Versión N°**8.5.0**|
||**INTEGRACIÓN**|Fecha:**23/08/2022**|
|||Página  15|


Una vez que la PC ha activado la señal RTS (solicitud a la impresora que esté conectada y lista para recibir datos), la impresora fiscal responde con la señal CTS (Impresora lista) para indicar que es posible la recepción.

Los parámetros de configuración del puerto serial son los siguientes:

|**Transmisión de data**|**Serial, Asíncrona**|
|---|---|
|Baud rate|9600 bps|
|Bit de datos|8 bits|
|Paridad|Par|
|Bits de stop|1|
|Tabla 3. Parámetros de confguración de puerto serial.||


## **8. ESTRUCTURA DE LA TRAMA DE COMUNICACIÓN**

La  trama  de  comunicación  es  el  conjunto  de  datos  que  debe  enviarse  a  la  impresora  para  que cumpla  determinada  instrucción;  debe  enviarse  en  orden  y  está  constituida  siempre  por  cuatro secciones.

**==> picture [471 x 61] intentionally omitted <==**

Imagen 6. Estructura de la trama a enviar

Las secciones de la trama de comunicación son las siguientes:

- **Carácter  de  inicio  de  trama  (STX):** representado  por  el  carácter  0x02h,  es  un  valor

- **DATA** :  Es  el  comando  y  sus  argumentos,  enviados  a  la  impresora  para  que  ejecute  una determinada acción.

- **Carácter  de  Fin  de  Trama  (ETX)** :  representado  por  el  carácter  0x03h  indica  el  fin  de  la trama y es un valor reservado únicamente a este fin.

- **LRC** :  Su  valor  es  el  OR  exclusivo  (XOR)  entre  la  DATA  y  ETX,  dirigido  a  la  detección  de error de la trama.

**IMPORTANTE** :  El  desarrollador  podrá  utilizar  el  protocolo  directo  o  usar  los  componentes  de  integración que  The  Factory  HKA  tiene  a  su  disposición.  Al  emplear  el  protocolo  directo  la  trama  se  envía  completa, cuando se emplean las interfaces o componentes de Integración solamente se envía el campo DATA.

**The Factory HKA, C.A. VENEZUELA**

||**MANUAL DE PROTOCOLOS Y COMANDOS**<br>**V8.5.0**|Código:**MIA-CINT-01**|
|---|---|---|
|||Versión N°**8.5.0**|
||**INTEGRACIÓN**|Fecha:**23/08/2022**|
|||Página  16|


Si  se  emplean  las  herramientas  de  integración  desarrolladas  por  The  Factory  HKA,  se  envía  el  contenido de  DATA  mediante  caracteres  ASCII  y  los  componentes  de  integración  se  encargan  de  convertirlos  a  su respectivo equivalente hexadecimal para enviarlos a la impresora.

Por  ejemplo,  si  se  envía  por  protocolo  directo  la  instrucción  de  impresión  de  Reporte  X,  se  debe  enviar  a  la impresora una trama como la que se muestra en la siguiente tabla.

|**ASCII**|**S**TX|**I**|**0**|**X**|**ETX**|LRC|
|---|---|---|---|---|---|---|
|**HEX**|02|**49**|**30**|**58**|03|22|
||**Inicio de trama**|**DATA**|||**Fin de Trama**|**LRC**|
|Tabla 4. Ejemplo de instrucción con protocolo directo.|||||||


Sí,  se  emplean  las  herramientas  de  integración  desarrolladas  por  The  Factory  HKA,  la  trama anterior  sé  reduciría  sólo  a  la **DATA** ,  y  se  utilizará  una  función  para  enviarla  a  la  impresora (verificar el respectivo manual de la librería a usar).

## **9. CONTROL DE TRÁFICO Y TRAMA DE COMUNICACIÓN**

## **9.1. CARACTERES DE CONTROL**

La  mayoría  de  caracteres  de  control  son  representados  con  valores  de  caracteres  no imprimibles,  por  lo  que  su  inclusión  en  la  trama  -  Protocolo  Directo  -  debe  realizarse  mediante  su valor hexadecimal.

|**Carácter**|**Hexadecimal**|**Hexadecimal**|**Descripción**|
|---|---|---|---|
|**STX**|0x02||Inicio de Trama|
|**ENQ**|0x05||Solicitud de status & Error|
|**ETX**|0x03||Fin de Trama|
|**ACK**|0x06||Reconocimiento del comando|
|**NAK**|0x15||No Reconocimiento del comando|
|**ETB**|0x17||Fin del bloque de transmisión|
|**LRC**|0x00-0xFF OR exclusivo de data con ETX. (Incluyendo ETX.)|||
|**EOT**|0X04|Fin de trasmisión||
|Tabla 5. Caracteres de control.||||


**The Factory HKA, C.A. VENEZUELA**

||**MANUAL DE PROTOCOLOS Y COMANDOS**<br>**V8.5.0**|Código:**MIA-CINT-01**|
|---|---|---|
|||Versión N°**8.5.0**|
||**INTEGRACIÓN**|Fecha:**23/08/2022**|
|||Página  17|


De  la  lista  anterior  cabe  destacar  dos  caracteres  de  Control,  ya  que  constituyen  las  principales respuestas de la impresora ante los comandos enviados.

## **9.2. RECEPCIÓN DE ACK (0X06)**

Ocurre cuando se satisfacen las siguientes condiciones:

- LRC y DATA son correctos.

- El comando es aceptable para la condición actual de la impresora.

## **9.3. RECEPCIÓN DE NAK (0X15)**

Ocurre ante cualquiera de las siguientes condiciones:

- LRC errado.

- El comando enviado a la impresora no era válido.

Si  se  envía  un  comando  y  la  impresora  está  ocupada,  no  se  retorna  ningún  valor.  Se  puede verificar  esta  condición  a  través  de  la  señal  DTR  de  la  impresora.  Se  debe  enviar  ENQ  o  NAK  de regreso a la impresora si un error de comunicación fue detectado en la PC.

Para  los  comandos  donde  las  consultas  deben  retornar  una  trama  de  información,  tales  como  la extracción  de  datos  de  la  Memoria  de  Auditoría  para  la  obtención  de  reportes,  se  lleva  a  cabo  el siguiente protocolo:

**==> picture [304 x 117] intentionally omitted <==**

Imagen 7. Caracteres de control para consulta de una trama de comunicación

El comando de solicitud de lectura de la memoria varía de acuerdo al tipo de reporte a requerir, así como también varía la estructura de la trama devuelta por la impresora.

## **10. SECUENCIA DE COMANDOS DE COMUNICACIÓN**

## **10.1. LEER ESTADO**

Para  determinar  el  estado  en  que  se  encuentra  la  impresora  fiscal,  se  envía  un  Enquirement (ENQ=0x05h).

**The Factory HKA, C.A. VENEZUELA**

||**MANUAL DE PROTOCOLOS Y COMANDOS**<br>**V8.5.0**|Código:**MIA-CINT-01**|
|---|---|---|
|||Versión N°**8.5.0**|
||**INTEGRACIÓN**|Fecha:**23/08/2022**|
|||Página  18|


Este  comando  se  envía  a  la  impresora  fiscal  para  determinar  el  estado  en  que  se  encuentra  y  si existe  un  error,  evaluarlo.  Cuando  se  envía  un  ENQ  a  la  impresora,  esta  responde  con  una  trama similar  a  la  de  recepción,  donde  DATA  es  un  par  de  bytes  que  contienen  la  información  del Estado y el posible Error de la impresora .

|**PC**|**→→→→→→→→→→→→→→→**<br> **←←←←←←←←←←←←←←←**|**Impresora**|
|---|---|---|
|ENQ||STX-STATUS-ETX-LRC|


Tabla 6. Secuencia de comunicación con la impresora fiscal

## La impresora responderá una trama con la siguiente estructura:

**==> picture [471 x 55] intentionally omitted <==**

Imagen 8. Trama de respuesta de la impresora

Dónde:

- STS1 corresponde al Estado de la impresora.

- STS2 corresponde al Error de la impresora.

Las  siguientes  tablas  contienen  los  valores  frecuentes  para  los  bytes  de  Status  (STS1)  y  Error (STS2) de las impresoras fiscales:

|**Valores de Status (STS1)**|**Valores de Status (STS1)**|
|---|---|
|**0x40**|Modo Entrenamiento y en Espera|
|**0x41**|Modo Entrenamiento y en medio de una Transacción Fiscal|
|**0x42**|Modo Entrenamiento y en medio de una Transacción No fscal|
|**0x60**|Modo Fiscal y en Espera|
|**0x68**|Modo Fiscal con la MF llena y en Espera|
|**0x61**|Modo Fiscal y en medio de una Transacción Fiscal|
|**0x69**|Modo Fiscal con la MF llena y en medio de una Transacción Fiscal|
|**0x62**|Modo Fiscal y en medio de una Transacción No fscal|
|**0x6A**|Modo Fiscal con la MF llena y en Transacción No fscal|
|Tabla 7. Valores de la trama de status.||


**The Factory HKA, C.A. VENEZUELA**

**==> picture [95 x 43] intentionally omitted <==**

**MANUAL DE PROTOCOLOS Y COMANDOS** Código: **MIA-CINT-01 V8.5.0** Versión N° **8.5.0** Fecha: **23/08/2022 INTEGRACIÓN** Página  19

|**Valores de Error (STS2)**|**Valores de Error (STS2)**|
|---|---|
|**0x40**|Ningún error|
|**0x48**|Error gaveta|
|**0x41**|Error sin papel|
|**0x42**|Error mecánico de la impresora / papel|
|**0x43**|Error mecánico de la impresora y fn de papel|
|**0x60**|Error fscal|
|**0x64**|Error en la memoria fscal|
|**0x6C**|Error memoria fscal llena|
|Tabla 8. Valores de la trama de error.||


## **10.2. COMANDOS SIMPLES**

|**PC**||**Impresora**|
|---|---|---|
|(Ejecución Normal “ACK”)<br>STX-CMD-DATA-ETX-LRC|→→→→→→→→→<br> ←←←←←←←←←|ACK|
|(Ejecución con Error “NAK”)<br>STX-CMD-DATA-ETX-LRC|→→→→→→→→→<br> ←←←←←←←←←|NAK<br>Error de Comunicación|
|(Impresora Ocupada “NAK”)<br>STX-CMD-DATA-ETX-LRC|→→→→→→→→→<br> ←←←←←←←←←|DTR off|
|Tabla 9. Secuencia de lectura de comandos simples.|||


En  el  caso  en  que  la  impresora  regresa  un  NAK  (no  reconocimiento  o  el  comando  no  fue  válido). Cuando  se  envía  un  comando  y  la  impresora  está  ocupada,  no  se  retorna  ningún  valor,  esta condición puede ser verificada a través de la señal DTR de la impresora.

**The Factory HKA, C.A. VENEZUELA**

**==> picture [95 x 43] intentionally omitted <==**

**MANUAL DE PROTOCOLOS Y COMANDOS** Código: **MIA-CINT-01 V8.5.0** Versión N° **8.5.0** Fecha: **23/08/2022 INTEGRACIÓN** Página  20

## **10.3. COMANDO DE LECTURA**

|**PC**||**Impresora**|
|---|---|---|
|STX-CMD-DATA-ETX-LRC<br>ACK|→→→→→→→→→<br> ←←←←←←←←←<br> →→→→→→→→→|STX-CMD-DATA-ETX-LRC|
|Tabla 10. Secuencia de comandos de lectura|||


Se  debe  enviar  ENQ  o  NAK  de  regreso  a  la  impresora  si  un  error  de  comunicación  fue  detectado en el host (PC).

## **10.4. COMANDO DE LECTURA DE INFORMACIÓN**

|**PC**||**Impresora**|
|---|---|---|
|STX-CMD1-DATA-ETX-LRC<br>ACK<br>ACK|→→→→→→→→→<br> ←←←←←←←←←<br> →→→→→→→→→<br> ←←←←←←←←←<br> →→→→→→→→→<br> ←←←←←←←←←|STX-DATA0-ETB-LRC<br>STX-DATAn-ETB-LRC<br>EOT|
|**IMPORTANTE:**|Cuando  se  utilizan  las  API  suministradas  por  The  Factory  HKA,  estas  se<br>encargan  de  enviar  de  forma  automática  el  ACK,  mientras  que  a  través  de<br>protocolo  directo  se  debe  enviar  el  ACK  a  la  impresora  para  poder  recibir  el<br>próximo bloque de información.||
|Tabla 11. Secuencia de comandos de lectura|||


## **11. COMANDOS PARA LA PROGRAMACIÓN DE LA IMPRESORA FISCAL**

La  impresora  fiscal  maneja  varios  parámetros  que  son  de  uso  importante  para  su funcionamiento,  los  cuales  deben  ser  programados.  Algunos  son  opcionales  y  otros obligatorios, en algunos casos estos parámetros tienen requisitos previos para su configuración.

Cuando  el  distribuidor  entrega  la  impresora  fiscal  al  cliente  final,  esta  última  ya  viene programada  con  ciertos  parámetros  para  su  funcionamiento,  los  cuales  son: **Tasas  de  Impuesto, Hora y Fecha, Medios de pago, Encabezado y Pie de Página.**

El  sistema  administrativo  puede  igualmente  programar  los  Medios  de  Pago  y  Cajeros.  Los medios  de  pago,  programación  del  visor  o  Display  y  los  cajeros  se  programan  de  acuerdo  a  las **REGISTRO DE CAJERO**

**The Factory HKA, C.A. VENEZUELA**

**==> picture [95 x 43] intentionally omitted <==**

**MANUAL DE PROTOCOLOS Y COMANDOS** Código: **MIA-CINT-01 V8.5.0** Versión N° **8.5.0** Fecha: **23/08/2022 INTEGRACIÓN** Página  21

Este  comando  permite  definir  la  información  relativa  a  un  cajero.  Es  necesaria  la  programación previa del cajero mediante este comando para ejecutar el comando Inicio de Cajero.

|**Descripción**<br>Registro de cajero<br>**Descripción**<br>Número de cajero (Dígitos: 01 - 30)<br>Indique un código secreto del cajero, Numérico: 5 dígitos 00000 - 99999<br>Indique la descripción o nombre del cajero (16 Caracteres máximos)|**Comandos**|
|---|---|
||**PC**|
||**Argumento**|
||**02**|
||**12345**|
||**Pedro**|


Tabla 12. Secuencia de comando de registro de cajero.

||**Inicio de trama**|**Comando**|**Argumento**|**Argumento**|**Argumento**|**Fin de Trama**|LRC|
|---|---|---|---|---|---|---|---|
|**ASCII**|STX|**PC**|**02**|**12345**|**Pedro**|ETX|XX|
|**HEX**|02|**DATA (HEX)**||||**03**|**LRC**|
|Tabla 13. Ejemplo de instrucción de programación de cajeros con protocolo directo.||||||||


## **11.1. INICIO Y FIN DE CAJERO**

Este  comando  permite  iniciar  y  finalizar  un  cajero  previamente  registrado.  Este  comando  es  de uso opcional.

|**Descripción**<br>Inicio de cajero<br>Fin del cajero<br>**Descripción**<br>Código secreto del cajero (Numérico; 5 dígitos: 00000 - 99999)|**Comandos**|
|---|---|
||**5**|
||**6**|
||**Argumento**|
||12345|


Tabla 14. Inicio y Fin de Cajero.

||**Inicio de trama**|**Comando**|**Argumento**|**Fin de Trama**|LRC|
|---|---|---|---|---|---|
|**ASCII**|STX|**5**|**12345**|ETX|XX|
|**HEX**|02|**DATA (HEX)**||**03**|**LRC**|
|Tabla 15. Ejemplo de instrucción de inicio de cajero con protocolo directo.||||||


**The Factory HKA, C.A. VENEZUELA**

||**MANUAL DE PROTOCOLOS Y COMANDOS**<br>**V8.5.0**|Código:**MIA-CINT-01**|
|---|---|---|
|||Versión N°**8.5.0**|
||**INTEGRACIÓN**|Fecha:**23/08/2022**|
|||Página  22|


## **11.2. MEDIOS DE PAGO**

Este  comando  permite  definir  los  descriptores  para  cada  medio  de  pago.  Su  uso  va  de  la  mano con  los  pagos  parciales  y  totales.  Las  impresoras  fiscales  manejan  16  o  24  medios  de  pagos, varía según el modelo.

|**Descripción**|**Comandos**|**Comandos**|
|---|---|---|
|Descriptor de medios de pagos|**PE**||
|ID|**01-24 (a)**<br>**01-16 (b)**||
|Nombre del medio de pago|14 Caracteres máximos||
|Medio de pago del**01 - 19**(Moneda Nacional),<br>Por defecto|**01-**Efectivo  1,**02**-Efectivo  2,**03**-Efectivo  3,**04**-Efectivo  4,**05**-Efectivo  5,<br>**06**-Efectivo  6,**07**-Cheque  1,**08**-Cheque  2,**09**-Cheque  3,**10**-Cheque  4,<br>**11**-Cheque  5,**12**-Cheque  6,**13**-Tarjeta  1,**14**-Tarjeta  1,**15**-Tarjeta  1,<br>**16**-Tarjeta 1,**17**-Tarjeta 1,**18**-Tarjeta 1,**19**-Ticket 1||
|Medio de pago del**20 - 24**(Moneda<br>Extranjera). Para totalizar con los siguientes<br>medios de pago se debe activar el**Flag 50 en**<br>**01 y utilizar el CMD 199**para cierre del<br>documento fscal|**20-**Divisa  1**, 21-**Divisa 2**, 22-**Divisa 3**, 23-**Divisa 4**, 24-**Divisa 5||
|**Importante**|Cuando se aplican uno o más pagos parciales y posteriormente<br>se procede anular el documento fscal en curso (enviando el<br>comando 7), el mismo no se anulará sino que continuará en<br>totalizar la información||
|Número del Medio de Pago (SRP-812, HKA-80, DT-230, PP9, P3100DL, ACLAS PP9-PLUS, TALLY1140)||**(a)**|
|Número del Medio de Pago (SRP-350, HKA112, HSP7000, TALLY 1125, KUBE)||**(b)**|


Tabla 16. Secuencia de comandos de Medios de pago.

||**Inicio de trama**|**Comando**|**Argumento**|**Fin de Trama**|LRC|
|---|---|---|---|---|---|
|**ASCII**|STX|**PE**|**12345**|ETX|XX|
|**HEX**|02|**DATA (HEX)**||**03**|**LRC**|
|Tabla 17. Ejemplo de instrucción de inicio de cajero con protocolo directo.||||||


## **11.3. PROGRAMACIÓN DE HORA Y FECHA**

Este  comando  permite  programar  la  hora  y  la  fecha  actual  de  la  impresora  fiscal.  Para  ello  debe realizar previamente un Reporte Z.

**The Factory HKA, C.A. VENEZUELA**

||**MANUAL DE PROTOCOLOS Y COMANDOS**<br>**V8.5.0**|Código:**MIA-CINT-01**|
|---|---|---|
|||Versión N°**8.5.0**|
||**INTEGRACIÓN**|Fecha:**23/08/2022**|
|||Página  23|


|**Descripción**|**Comandos**|
|---|---|
|Hora|**PF**|
|Fecha|**PG**|
|**Ejemplo**|**Hora**<br>**PF133055**<br>**Fecha**<br>**PG181091**|
|Hora (HH: 2 Caracteres Formato 24H) - Minuto (MM: 2 Caracteres) - Segundos (SS: 2 caracteres)||
|Día (DD: 2 Caracteres) - Mes (MM: 2 Caracteres) - Año (YY: 2 Caracteres)||


Tabla 18. Comando de programación de hora y fecha.

## **11.4. PROGRAMACIÓN Y REGISTRO DE TASAS DE IMPUESTO**

Este comando permite enviar el valor de las tasas de impuesto al equipo fiscal. Al utilizar este comando se debe enviar otro comando de confirmación para su grabado en la memoria fiscal.

Se debe configurar el IGTF en la impresora fiscal para su uso, el comando de programación será el siguiente:

|**Descripción**|**Comandos**|
|---|---|
|Programación (Tasa 1 - Tasa 2 - Tasa 3 - IGTF)|**Tasa 1 :   16%**<br>**Tasa 2 :   8 %**<br>**Tasa 3 :    31%**<br>**Tasa 4 :   0%**<br>**IGTF   :    3%**|
|Registro|**Pt**|
|**Ejemplo Programación de tasas**|**PT11600108001310010300**|
|||
|Tipo 1: Tasa Excluida (Precio + ítem = Base imponible)<br>Tipo 2: Tasa Incluida (Precio + ítem = Base imponible + IVA)||
|El valor consta ( 4 dígitos: 2 Enteros + 2 Decimales)||
|**IMPORTANTE:**|**Tasa 3**: programada en 0 es considerada como percibido para las<br>impresoras SRP350, HSP7000, KUBE, HKA112, TD1125.<br>**Tasa 4:**solo es aceptada para las impresoras SRP812, DT230,<br>HKA80, PP9, ACLAS PP9-PLUS, PD3100DL, TD1140.|


Tabla 19. Tipo de impuesto y dígitos.

**The Factory HKA, C.A. VENEZUELA**

||**MANUAL DE PROTOCOLOS Y COMANDOS**<br>**V8.5.0**|Código:**MIA-CINT-01**|
|---|---|---|
|||Versión N°**8.5.0**|
||**INTEGRACIÓN**|Fecha:**23/08/2022**|
|||Página  24|


## **11.5. ENCABEZADO Y PIE DE PÁGINA**

Este comando permite definir los mensajes que se muestran en el encabezado y pie de página de los documentos. Para ello debe realizar previamente un Reporte Z.

|**Descripción**|**Descripción**|**Comandos**|
|---|---|---|
|Encabezado y Pie de Página||**PH**|
|**Ejemplo:**||**PH01Hola**|
|Número de línea del encabezado: 2 Caracteres (01-08)|||
|Número de línea del pie de página: 2 Caracteres (91-98)|||
|**IMPORTANTE:**|-No  debe  confundirse  la  “Programación  de  encabezado  y  pie  de  página”<br>con  los  “Datos  adicionales  del  cliente  en  encabezado  y  pie  de  página”.  La<br>programación  de  encabezado  y  pie  de  página  es  estática,  mientras  que  los<br>datos  adicionales  del  cliente  son  dinámicos  y  deben  enviarse  por  cada<br>documento emitido.<br>-En  el  equipo  Dascom**Tally  1125**,  la  cantidad  de  caracteres  que  se<br>muestran  para  el  encabezado  y  el  pie  de  página  puede  variar  dependiendo<br>de la confguración del formato de página.||


Tabla 20. Comando de definir encabezado y pie de página.

## **11.6. BANDERAS DE PROGRAMACIÓN (FLAGS)**

Este comando **(PJ)** permite definir el valor de las opciones de configuración utilizadas por el equipo.

|**Descripción**|**Comandos**|
|---|---|
|Banderas (FLAGS)|**PJ**|
|**Ejemplo**|**PJ5001**|
|Tipo de Bandera (2 Dígitos)||
|Valor de Bandera (2 Dígitos)||
|**IMPORTANTE:**|Descargar  la  lista  de  fag  de  cada  equipo  del<br>portal  Web,  ya  que  la  cantidad  de  fags  y<br>función  de  estos  varía  dependiendo  del<br>modelo de impresora fscal.|


Tabla 21. Comando para configuración de banderas.

**The Factory HKA, C.A. VENEZUELA**

**MANUAL DE PROTOCOLOS Y COMANDOS V8.5.0**

**INTEGRACIÓN**

**==> picture [95 x 43] intentionally omitted <==**

Código: **MIA-CINT-01** Versión N° **8.5.0** Fecha: **23/08/2022** Página  25

## **11.7. CONFIGURACIÓN DEL (FLAG 21)**

|**Flag 21**|||||
|---|---|---|---|---|
|**Montos Máximos permitidos con Flag 21 en Comandos Generales y Tradicionales**|||||
|**Información:**Al activar el**Flag (63= 01, 02, 03)**es posible hacer uso y extracción<br>de las tramas ampliadas.|||**Información:**Dependiente del valor (fag 21) que<br>este  activo se enviará la cantidad de dígitos que se<br>le presenta a continuación**(pago parcial**)||
|**REGISTRO DE PRODUCTO**|**FLAG 21**|**DÍGITOS**|**PAGO PARCIAL**|**IMPRESORAS**|
|**Precio Unitario del Ítem**|||||
|Precio del ítem<br>(8 enteros + 2 decimales)|00|**0000000100**|**2010000000100**|**KUBE* **<br>**TD1125* **<br>**SRP350****<br>**HKA112****<br>**SRP812**<br>**DT230**<br>**HKA80**<br>**PD3100**<br>**PP9**<br>**ACLAS PP9 PLUS**<br>**HSP7000**<br>**TD1140**|
|Precio del ítem<br>(7 enteros + 3 decimales)|01|**0000001000**|**2010000001000**||
|Precio del ítem<br>(6 enteros + 4 decimales)|02|**0000010000**|**2010000010000**||
|Precio del ítem<br>(9 enteros + 1 decimales)|11|**0000000010**|**2010000000010**||
|Precio del ítem<br>(10 enteros + 0 decimales)|12|**0000000001**|**2010000000001**||
|Precio del ítem<br>(14 enteros + 2 decimales)|30|**0000000000000100**|**2010000000000000100**||
|**Atención (*)**<br>Precio del ítem<br>(0000 +10 enteros + 2 decimales)<br>14 enteros + 2 decimales|30|**0000999999999999**|**20199999999999999000**|**KUBE* **<br>**TD1125* **|
|**Atención (**)**<br>No admiten el fag 21=30|30|No admiten|No admiten|**SRP350****<br>**HKA112****|
|**Cantidad de Ítem**|**FLAG 21**|**DÍGITOS**||**IMPRESORAS**|
|Cantidad del ítem<br>(5 enteros + 3 decimales)|00,01,02,<br>11,12|**00001000**||**KUBE**<br>**TD1125**<br>**SRP350**<br>**HKA112**<br>**T230**<br>**HSRP812**<br>**DKA80**<br>**PD3100**<br>**PP9**<br>**ACLAS PP9 PLUS**<br>**HSP7000**<br>**TD1140**|
|Cantidad del ítem<br>(14 enteros + 3 decimales)|30|**00000000000001000**|||
|**Montos Máximos permitidos con Flag 21 en Comandos Generales y Tradicionales**|||||
|**Información:**Al activar el**Flag (63= 01, 02, 03)**es posible hacer uso y extracción<br>de las tramas ampliadas.|||**Información:**Dependiente del valor (fag 21) que<br>este  activo se enviará la cantidad de dígitos que se<br>le presenta a continuación**(pago parcial**)||
|**REGISTRO DE PRODUCTO**|**FLAG 21**|**DÍGITOS**|**PAGO PARCIAL**|**IMPRESORAS**|
|**Precio Unitario del Ítem**|||||
|Precio del ítem<br>(8 enteros + 2 decimales)|00|**0000000100**|**2010000000100**|**KUBE* **<br>**TD1125* **<br>**SRP350****<br>**HKA112****<br>**SRP812**<br>**DT230**<br>**HKA80**<br>**PD3100**<br>**PP9**<br>**ACLAS PP9 PLUS**<br>**HSP7000**<br>**TD1140**|
|Precio del ítem<br>(7 enteros + 3 decimales)|01|**0000001000**|**2010000001000**||
|Precio del ítem<br>(6 enteros + 4 decimales)|02|**0000010000**|**2010000010000**||
|Precio del ítem<br>(9 enteros + 1 decimales)|11|**0000000010**|**2010000000010**||
|Precio del ítem<br>(10 enteros + 0 decimales)|12|**0000000001**|**2010000000001**||
|Precio del ítem<br>(14 enteros + 2 decimales)|30|**0000000000000100**|**2010000000000000100**||
|**Atención (*)**<br>Precio del ítem<br>(0000 +10 enteros + 2 decimales)<br>14 enteros + 2 decimales|30|**0000999999999999**|**20199999999999999000**|**KUBE* **<br>**TD1125* **|
|**Atención (**)**<br>No admiten el fag 21=30|30|No admiten|No admiten|**SRP350****<br>**HKA112****|
|**Cantidad de Ítem**|**FLAG 21**|**DÍGITOS**||**IMPRESORAS**|
|Cantidad del ítem<br>(5 enteros + 3 decimales)|00,01,02,<br>11,12|**00001000**||**KUBE**<br>**TD1125**<br>**SRP350**<br>**HKA112**<br>**T230**<br>**HSRP812**<br>**DKA80**<br>**PD3100**<br>**PP9**<br>**ACLAS PP9 PLUS**<br>**HSP7000**<br>**TD1140**|
|Cantidad del ítem<br>(14 enteros + 3 decimales)|30|**00000000000001000**|||


**The Factory HKA, C.A. VENEZUELA**

**==> picture [95 x 43] intentionally omitted <==**

Código: **MIA-CINT-01 V8.5.0** Versión N° **8.5.0** Fecha: **23/08/2022 INTEGRACIÓN** Página  26

## **MANUAL DE PROTOCOLOS Y COMANDOS V8.5.0**

|**Atención (*)**<br>Max :2.147.483,647<br>Cantidad del ítem<br>(0000000 + 7 enteros + 3 decimales)<br>14 enteros + 3 decimales|30||**00000002147483647**|**KUBE* **<br>**TD1125* **|
|---|---|---|---|---|
|**Atención (**)**<br>No admiten el fag 21=30|30||No admiten|**SRP350****<br>**HKA112****|
|**Ejemplo de trama**|||**Orden de la trama**<br>**cmd**<br>**Precio**<br>**Cantidad**<br>**Descripción**<br>**!**<br>**0000000100**<br>**00001000**<br>**producto**||
||||||
|**DESCUENTO Y RECARGO POR**<br>**MONTO**|**FLAG 21**||**DÍGITOS**||
|El monto consta<br>(7 enteros + 2 decimales)|00||**000000100**|**KUBE* **<br>**TD1125* **<br>**SRP350****<br>**HKA112****<br>**SRP812**<br>**DT230**<br>**HKA80**<br>**PD3100D**<br>**PP9**<br>**ACLAS PP9 PLUS**<br>**HSP7000**<br>**TD1140**|
|El monto consta<br>(7 enteros + 2 decimales)|01||**000000100**||
|El monto consta<br>(7 enteros + 2 decimales)|02||**000000100**||
|El monto consta<br>(8 enteros + 1 decimales)|11||**000000010**||
|El monto consta<br>(9 enteros + 0 decimales)|12||**000000001**||
|El monto consta<br>(15 enteros + 2 decimales)|30||**00000000000000100**||
|**ANULACIÓN DE UN ÍTEM**|||||
|Precio del ítem<br>(8 enteros + 2 decimales)|00|**0000000100**||**KUBE* **<br>**TD1125* **<br>**SRP350****<br>**HKA112****<br>**SRP812**<br>**DT230**<br>**HKA80**<br>**PD3100**<br>**PP9**<br>**ACLAS PP9 PLUS**<br>**HSP7000**<br>**TD1140**|
|Precio del ítem<br>(7 enteros + 3 decimales)|01|**0000001000**|||
|Precio del ítem<br>(6 enteros + 4 decimales)|02|**0000010000**|||
|Precio del ítem<br>(9 enteros + 1 decimales)|11|**0000000010**|||
|Precio del ítem<br>(10 enteros + 0 decimales)|12|**0000000001**|||
|Precio del ítem<br>(14 enteros + 2 decimales)|30|**0000000000000100**|||


Tabla 22. Configuración del Flag 21

**The Factory HKA, C.A. VENEZUELA**

||**MANUAL DE PROTOCOLOS Y COMANDOS**<br>**V8.5.0**|Código:**MIA-CINT-01**|
|---|---|---|
|||Versión N°**8.5.0**|
||**INTEGRACIÓN**|Fecha:**23/08/2022**|
|||Página  27|


## **11.8. MANEJO DEL VISOR O DISPLAY DE PRECIOS DEL CLIENTE**

Estructura de los comandos de programación del visor o display.

|**Descripción**|**Comandos**|
|---|---|
|Mostrar hora y fecha|**a**|
|Programación de mensaje comercial en el visor|**PI**|
|Mostrar mensaje comercial|**b**|
|Programar  mensajes  temporales  en  el  visor  o<br>display|**cU**|
|Indicador de Mensaje comercial en el Display (50 Caracteres máximos)||
|Línea superior del visor: U<br>Línea inferior del visor: L<br>(20 Caracteres máximos)||
|**Ejemplo**|**PIBIENVENIDO**<br>**cUBIENVENIDO**|
|**IMPORTANTE**:|En  los  equipos  Aclas  PP9  no  se  pueden<br>programar<br>mensajes<br>comerciales<br>ni<br>temporales,  el  visor  que  tienen  incorporado<br>no es LCD sino de segmentos.|


Tabla 23. Manejo de visor o display.

## **11.9. APERTURA DE GAVETA Y RETIRO/FONDO DE CAJA**

|**Descripción**|**Comandos**|
|---|---|
|Apertura de gaveta de dinero|**0**|
|Apertura  de  gaveta  en  medio  de  una<br>transacción fscal|**w**|
|Comando de inicio para retiro y fondo|**9**|
|Retiro de efectivo|**0**|
|Fondos de caja|**1**|
|Fin de retiro y fondo de caja|**t**|
|Medio de pago: 01-24|**2 caracteres**|
|Monto|**10 enteros y 2 decimales**|


**The Factory HKA, C.A. VENEZUELA**

**==> picture [95 x 43] intentionally omitted <==**

**MANUAL DE PROTOCOLOS Y COMANDOS** Código: **MIA-CINT-01 V8.5.0** Versión N° **8.5.0** Fecha: **23/08/2022 INTEGRACIÓN** Página  28

|**Descripción**|**Comandos**|
|---|---|
|**Ejemplos:**|**9012000000000200**|
|**IMPORTANTE:**|Debe  haber  al  menos  1  producto  registrado,<br>el  comando**w**solo  abre  la  gaveta  de  dinero<br>en  medio  de  una  transacción,  activando  el<br>Flag  24  en  01  (ver  lista  de  fags  del  equipo),<br>mientras  que  el  comando**0**abre  la  gaveta  en<br>cualquier  momento  con  el  Flag  24  en  00  (ver<br>lista de fags del equipo).|


Tabla 24. Secuencia de comandos para emisión de Documentos No Fiscales.

## **11.10. IMPRIMIR PROGRAMACIÓN**

|**Descripción**|**Comandos**|
|---|---|
|Programación de la impresora|**D**|
|Éste comando imprime los valores almacenados para los siguientes parámetros:<br>●<br>Tasas de impuesto.<br>●<br>Nombre de cajero activo (luego de programarlo e iniciarlo).<br>●<br>Nombre de medios de pago programados.<br>●<br>Banderas (FLAGS) del sistema y sus valores programados.<br>●<br>Versión de Firmware de la impresora fscal.<br>●<br>Mensajes del Módulo de Comunicación||


Tabla 25. Secuencia de comandos para emisión de Documentos No Fiscal (Programación).

**The Factory HKA, C.A. VENEZUELA**

**==> picture [95 x 43] intentionally omitted <==**

**MANUAL DE PROTOCOLOS Y COMANDOS** Código: **MIA-CINT-01 V8.5.0** Versión N° **8.5.0** Fecha: **23/08/2022 INTEGRACIÓN** Página  29

## **12. CÓDIGO DE BARRAS**

Este  comando  permite  imprimir  un  código  de  barra  como  referencia  de  un  producto  dentro  de  la factura, nota de crédito, nota de débito o en el pie de la factura

||**1D (unidimensionales)**|**1D (unidimensionales)**|**1D (unidimensionales)**|**1D (unidimensionales)**|**Bidimensionales (2D)**|**Bidimensionales (2D)**|
|---|---|---|---|---|---|---|
|**Formato**|||||||
|**Modelo de**<br>**Impresora**|**EAN13**|**ITF**|**CODE128**|**CODE39**|**QR**|**PDF**|
|**Comandos**|||||||
|**Y**|**Codigo de Barra en el producto**||||||
|**y**|**Codigo de Barra en el Pie de Ticket**||||||
|**PJ3000**|**Imprime el Codigo de Barra y no el número asociado**||||||
|**PJ3001**|**Imprime el Codigo de Barra y el número asociado**||||||
|**PJ43**|**PJ4300**|**PJ4301**|**PJ4302**|**PJ4303**|**PJ4304**|**PJ4305**|
|**Descripción de Caracteres**|||||||
|**SRP-812**|12 Dígitos fjos|12 Dígitos fjos|32 Caracteres<br>Maximos|32 Caracteres<br>Maximos|120 Caracteres<br>Maximos|120 Caracteres<br>Maximos|
|**HKA-80**|12 Dígitos fjos|12 Dígitos fjos|23 Caracteres<br>Maximos|20 Caracteres<br>Maximos|120 Caracteres<br>Maximos|120 Caracteres<br>Maximos|
|**DT-230**|12 Dígitos fjos|32 Dígitos Máximos|32 Caracteres<br>Maximos|32 Caracteres<br>Maximos|122 Caracteres<br>Maximos|122 Caracteres<br>Maximos|
|**PP9**|12 Dígitos fjos|38 Caracteres<br>Maximos|44 Caracteres<br>Maximos|12 Dígitos fjos|122 Caracteres<br>Maximos|N/A|
|**ACLAS PP9**<br>**PLUS**|12 Caracteres<br>Maximos|32 Dígitos Máximos|32 Caracteres<br>Maximos|32 Caracteres<br>Maximos|122 Caracteres<br>Maximos|122 Caracteres<br>Maximos|
|**P3100DL**|12 Dígitos fjos|13 Dígitos fjos|32 Caracteres<br>Maximos|32 Caracteres<br>Maximos|120 Caracteres<br>Maximos|120 Caracteres<br>Maximos|


**The Factory HKA, C.A. VENEZUELA**

**==> picture [95 x 43] intentionally omitted <==**

## **MANUAL DE PROTOCOLOS Y COMANDOS V8.5.0**

**==> picture [57 x 9] intentionally omitted <==**

**----- Start of picture text -----**<br>
||
|---|
|INTEGRACIÓN|

**----- End of picture text -----**<br>


Código: **MIA-CINT-01** Versión N° **8.5.0** Fecha: **23/08/2022** Página  30

|**SRP-350**|12 Dígitos fjos|31 Caracteres<br>Maximos|32 Caracteres<br>Maximos|N/A|N/A|N/A|
|---|---|---|---|---|---|---|
|**HKA-112**|12 Dígitos fjos|20 Caracteres<br>Maximos|20 Caracteres<br>Maximos|20 Caracteres<br>Maximos|120 Caracteres<br>Maximos|N/A|
|**HSP7000**|12 Dígitos fjos|20 Caracteres<br>Maximos|20 Caracteres<br>Maximos|20 Caracteres<br>Maximos|N/A|N/A|
|**TALLY 1125**|12 Dígitos fjos|32 Dígitos fjos|32 Caracteres<br>Maximos|32 Caracteres<br>Maximos|N/A|N/A|
|**TALLY 1140**|12 Caracteres<br>Maximos|32 Dígitos Máximos|25 Caracteres<br>Maximos|11 Caracteres<br>Maximos|N/A|N/A|
|**KUBE**|12 Dígitos fjos|20 Caracteres<br>Maximos|20 Caracteres<br>Maximos|N/A|N/A|N/A|
|**SRP-280**|N/A|N/A|N/A|N/A|N/A|N/A|
||||||||


Tabla 26. Comandos para códigos de barras.

## **13. TABLA DE CARACTERES**

|**Modelo de Impresora**|**Encabezados**<br>**X (Y)**|**Pie de Página**<br>**X (Y)**|**RIF/C.I. X**|**Razón**<br>**Social X**|**Información**<br>**Adicional**<br>**X (Y)**|**Comentario**<br>**X**|**Descripción**<br>**Producto**<br>**X**|
|---|---|---|---|---|---|---|---|
|**SRP-812**|40 Caracteres<br>(8 líneas)|40 Caracteres<br>(8 líneas)|40<br>Caracteres|40<br>Caracteres|ENC (40)<br>Caracteres<br>PIE (40)<br>(10 líneas)|40<br>Caracteres|127<br>Caracteres|
|**HKA-80**|40 Caracteres<br>(8 líneas)|40 Caracteres<br>(8 líneas)|40<br>Caracteres|40<br>Caracteres|ENC (40)<br>Caracteres<br>PIE (40)<br>(10 líneas)|40<br>Caracteres|127<br>Caracteres|
|**DT-230**|40 Caracteres<br>(8 líneas)|40 Caracteres<br>(8 líneas)|40<br>Caracteres|40<br>Caracteres|ENC (40)<br>Caracteres<br>PIE (40)<br>(10 líneas)|40<br>Caracteres|127<br>Caracteres|
|**PP9**|40 Caracteres<br>(8 líneas)|40 Caracteres<br>(8 líneas)|38<br>Caracteres|34<br>Caracteres|ENC (40)<br>Caracteres<br>PIE (40)<br>(10 líneas)|40<br>Caracteres|120<br>Caracteres|
|**PP9 PLUS**|40 Caracteres<br>(8 líneas)|40 Caracteres<br>(8 líneas)|38<br>Caracteres|34<br>Caracteres|ENC (40)<br>Caracteres<br>PIE (40)<br>(10 líneas)|40<br>Caracteres|120<br>Caracteres|
|**P3100DL (VERTICAL 80)**|38 Caracteres<br>(6 líneas)|38 (variable)|24<br>Caracteres|20<br>Caracteres|ENC (33)<br>Caracteres<br>PIE (38)<br>Caracteres|27<br>Caracteres|127<br>Caracteres|
|**P3100DL (VERTICAL 136)**|40 Caracteres<br>(6 líneas)|40 (variable)|40<br>Caracteres|40<br>Caracteres|ENC (40)<br>Caracteres<br>PIE (40)<br>Caracteres|40<br>Caracteres|127<br>Caracteres|
|**P3100DL (VERTICAL 187)**|40 Caracteres<br>(6 líneas)|40 (variable)|40<br>Caracteres|40<br>Caracteres|ENC (40)<br>Caracteres<br>PIE (40)<br>Caracteres|40<br>Caracteres|127<br>Caracteres|


**The Factory HKA, C.A. VENEZUELA**

||**MANUAL DE PROTOCOLOS Y COMANDOS**<br>**V8.5.0**|Código:**MIA-CINT-01**|
|---|---|---|
|||Versión N°**8.5.0**|
||**INTEGRACIÓN**|Fecha:**23/08/2022**|
|||Página  31|


|**SRP-350**|40 Caracteres<br>(8 líneas)|40 Caracteres<br>(8 líneas)|47<br>Caracteres|43<br>Caracteres|ENC (56)<br>Caracteres<br>PIE (56)<br>(10 líneas)|40<br>Caracteres|37<br>Caracteres|
|---|---|---|---|---|---|---|---|
|**HKA-112**|40 Caracteres<br>(8 líneas)|40 Caracteres<br>(8 líneas)|40<br>Caracteres|40<br>Caracteres|40<br>Caracteres<br>(10 líneas)|40|116|
|**HSP7000**|40 Caracteres<br>(8 líneas)|40 Caracteres<br>(8 líneas)|47<br>Caracteres|43<br>Caracteres|50<br>Caracteres<br>(10 líneas)|40|120|
|**TALLY 1125 (½ CARTA - 80)**|38 Caracteres<br>(3 líneas)|38 (variable)|29|38<br>Caracteres|ENC (38)<br>Caracteres<br>PIE (38)<br>Caracteres|39|118|
|**TALLY 1125 (½ CARTA -**<br>**136)**|40 Caracteres<br>(2 líneas)|40 (variable)|40<br>Caracteres|40<br>Caracteres|ENC (40)<br>Caracteres<br>PIE (40)<br>Caracteres|60|118|
|**TALLY 1125 (CARTA - 80)**|38 Caracteres<br>(6 líneas)|38 (variable)|29<br>Caracteres|38<br>Caracteres|ENC (38)<br>Caracteres<br>PIE (38)<br>Caracteres|39|118|
|**TALLY 1125 (CARTA - 136)**|40 Caracteres<br>(6 líneas)|40 (variable)|40<br>Caracteres|40<br>Caracteres|ENC (40)<br>Caracteres<br>PIE (40)<br>Caracteres|60|118|
|**TALLY 1140 (½ CARTA -**<br>**136)**|40 Caracteres<br>(8 líneas)|40 Caracteres<br>(8 líneas)|40<br>Caracteres|40<br>Caracteres|ENC (40)<br>Caracteres<br>PIE (40)<br>Caracteres|40|140|
|**TALLY 1140 (CARTA - 136)**|40 Caracteres<br>(8 líneas)|40 Caracteres<br>(8 líneas)|40<br>Caracteres|40<br>Caracteres|ENC (40)<br>Caracteres<br>PIE (40)<br>Caracteres|40|140|
|**SRP-280**|40 Caracteres<br>(8 líneas)|40 Caracteres<br>(8 líneas)|33<br>Caracteres|40<br>Caracteres|40 (10<br>líneas)|40|120|
|**KUBE**|40 Caracteres<br>(8 líneas)|40 Caracteres<br>(8 líneas)|47<br>Caracteres|43<br>Caracteres|56 (10<br>líneas)|40|120|
|**Longitud Total**||||||||
|||||||||
|**X:**Representa la cantidad de caracteres por línea que muestra la impresora para el comando o campo específco.<br>**Y:**Representa el número de líneas que soporta la impresora para el comando o campo específco.||||||||


Tabla 27. Tabla de caracteres

**The Factory HKA, C.A. VENEZUELA**

||**MANUAL DE PROTOCOLOS Y COMANDOS**<br>**V8.5.0**|Código:**MIA-CINT-01**|
|---|---|---|
|||Versión N°**8.5.0**|
||**INTEGRACIÓN**|Fecha:**23/08/2022**|
|||Página  32|


## **14. COMANDOS PARA GENERAR DOCUMENTOS FISCALES**

## **14.1. COMANDOS PARA EL REGISTRO DE UN ÍTEM EN UNA FACTURA**

|**Descripción**|**Descripción**|**Comando**|
|---|---|---|
|DESCRIPCIÓN|**HEX**|**ASCII**|
|Ítem Exento|(0x20)|**carácter espacio**|
|Ítem Tasa 1  (General)|(0x21)|**!**|
|Ítem Tasa 2  (Reducida)|(0x22)|**“**|
|Ítem Tasa 3 (Adicional)|(0x23)|**#**|
|Ítem Tasa 4 (Percibido)|(0x24)|**$**|
|**Ejemplo de Trama**|**CMD**<br>**PRECIO**<br>**CANTIDAD**<br>**CODIGO**<br>**DESCRIPCIÓN**<br>**!**<br>**0000001000**<br>**00010000**<br>**8523**<br>**Producto**||
|**Anulación de ítem**|||
|Anulación de Exento|(0xA0)|**(0xA0)**|
|Anulación de Tasa 1<br>(General)|(0xA1)|**¡**|
|Anulación de Tasa 2<br>(Reducida)|(0xA2)|**¢**|
|Anulación de Tasa 3<br>(Adicional)|(0xA3)|**£**|
|Anulación de Tasa 4<br>(Percibido)|(0xA4)|**¤**|
|**Importante**|**Tasa 3 (Adicional):**programada en 0 es considerada como<br>percibido para las impresoras**SRP350, SRP280, HSP7000,**<br>**KUBE, HKA112, TD1125.**||
||**Tasa 4 (Percibido):**sólo es aceptada para las impresoras<br>**SRP812, DT230, HKA80, PP9,  PP9-PLUS, PD3100DL,**<br>**TD1140.**||


Tabla 28. Comandos de Factura

**The Factory HKA, C.A. VENEZUELA**

||**MANUAL DE PROTOCOLOS Y COMANDOS**<br>**V8.5.0**|Código:**MIA-CINT-01**|
|---|---|---|
|||Versión N°**8.5.0**|
||**INTEGRACIÓN**|Fecha:**23/08/2022**|
|||Página  33|


## **14.2. EJEMPLO PARA GENERAR UNA FACTURA**

Esquema  general  para  realizar  una  factura,  el  cual  incluye  todas  las  operaciones  posibles  para este documento.

|**Descripción**|**Comandos**|**Ejemplo de una Factura impresa**|
|---|---|---|
|||SENIAT|
|||RIF J-312171197|
|Encabezado|**PH01Encabezado 1**|ENCABEZADO 1|
||||
|Encabezado|**PH08 Encabezado 8**|ENCABEZADO 8|
|RIF/C.I.|**iR*J-123456789**|RIF/C.I.: J-123456789|
|Razón Social|**iS*The Factory HKA**|Razón Social: The Factory HKA|
|Líneas Adicionales|**i01Línea Adicional 01**|Línea Adicional 01|
||||
|Líneas Adicionales|**i09Línea Adicional 09**|Línea Adicional 09|
|||FACTURA|
|Doc. Fiscal y Número de Factura||FACTURA:<br>00001325|
|Fecha del DF y de Hora del DF||FECHA: 16-08-2016<br>HORA: 14:42|
|---------------------------------------------------------------|-----------------------------------------------------------------------|**--------------------------------------------------------**|
|Comentario en el cuerpo del Documento|**@Esto es un Comentario**||Esto es un Comentario||
|Tasa Exento|**000000100000001000Producto Exento**|Producto Exento (E)                                      Bs 10,00|
|Descuento por Porcentaje|**p-1000**|DESC (10,00%)                                                Bs - 1,00|
|Tasa General|**!000000200000001000Producto General**|Producto General (G)                                    Bs 20,00|
|Recargo por Porcentaje|**p+1000**|RECAR (10,00%)                                               Bs 2,00|
|Tasa Reducida|**“000000300000001000Producto Reducida**|Producto Reducida (R)                                  Bs 30,00|
|Descuento por Monto|**q-000001000**|DESC<br>Bs - 10,00|
|Tasa Adicional|**#000000400000001000Producto Adicional**|Producto Adicional (A)                                  Bs 40,00|
|Recargo por Monto|**q+000001000**|RECAR                                                            Bs 10,00|
|Tasa Exento|**000000100000001000Producto Exento**|Producto Exento (E)                                      Bs 10,00|
|Corrección|**k**|CORRECCIÓN|
|Cancela último ítem/descuento/recargo||Producto Exento (E)                                   Bs - 10,00|
|Tasa Adicional|**#000000400000001000Producto Adicional**|Producto Adicional (A)                                Bs 40,00|
|||ANULACIÓN|
|Anula producto Tasa (A)|**£000000400000001000Producto Adicional**|Producto Adicional (A)                               Bs - 40,00|
|Tasa Percibido|**$000000500000001000Producto Percibido**|Producto Percibido (P)                                 Bs 50,00|
|Código de barra para un producto|**Y1234567890128**||


**The Factory HKA, C.A. VENEZUELA**

**==> picture [95 x 43] intentionally omitted <==**

## **MANUAL DE PROTOCOLOS Y COMANDOS V8.5.0 INTEGRACIÓN**

Código: **MIA-CINT-01** Versión N° **8.5.0** Fecha: **23/08/2022** Página  34

|-------------------------------|----------------------------------------------------------|**---------------------------------------------------------**|
|---|---|---|
|Subtotal|**3**|SUBTTL                                                         Bs 151,00|
|||**---------------------------------------------------------**|
|Tasas de Impuesto utilizadas en el<br>cuerpo de la factura||EXENTO         Bs 9,00       PERCIBIDO<br>Bs 50,00|
|||BI G16,00%    Bs 22,00     IVA G16,00%<br>Bs 3,52|
|||BI R8,00%      Bs 20,00      IVA R8,00%<br>Bs 1,60|
|||BI A31,00%    Bs 50,00<br>IVA A31,00%<br>Bs 15,50|
|------------------------------------------------------------|**--------------------------------------------------**|**---------------------------------------------------------**|
|Subtotal de la Factura||SUBTTL          Bs 151,00   IVA                       Bs 20,62|
|**-------------------------------------------**|**--------------------------------------------------**|**---------------------------------------------------------**|
|Pago Parcial (Efectivo 1)|**201000000002062**|EFECTIVO 1<br>Bs 20,62|
|Pago Parcial (Cheque 5)|**211000000005100**|CHEQUE 5<br>Bs 51,00|
|Pago Directo(Divisa 3)|**122**|DIVISA 3                                                        Bs 103,00|
|**--------------------------------------------**|**--------------------------------------------------**|**---------------------------------------------------------**|
|||BI IGTF3,00% Bs 100,00    IGTF3,00%<br>Bs 3,00|
|Cierre de la Factura|**199**|**TOTAL**<br>**Bs 174,62**|
|Líneas Adicionales|**i01 Línea Adicional 01**|Línea Adicional 01|
||||
|Líneas Adicionales|**i09 Línea Adicional 09**|Línea Adicional 09|
|Pie de Ticket|**PH91Pie de Ticket 01**|Pie de Ticket 01|
||||
|Pie de Ticket|**PH98Pie de Ticket 01**|Pie de Ticket 08|
|Código de barra de Pie de Ticket|**y1234567890128**||
|||_MH_<br>Z1F9999988|
|**IMPORTANTE:**|**Para generar esta Factura se activaron los siguientes Flags.**<br>**2100**<br>Se mantiene la confguración estándar de los montos que maneja la impresora.(Ver.<br>Tabla 21<br>**5001**<br>Se activa para realizar cálculo del IGTF aplicando pagos en moneda extranjera<br>**3001**<br>Imprime el código de barra con el número asociado bajo él código<br>**4300**<br>Se activa el codigo de barra**EAN13**<br>**199**<br>Comando que es de uso obligatorio para cerrar los documentos fscales ( Factura de venta,<br>Nota de Crédito, Nota de Débito) cuando el fag**50**está en**01.**||


Tabla 29. Ejemplo de comandos para emisión de facturas.

**The Factory HKA, C.A. VENEZUELA**

||**MANUAL DE PROTOCOLOS Y COMANDOS**<br>**V8.5.0**|Código:**MIA-CINT-01**|
|---|---|---|
|||Versión N°**8.5.0**|
||**INTEGRACIÓN**|Fecha:**23/08/2022**|
|||Página  35|


## **14.3. COMANDOS PARA GENERAR UNA NOTA DE CRÉDITO (DEVOLUCIÓN)**

|**Descripción**|||**Comando**|
|---|---|---|---|
|Ítem Exento|||**d0**|
|Ítem Tasa 1  (General)|||**d1**|
|Ítem Tasa 2  (Reducida)|||**d2**|
|Ítem Tasa 3 (Adicional)|||**d3**|
|Ítem Tasa 4 (Percibido)|||**d4**|
|**Ejemplo de Trama**||**CMD**<br>**PRECIO**<br>**CANTIDAD**<br>**CODIGO**<br>**DESCRIPCIÓN**<br>**d1**<br>**0000001000**<br>**00010000**<br>**8523**<br>**Producto**||
|**Anulación de ítem**||||
|Anulación de Exento||(ä = 0xE4)|**ä0**|
|Anulación de Tasa 1  (General)||(ä = 0xE4)|**ä1**|
|Anulación de Tasa 2  (Reducida)||(ä = 0xE4)|**ä2**|
|Anulación de Tasa 3 (Adicional)||(ä = 0xE4)|**ä3**|
|Anulación de Tasa 4 (Percibido)||(ä = 0xE4)|**ä4**|
|**Importante**|**Tasa 3 (Adicional):**programada en 0 es considerada<br>cómo percibido para las impresoras**SRP350,**<br>**SRP280, HSP7000, KUBE, HKA112, TD1125.**|||
||**Tasa 4 (Percibido):**sólo es aceptada para las<br>impresoras**SRP812, DT230, HKA80, PP9, PP9-PLUS,**<br>**PD3100DL, TD1140.**|||


Tabla 30. Comandos para Nota de Crédito

**The Factory HKA, C.A. VENEZUELA**

||**MANUAL DE PROTOCOLOS Y COMANDOS**<br>**V8.5.0**|Código:**MIA-CINT-01**|
|---|---|---|
|||Versión N°**8.5.0**|
||**INTEGRACIÓN**|Fecha:**23/08/2022**|
|||Página  36|


## **14.4. EJEMPLO PARA GENERAR UNA NOTA DE CRÉDITO (DEVOLUCIÓN)**

Esquema  general  para  realizar  una  Nota  de  Crédito,  la  cual  incluye  todas  las  operaciones posibles para este documento.

|**Descripción**|**Comandos**|**Ejemplo de una Nota de Credito Impresa**|
|---|---|---|
|||SENIAT|
|||RIF J-312171197|
|Encabezado|**PH01Encabezado 1**|ENCABEZADO 1|
||||
|Encabezado|**PH08 Encabezado**8|ENCABEZADO 8|
|Número de Factura Afectada|**(OBLIGATORIO)**<br>**iF*01020000001**|#FAC: 01020000001|
|Fecha de Factura Afectada|**(OBLIGATORIO)**<br>**iD*23/06/2022**|FECHA FAC: 23/06/2022|
|Número de Registro|**(OBLIGATORIO)**<br>**iI*Z1F1234567**|#CONTROL/SERIAL IF: Z1F1234567|
|RIF/C.I.|**(OBLIGATORIO)**<br>**iR*J-123456789**|RIF/C.I.: J-123456789|
|Razón Social|**(OBLIGATORIO) iS*The Factory HKA**|RAZON SOCIAL: The Factory HKA|
|Líneas Adicionales|**i01Línea Adicional 01**|Línea Adicional 01|
||||
|Líneas Adicionales|**i09Línea Adicional 09**|Línea Adicional 09|
|||NOTA DE CRÉDITO|
|Doc. Fiscal y Número de Nota de Débito||NOTA DE CRÉDITO:                        00000043|
|Fecha del DF y de Hora del DF||FECHA: 23-06-2022<br>HORA: 14:42|
|--------------------------------------------------------------|----------------------------------------------------------------------|**----------------------------------------------------**|
|Comentario en el cuerpo del Documento|**B Esto es un Comentario**||Esto es un Comentario||
|Tasa Exento|**d0000000100000001000Producto Exento**|Producto Exento (E)                             Bs 10,00|
|Descuento por Porcentaje|**p-**1000|DESC (10,00%)                                      Bs - 1,00|
|Tasa General|**d1000000200000001000Producto Genera**|Producto General (G)                           Bs 20,00|
|Recargo por Porcentaje|**p+**1000|RECAR (10,00%)                                    Bs   2,00|
|Tasa Reducida|**d2000000300000001000Producto Reducida**|Producto Reducida (R)                         Bs 30,00|
|Descuento por Monto|**q-**000001000|DESC<br>Bs - 10,00|
|Tasa Adicional|**d3000000400000001000ProductoAdicional**|Producto Adicional (A)                         Bs 40,00|
|Recargo por Monto|**q+**000001000|RECAR                                                     Bs 10,00|
|Tasa Exento|**d0 000000100000001000Producto Exento**|Producto Exento (E)                              Bs 10,00|
|Corrección|**k**|CORRECCIÓN|
|Cancela último ítem/descuento/recargo||Producto Exento (E)                           Bs - 10,00|
|Tasa Adicional|**d3000000400000001000 Producto Adicional**|Producto Adicional (A)                        Bs 40,00|
|||ANULACIÓN|
|Anula producto Tasa (A)|**á3000000400000001000ProductoAdicional**|Producto Adicional (A)                       Bs - 40,00|


**The Factory HKA, C.A. VENEZUELA**

**==> picture [95 x 43] intentionally omitted <==**

**MANUAL DE PROTOCOLOS Y COMANDOS V8.5.0 INTEGRACIÓN**

Código: **MIA-CINT-01** Versión N° **8.5.0** Fecha: **23/08/2022** Página  37

|Tasa Percibido|**d4000000500000001000ProductoPercibido**|Producto Percibido (P)                        Bs  50,00|
|---|---|---|
|Código de barra para un producto|**Y**1234567890128||
|-------------------------------|----------------------------------------------------------|**---------------------------------------------------**|
|Subtotal|**3**|SUBTTL      Bs 151,00<br>IVA          Bs 20,62|
|||**---------------------------------------------------**|
|Tasas de Impuesto utilizadas en el<br>cuerpo de la factura||EXENTO        Bs 9,00    PERCIBIDO     Bs 50,00|
|||BI G16,00%   Bs 22,00  IVA G16,00%  Bs 3,52|
|||BI R8,00%      Bs 20,00  IVA R8,00%    Bs 1,60|
|||BI A31,00%    Bs 50,00  IVA A31,00% Bs 15,50|
|------------------------------------------------------------|**-------------------------------------------------**|**---------------------------------------------------**|
|Subtotal de la Factura||SUBTTL        Bs 151,00  IVA               Bs 20,62|
|**-------------------------------------------**|**-------------------------------------------------**|**---------------------------------------------------**|
|Pago Parcial (Efectivo 1)|**201000000002062**|EFECTIVO 1<br>Bs 20,62|
|Pago Parcial (Cheque 5)|**211000000005100**|CHEQUE 5<br>Bs 51,00|
|Pago Directo(Divisa 3)|**122**|DIVISA 3<br>Bs 103,00|
|**--------------------------------------------**|**-------------------------------------------------**|**---------------------------------------------------**|
|||BI IGTF3,00% Bs 100,00   IGTF3,00%  Bs 3,00|
|Cierre de la Factura|**199**|**TOTAL**<br>**Bs 174,62**|
|Líneas Adicionales|**i01 Línea Adicional 01**|Línea Adicional 01|
||||
|Líneas Adicionales|**i09 Línea Adicional 09**|Línea Adicional 09|
|Pie de Ticket|**PH91**Pie de Ticket 01|Pie de Ticket 01|
||||
|Pie de Ticket|**PH98**Pie de Ticket 01|Pie de Ticket 08|
|Código de barra de Pie de Ticket|**y1234567890128**||
|||_MH_<br>Z1F9999988|
|**IMPORTANTE:**|**Para generar esta Nota de Crédito se activaron los siguientes Flags.**<br>**2100**<br>Se mantiene la confguración estándar de los montos que maneja la impresora.(Ver.<br>Tabla 21<br>**5001**<br>Se activa para realizar cálculo del IGTF aplicando pagos en moneda extranjera<br>**3001**<br>Imprime el código de barra con el número asociado bajo él código<br>**4300**<br>Se activa el codigo de barra**EAN13**<br>**199**<br>Comando que es de uso obligatorio para cerrar los documentos fscales ( Factura de<br>venta, Nota de Crédito, Nota de Débito) cuando el fag**50**está en**01.**||


Tabla 31. Ejemplo de comandos para emisión de Notas de Créditos

**The Factory HKA, C.A. VENEZUELA**

||**MANUAL DE PROTOCOLOS Y COMANDOS**<br>**V8.5.0**|Código:**MIA-CINT-01**|
|---|---|---|
|||Versión N°**8.5.0**|
||**INTEGRACIÓN**|Fecha:**23/08/2022**|
|||Página  38|


## **14.5. COMANDOS PARA GENERAR UNA NOTA DE DÉBITO**

|**Descripción**|**Descripción**||**Comando**|
|---|---|---|---|
|Ítem Exento|||**‘0**|
|Ítem Tasa 1  (General)|||**‘1**|
|Ítem Tasa 2  (Reducida)|||**‘2**|
|Ítem Tasa 3 (Adicional)|||**‘3**|
|Ítem Tasa 4 (Percibido)|||**‘4**|
|**Ejemplo de Trama**||**CMD**<br>**PRECIO**<br>**CANTIDAD**<br>**CODIGO**<br>**DESCRIPCIÓN**<br>**‘1**<br>**0000001000**<br>**00010000**<br>**8523**<br>**Producto**||
|**Anulación de ítem**||||
|Anulación de Exento||(à = 0xE0)|**à0**|
|Anulación de Tasa 1  (General)||(à = 0xE1)|**à1**|
|Anulación de Tasa 2  (Reducida)||(à = 0xE2)|**à2**|
|Anulación de Tasa 3 (Adicional)||(à = 0xE3)|**à3**|
|Anulación de Tasa 4 (Percibido)||(à = 0xE4)|**à4**|
|**Importante**|**Tasa 3 (Adicional):**programada en 0 es considerada<br>cómo percibido para las impresoras**SRP350,**<br>**SRP280, HSP7000, KUBE, HKA112, TD1125.**|||
|**Importante**|**Tasa 4 (Percibido):**sólo es aceptada para las<br>impresoras**SRP812, DT230, HKA80, PP9, PD3100DL, PP9-PLUS**<br>**TD1140.**|||


Tabla 32. Comandos para Nota de Débito

**The Factory HKA, C.A. VENEZUELA**

||**MANUAL DE PROTOCOLOS Y COMANDOS**<br>**V8.5.0**|Código:**MIA-CINT-01**|
|---|---|---|
|||Versión N°**8.5.0**|
||**INTEGRACIÓN**|Fecha:**23/08/2022**|
|||Página  39|


## **14.6. EJEMPLO PARA GENERAR UNA NOTA DE DÉBITO**

Tabla  general  para  realizar  una  Nota  de  Débito,  la  cual  incluye  todas  las  operaciones  posibles para éste documento.

**IMPORTANTE:** La  nota  de  débito  solo  es  soportada  para  los  siguientes  modelos  de  impresoras:  DT230,  SRP812, ACLAS PP9, ACLAS PP9-PLUS, HKA80 y PANTUM P3100DL

|**Descripción**|**Comandos**|**Ejemplo de una Nota de Débito impresa (imagen 11)**|
|---|---|---|
|||SENIAT|
|||RIF J-312171197|
|Encabezado|**PH01Encabezado 1**|ENCABEZADO 1|
||||
|Encabezado|**PH08 Encabezado**8|ENCABEZADO 8|
|Número de Factura Afectada|**(OBLIGATORIO)**<br>**iF*01020000001**|#FAC: 01020000001|
|Fecha de Factura Afectada|**(OBLIGATORIO)**<br>**iD*23/06/2022**|FECHA FAC: 23/06/2022|
|Número de Registro|**(OBLIGATORIO)**<br>**iI*Z1F1234567**|#CONTROL/SERIAL IF: Z1F1234567|
|RIF/C.I.|**(OBLIGATORIO)**<br>**iR*J-123456789**|RIF/C.I.: J-123456789|
|Razón Social|**(OBLIGATORIO) iS*The Factory HKA**|RAZON SOCIAL: The Factory HKA|
|Líneas Adicionales|**i01Línea Adicional 01**|Línea Adicional 01|
||||
|Líneas Adicionales|**i09Línea Adicional 09**|Línea Adicional 09|
|||NOTA DE DEBITO|
|Doc. Fiscal y Número de Nota de Débito||NOTA DE DEBITO:                        00000043|
|Fecha del DF y de Hora del DF||FECHA: 23-06-2022<br>HORA: 14:42|
|--------------------------------------------------------------|----------------------------------------------------------------------|**----------------------------------------------------**|
|Comentario en el cuerpo del Documento|**B Esto es un Comentario**||Esto es un Comentario||
|Tasa Exento|**‘0000000100000001000Producto Exento**|Producto Exento (E)                             Bs 10,00|
|Descuento por Porcentaje|**p-**1000|DESC (10,00%)                                      Bs - 1,00|
|Tasa General|**‘1000000200000001000Producto General**|Producto General (G)                           Bs 20,00|
|Recargo por Porcentaje|**p+**1000|RECAR (10,00%)                                    Bs   2,00|
|Tasa Reducida|**‘2000000300000001000Producto Reducida**|Producto Reducida (R)                         Bs 30,00|
|Descuento por Monto|**q-**000001000|DESC<br>Bs - 10,00|
|Tasa Adicional|**‘3000000400000001000ProductoAdicional**|Producto Adicional (A)                         Bs 40,00|
|Recargo por Monto|**q+**000001000|RECAR                                                     Bs 10,00|
|Tasa Exento|**‘0000000100000001000Producto Exento**|Producto Exento (E)                              Bs 10,00|
|Corrección|**k**|CORRECCIÓN|
|Cancela último ítem/descuento/recargo||Producto Exento (E)                           Bs - 10,00|
|Tasa Adicional|**‘3000000400000001000Producto Adicional**|Producto Adicional (A)                        Bs 40,00|
|||ANULACIÓN|


**The Factory HKA, C.A. VENEZUELA**

**==> picture [95 x 43] intentionally omitted <==**

**MANUAL DE PROTOCOLOS Y COMANDOS V8.5.0**

**==> picture [57 x 9] intentionally omitted <==**

**----- Start of picture text -----**<br>
||
|---|
|INTEGRACIÓN|

**----- End of picture text -----**<br>


Código: **MIA-CINT-01** Versión N° **8.5.0** Fecha: **23/08/2022** Página  40

|Anula producto Tasa (A)|**á3000000400000001000ProductoAdicional**|Producto Adicional (A)                       Bs - 40,00|
|---|---|---|
|Tasa Percibido|**á4000000500000001000ProductoPercibido**|Producto Percibido (P)                        Bs  50,00|
|Código de barra para un producto|**Y1234567890128**||
|-------------------------------|----------------------------------------------------------|**---------------------------------------------------**|
|Subtotal|**3**|SUBTTL|
|||**---------------------------------------------------**|
|Tasas de Impuesto utilizadas en el<br>cuerpo de la factura||EXENTO        Bs 9,00    PERCIBIDO     Bs 50,00|
|||BI G16,00%   Bs 22,00  IVA G16,00%  Bs 3,52|
|||BI R8,00%      Bs 20,00  IVA R8,00%    Bs 1,60|
|||BI A31,00%    Bs 50,00  IVA A31,00% Bs 15,50|
|------------------------------------------------------------|**-------------------------------------------------**|**---------------------------------------------------**|
|Subtotal de la Factura||SUBTTL        Bs 151,00  IVA               Bs 20,62|
|**-------------------------------------------**|**-------------------------------------------------**|**---------------------------------------------------**|
|Pago Parcial (Efectivo 1)|**201000000002062**|EFECTIVO 1<br>Bs 20,62|
|Pago Parcial (Cheque 5)|**211000000005100**|CHEQUE 5<br>Bs 51,00|
|Pago Directo(Divisa 3)|**122**|DIVISA 3<br>Bs 103,00|
|**--------------------------------------------**|**-------------------------------------------------**|**---------------------------------------------------**|
|||BI IGTF3,00% Bs 100,00   IGTF3,00%  Bs 3,00|
|Cierre de la Factura|**199**|**TOTAL**<br>**Bs 174,62**|
|Líneas Adicionales|**i01 Línea Adicional 01**|Línea Adicional 01|
||||
|Líneas Adicionales|**i09 Línea Adicional 09**|Línea Adicional 09|
|Pie de Ticket|**PH91Pie de Ticket 01**|Pie de Ticket 01|
||||
|Pie de Ticket|**PH98Pie de Ticket 01**|Pie de Ticket 08|
|Código de barra de Pie de Ticket|**y1234567890128**||
|||_MH_<br>Z1F9999988|
|**IMPORTANTE:**|**Para generar esta Nota de Débito se activaron los siguientes Flags.**<br>**2100**<br>Se mantiene la confguración estándar de los montos que maneja la impresora.(Ver.<br>Tabla 21<br>**5001**<br>Se activa para realizar cálculo del IGTF aplicando pagos en moneda extranjera<br>**3001**<br>Imprime el código de barra con el número asociado bajo él código<br>**4300**<br>Se activa el codigo de barra**EAN13**<br>**199**<br>Comando que es de uso obligatorio para cerrar los documentos fscales ( Factura de<br>venta, Nota de Crédito, Nota de Débito) cuando el fag**50**está en**01.**||


Tabla 33. Ejemplo de comandos para emisión de Notas de Débitos.

**The Factory HKA, C.A. VENEZUELA**

||**MANUAL DE PROTOCOLOS Y COMANDOS**<br>**V8.5.0**|Código:**MIA-CINT-01**|
|---|---|---|
|||Versión N°**8.5.0**|
||**INTEGRACIÓN**|Fecha:**23/08/2022**|
|||Página  41|


## **15. COMANDOS PARA GENERAR DOCUMENTOS NO FISCALES**

Tabla  general  para  realizar  un  Documento  No  Fiscal,  la  cual  incluye  todas  las  operaciones posibles para este documento.

|**Descripción**|**Comandos**|**Ejemplo  de un Documento No Fiscal**|
|---|---|---|
|||SENIAT|
|||RIF J-312171197|
|Encabezado|**PH01Encabezado 1**|ENCABEZADO 1|
||||
|Encabezado|**PH08 Encabezado**8|ENCABEZADO 8|
|||DOCUMENTO NO FISCAL|
|Doc. NO Fiscal y Número de Documento||NO FISCAL:                                00000257|
|Fecha del DNF y de Hora del DNF||FECHA: 23-06-2022<br>HORA: 14:42|
|--------------------------------------------------------------|----------------------------------------------------------------------|**----------------------------------------------------**|
|Apertura el documento No Fiscal|**800Documento de prueba**|Documento de prueba|
|||NO FISCAL|
|Efecto negrita|**80*los documentos NO Fiscales y de sus**|**los documentos NO Fiscales y de sus**|
|Efecto expandido|**80>distintas características y efectos…**|_distintas características y efectos…_|
|Efecto negrita + centrado + doble ancho|**80$dichos documentos pueden ser**|**dichos documentos pueden ser**|
|Efecto centrado|**80!la impresión de reportes internos**|la impresión de reportes internos|
|Efecto negrita + centrado|**80¡comandos que reciben las impresoras**|**comandos que reciben las impresoras**|
|Cierra el documento No Fiscal|**810fn del uso**|Fin del uso|
|||_NO FISCAL_<br>Z1F9999988|


Tabla 34. Secuencia de comandos para emisión de Documentos No Fisca les

**The Factory HKA, C.A. VENEZUELA**

||**MANUAL DE PROTOCOLOS Y COMANDOS**<br>**V8.5.0**|Código:**MIA-CINT-01**|
|---|---|---|
|||Versión N°**8.5.0**|
||**INTEGRACIÓN**|Fecha:**23/08/2022**|
|||Página  42|


## **16. COMANDOS GENERALES**

## **16.1. TABLA DE IMPRESORA QUE ACEPTAN COMANDOS GENERALES**

|**Modelo de**<br>**Impresora**|**Factura**|**Nota de Crédito**|**Nota de Débito**|
|---|---|---|---|
|**Valor Maximo**|**(Precio unitario)**<br>**99.999.999.999.999,99**|**(Cantidad Item)**<br>**99.999.999.999.999,999**|**(Total Item)**<br>**99.999.999.999.999,99**|
|**SRP-812**|✅|✅|✅|
|**DT-230**|✅|✅|✅|
|**HKA-80**|✅|✅|✅|
|**PP9**|✅|✅|✅|
|**PP9 PLUS**|✅|✅|✅|
|**P3100DL**|✅|✅|✅|
|**TD1140**|✅|✅|✅|
|**Modelo de**<br>**Impresora**|**Factura**|**Nota de Crédito**|**Nota de Débito**|
|**Valor Maximo**|**(Precio unitario)**<br>**9.999.999.999,99**|**(Cantidad Item)**<br>**2.147.483,647**|**(Total Item)**<br>**9.999.999.999,99**|
|**SRP-350**|❌|❌|❌|
|**HKA-112**|✅|✅|❌|
|**HSP7000**|✅|✅|❌|
|**TALLY 1125**|✅|✅|❌|
|**KUBE**|✅|✅|❌|
|||||


Tabla 35. Tabla de impresoras que aceptan comandos generales

**The Factory HKA, C.A. VENEZUELA**

||**MANUAL DE PROTOCOLOS Y COMANDOS**<br>**V8.5.0**|Código:**MIA-CINT-01**|
|---|---|---|
|||Versión N°**8.5.0**|
||**INTEGRACIÓN**|Fecha:**23/08/2022**|
|||Página  43|


## **16.2. EJEMPLO DE COMANDOS GENERALES PARA REALIZAR UNA FACTURA**

Esquema  general  para  realizar  una  factura,  el  cual  incluye  todas  las  operaciones  posibles  para éste documento.

|**Descripción**|**Comandos**|**Ejemplo de una Factura impresa**|
|---|---|---|
|||SENIAT|
|||RIF J-312171197|
|Encabezado|**PH01Encabezado 1**|ENCABEZADO 1|
||||
|Encabezado|**PH08 Encabezado 8**|ENCABEZADO 8|
|RIF/C.I.|**iR*J-123456789**|RIF/C.I.: J-123456789|
|Razón Social|**iS*The Factory HKA**|Razón Social: The Factory HKA|
|Líneas Adicionales|**i01Línea Adicional 01**|Línea Adicional 01|
|Líneas Adicionales|**i09Línea Adicional 09**|Línea Adicional 09|
|||FACTURA|
|Doc. Fiscal y Número de Factura||FACTURA:<br>00001325|
|Fecha del DF y de Hora del DF||FECHA: 16-08-2016                     HORA: 14:42|
|------------------------------------------------------|-----------------------------------------------------------------------|**------------------------------------------------------**|
|Comentario en el cuerpo del Documento|**@Esto es un Comentario**||Esto es un Comentario||
|Tasa Exento|**GF+000000000000010,00||00000000000001,0**<br>**00||Producto Exento**|Producto Exento (E)                              Bs 10,00|
|Descuento por Porcentaje|**p-1000**|DESC (10,00%)                                       Bs - 1,00|
|Tasa General|**GF+100000000000020,00||00000000000001,0**<br>**00||ProductoGeneral**|Producto General (G)                            Bs 20,00|
|Recargo por Porcentaje|**p+1000**|RECAR (10,00%)                                     Bs 2,00|
|Tasa Reducida|**GF+200000000000030,00||00000000000001,0**<br>**00||ProductoReducida**|Producto Reducida (R)                          Bs 30,00|
|Descuento por Monto|**q-000001000**|DESC<br>Bs - 10,00|
|Tasa Adicional|**GF+300000000000040,00||00000000000001,0**<br>**00||Producto Adicional**|Producto Adicional (A)                          Bs 40,00|
|Recargo por Monto|**q+000001000**|RECAR                                                      Bs 10,00|
|Tasa Exento|**GF+000000000000010,00||00000000000001,0**<br>**00||Producto Exento**|Producto Exento (E)                               Bs 10,00|
|Corrección|**k**|CORRECCIÓN|
|Cancela último<br>ítem/descuento/recargo|**GF-000000000000010,00||00000000000001,0**<br>**00||Producto Exento**|Producto Exento (E)                              Bs - 10,00|
|Tasa Adicional|**GF+300000000000040,00||00000000000001,0**<br>**00||Producto Adicional**|Producto Adicional (A)                          Bs 40,00|
|||ANULACIÓN|


**The Factory HKA, C.A. VENEZUELA**

**==> picture [95 x 43] intentionally omitted <==**

**MANUAL DE PROTOCOLOS Y COMANDOS** Código: **MIA-CINT-01 V8.5.0** Versión N° **8.5.0** Fecha: **23/08/2022 INTEGRACIÓN** Página  44

|Anular producto Tasa (A)|**GF-300000000000040,00||00000000000001,0**<br>**00||Producto Adicional**|Producto Adicional (A)                          Bs - 40,00|
|---|---|---|
|Tasa Percibido|**GF+400000000000050,00||00000000000001,0**<br>**00||Producto Percibido**|Producto Percibido (P)                          Bs 50,00|
|Código de barra para un producto|**Y1234567890128**||
|-------------------------------|----------------------------------------------------------|**-----------------------------------------------------**|
|Subtotal|**3**|SUBTTL                                                 Bs 151,00|
|||**-----------------------------------------------------**|
|Tasas de Impuesto utilizadas en<br>el cuerpo de la factura||EXENTO         Bs 9,00       PERCIBIDO  Bs 50,00|
|||BI G16,00%    Bs 22,00    IVA G16,00   Bs 3,52|
|||BI R8,00%      Bs 20,00      IVA R8,00%  Bs 1,60|
|||BI A31,00%    Bs 50,00<br>IVA A31,00 Bs 15,50|
|------------------------------------------------------|**--------------------------------------------------**|**-----------------------------------------------------**|
|Subtotal de la Factura||SUBTTL          Bs 151,00   IVA              Bs 20,62|
|**--------------------------------------**|**--------------------------------------------------**|**-----------------------------------------------------**|
|Pago Parcial (Efectivo 1)|**201000000002062**|EFECTIVO 1<br>Bs 20,62|
|Pago Parcial (Cheque 5)|**211000000005100**|CHEQUE 5<br>Bs 51,00|
|Pago Directo(Divisa 3)|**122**|DIVISA 3                                                Bs 103,00|
|**--------------------------------------**|**--------------------------------------------------**|**-----------------------------------------------------**|
|||BI IGTF3,00% Bs 100,00    IGTF3,00%  Bs 3,00|
|Cierre de la Factura|**199**|**TOTAL**<br>**Bs 174,62**|
|Líneas Adicionales|**i01 Línea Adicional 01**|Línea Adicional 01|
||||
|Líneas Adicionales|**i09 Línea Adicional 09**|Línea Adicional 09|
|Pie de Ticket|**PH91Pie de Ticket 01**|Pie de Ticket 01|
||||
|Pie de Ticket|**PH98Pie de Ticket 01**|Pie de Ticket 08|
|Código de barra de Pie de Ticket|**y1234567890128**||
|||_MH_<br>Z1F9999988|
|**IMPORTANTE:**|**Para generar esta Nota de Crédito se activaron los siguientes Flags.**<br>**2100**<br>Se mantiene la confguración estándar de los montos que maneja la impresora.(Ver.<br>Tabla 21<br>**5001**<br>Se activa para realizar cálculo del IGTF aplicando pagos en moneda extranjera<br>**3001**<br>Imprime el código de barra con el número asociado bajo él código<br>**4300**<br>Se activa el codigo de barra**EAN13**<br>**199**<br>Comando que es de uso obligatorio para cerrar los documentos fscales ( Factura de venta,<br>Nota de Crédito, Nota de Débito) cuando el fag**50**está en**01.**||


Tabla 36. Ejemplo de comandos para comandos generales en Facturas

**The Factory HKA, C.A. VENEZUELA**

**MANUAL DE PROTOCOLOS Y COMANDOS V8.5.0**

**INTEGRACIÓN**

**==> picture [95 x 43] intentionally omitted <==**

Código: **MIA-CINT-01** Versión N° **8.5.0** Fecha: **23/08/2022** Página  45

## **16.3. EJEMPLO  DE  COMANDOS  GENERALES  PARA  REALIZAR  UNA  NOTA  DE CRÉDITO**

|**Descripción**|**Comandos**|**Ejemplo de una Nota de crédito impresa**|
|---|---|---|
|||SENIAT|
|||RIF J-312171197|
|Encabezado|**PH01Encabezado 1**|ENCABEZADO 1|
||||
|Encabezado|**PH08 Encabezado 8**|ENCABEZADO 8|
|Número de Factura Afectada|**(OBLIGATORIO)**<br>**iF*01020000001**|#FAC: 01020000001|
|Fecha de Factura Afectada|**(OBLIGATORIO)**<br>**iD*23/06/2022**|FECHA FAC: 23/06/2022|
|Número de Registro|**(OBLIGATORIO)**<br>**iI*Z1F1234567**|#CONTROL/SERIAL IF: Z1F1234567|
|RIF/C.I.|**(OBLIGATORIO)**<br>**iR*J-123456789**|RIF/C.I.: J-123456789|
|Razón Social|**(OBLIGATORIO) iS*The Factory HKA**|RAZON SOCIAL: The Factory HKA|
|Líneas Adicionales|**i09Línea Adicional 09**|Línea Adicional 09|
|||NOTA DE CRÉDITO|
|Doc. Fiscal y Número de Factura||NOTA DE CRÉDITO:                        00000043|
|Fecha del DF y de Hora del DF||FECHA: 16-08-2016                     HORA: 14:42|
|------------------------------------------------------|-----------------------------------------------------------------------|**------------------------------------------------------**|
|Comentario en el cuerpo del<br>Documento|**@Esto es un Comentario**||Esto es un Comentario||
|Tasa Exento|**GC+000000000000010,00||00000000000001,0**<br>**00||Producto Exento**|Producto Exento (E)                              Bs 10,00|
|Descuento por Porcentaje|**p-1000**|DESC (10,00%)                                       Bs - 1,00|
|Tasa General|**GC+100000000000020,00||00000000000001,0**<br>**00||ProductoGeneral**|Producto General (G)                            Bs 20,00|
|Recargo por Porcentaje|**p+1000**|RECAR (10,00%)                                     Bs 2,00|
|Tasa Reducida|**GC+200000000000030,00||00000000000001,0**<br>**00||ProductoReducida**|Producto Reducida (R)                          Bs 30,00|
|Descuento por Monto|**q-000001000**|DESC<br>Bs - 10,00|
|Tasa Adicional|**GC+300000000000040,00||00000000000001,0**<br>**00||Producto Adicional**|Producto Adicional (A)                          Bs 40,00|
|Recargo por Monto|**q+000001000**|RECAR                                                      Bs 10,00|
|Tasa Exento|**GC+000000000000010,00||00000000000001,0**<br>**00||Producto Exento**|Producto Exento (E)                               Bs 10,00|
|Corrección|**k**|CORRECCIÓN|
|Cancela último<br>ítem/descuento/recargo|**GC-000000000000010,00||00000000000001,0**<br>**00||Producto Exento**|Producto Exento (E)                              Bs - 10,00|
|Tasa Adicional|**GC+300000000000040,00||00000000000001,0**<br>**00||Producto Adicional**|Producto Adicional (A)                          Bs 40,00|
|||ANULACIÓN|


**The Factory HKA, C.A. VENEZUELA**

**==> picture [95 x 43] intentionally omitted <==**

## **MANUAL DE PROTOCOLOS Y COMANDOS V8.5.0**

**INTEGRACIÓN**

Código: **MIA-CINT-01** Versión N° **8.5.0** Fecha: **23/08/2022** Página  46

|Anular producto Tasa (A)|**GC-300000000000040,00||00000000000001,0**<br>**00||Producto Adicional**|Producto Adicional (A)                          Bs - 40,00|
|---|---|---|
|Tasa Percibido|**GC+400000000000050,00||00000000000001,0**<br>**00||Producto Percibido**|Producto Percibido (P)                          Bs 50,00|
|Código de barra para un producto|**Y1234567890128**||
|-------------------------------|----------------------------------------------------------|**-----------------------------------------------------**|
|Subtotal|**3**|SUBTTL                                                 Bs 151,00|
|||**-----------------------------------------------------**|
|Tasas de Impuesto utilizadas en<br>el<br>cuerpo de la factura||EXENTO         Bs 9,00       PERCIBIDO  Bs 50,00|
|||BI G16,00%    Bs 22,00    IVA G16,00   Bs 3,52|
|||BI R8,00%      Bs 20,00      IVA R8,00%  Bs 1,60|
|||BI A31,00%    Bs 50,00<br>IVA A31,00 Bs 15,50|
|------------------------------------------------------|**--------------------------------------------------**|**-----------------------------------------------------**|
|Subtotal de la Factura||SUBTTL          Bs 151,00   IVA              Bs 20,62|
|**--------------------------------------**|**--------------------------------------------------**|**-----------------------------------------------------**|
|Pago Parcial (Efectivo 1)|**201000000002062**|EFECTIVO 1<br>Bs 20,62|
|Pago Parcial (Cheque 5)|**211000000005100**|CHEQUE 5<br>Bs 51,00|
|Pago Directo(Divisa 3)|**122**|DIVISA 3                                                Bs 103,00|
|**--------------------------------------**|**--------------------------------------------------**|**-----------------------------------------------------**|
|||BI IGTF3,00% Bs 100,00    IGTF3,00%  Bs 3,00|
|Cierre de la Factura|**199**|**TOTAL**<br>**Bs 174,62**|
|Líneas Adicionales|**i01 Línea Adicional 01**|Línea Adicional 01|
||||
|Líneas Adicionales|**i09 Línea Adicional 09**|Línea Adicional 09|
|Pie de Ticket|**PH91Pie de Ticket 01**|Pie de Ticket 01|
||||
|Pie de Ticket|**PH98Pie de Ticket 01**|Pie de Ticket 08|
|Código de barra de Pie de Ticket|**y1234567890128**||
|||_MH_<br>Z1F9999988|
|**IMPORTANTE:**|**Para generar esta Nota de Crédito se activaron los siguientes Flags.**<br>**2100**<br>Se mantiene la confguración estándar de los montos que maneja la impresora.(Ver.<br>Tabla 21<br>**5001**<br>Se activa para realizar cálculo del IGTF aplicando pagos en moneda extranjera<br>**3001**<br>Imprime el código de barra con el número asociado bajo él código<br>**4300**<br>Se activa el codigo de barra**EAN13**<br>**199**<br>Comando que es de uso obligatorio para cerrar los documentos fscales ( Factura de venta,<br>Nota de Crédito, Nota de Débito) cuando el fag**50**está en**01.**||


Tabla 37. Ejemplo de comandos para comandos generales en Notas de Crédito.

.

**The Factory HKA, C.A. VENEZUELA**

**MANUAL DE PROTOCOLOS Y COMANDOS V8.5.0**

**==> picture [95 x 43] intentionally omitted <==**

**INTEGRACIÓN**

Código: **MIA-CINT-01** Versión N° **8.5.0** Fecha: **23/08/2022** Página  47

## **16.4. EJEMPLO  DE  COMANDOS  GENERALES  PARA  REALIZAR  UNA  NOTA  DE DÉBITO**

|**Descripción**|**Comandos**|**Ejemplo de una Nota de débito impresa**|
|---|---|---|
|||SENIAT|
|||RIF J-312171197|
|Encabezado|**PH01Encabezado 1**|ENCABEZADO 1|
||||
|Encabezado|**PH08 Encabezado 8**|ENCABEZADO 8|
|Número de Factura Afectada|**(OBLIGATORIO) iF*01020000001**|#FAC: 01020000001|
|Fecha de Factura Afectada|**(OBLIGATORIO) iD*23/06/2022**|FECHA FAC: 23/06/2022|
|Número de Registro|**(OBLIGATORIO) iI*Z1F1234567**|#CONTROL/SERIAL IF: Z1F1234567|
|RIF/C.I.|**(OBLIGATORIO) iR*J-123456789**|RIF/C.I.: J-123456789|
|Razón Social|**(OBLIGATORIO) iS*The Factory HKA**|RAZON SOCIAL: The Factory HKA|
|Líneas Adicionales|**i09Línea Adicional 09**|Línea Adicional 09|
|||NOTA DE DÉBITO|
|Doc. Fiscal y Número de Factura||NOTA DE CRÉDITO:                           00000043|
|Fecha del DF y de Hora del DF||FECHA: 16-08-2016                       HORA: 14:42|
|------------------------------------------------------|-----------------------------------------------------------------------|**------------------------------------------------------**|
|Comentario en el cuerpo del<br>Documento|**@Esto es un Comentario**||Esto es un Comentario||
|Tasa Exento|**GD+000000000000010,00||00000000000001,0**<br>**00||Producto Exento**|Producto Exento (E)                              Bs 10,00|
|Descuento por Porcentaje|**p-1000**|DESC (10,00%)                                       Bs - 1,00|
|Tasa General|**GD+100000000000020,00||00000000000001,0**<br>**00||ProductoGeneral**|Producto General (G)                            Bs 20,00|
|Recargo por Porcentaje|**p+1000**|RECAR (10,00%)                                     Bs 2,00|
|Tasa Reducida|**GD+200000000000030,00||00000000000001,0**<br>**00||ProductoReducida**|Producto Reducida (R)                          Bs 30,00|
|Descuento por Monto|**q-000001000**|DESC<br>Bs - 10,00|
|Tasa Adicional|**GD+300000000000040,00||00000000000001,0**<br>**00||Producto Adicional**|Producto Adicional (A)                          Bs 40,00|
|Recargo por Monto|**q+000001000**|RECAR                                                      Bs 10,00|
|Tasa Exento|**GD+000000000000010,00||00000000000001,0**<br>**00||Producto Exento**|Producto Exento (E)                               Bs 10,00|
|Corrección|**k**|CORRECCIÓN|
|Cancela último<br>ítem/descuento/recargo|**GD-000000000000010,00||00000000000001,0**<br>**00||Producto Exento**|Producto Exento (E)                              Bs - 10,00|
|Tasa Adicional|**GD+300000000000040,00||00000000000001,0**<br>**00||Producto Adicional**|Producto Adicional (A)                          Bs 40,00|
|||ANULACIÓN|


**The Factory HKA, C.A. VENEZUELA**

**==> picture [95 x 43] intentionally omitted <==**

## **MANUAL DE PROTOCOLOS Y COMANDOS V8.5.0**

**INTEGRACIÓN**

Código: **MIA-CINT-01** Versión N° **8.5.0** Fecha: **23/08/2022** Página  48

|Anular producto Tasa (A)|**GD-300000000000040,00||00000000000001,0**<br>**00||Producto Adicional**|Producto Adicional (A)                          Bs - 40,00|
|---|---|---|
|Tasa Percibido|**GD+400000000000050,00||00000000000001,0**<br>**00||Producto Percibido**|Producto Percibido (P)                          Bs 50,00|
|Código de barra para un producto|**Y1234567890128**||
|-------------------------------|----------------------------------------------------------|**-----------------------------------------------------**|
|Subtotal|**3**|SUBTTL                                                 Bs 151,00|
|||**-----------------------------------------------------**|
|Tasas de Impuesto utilizadas en<br>el cuerpo de la factura||EXENTO         Bs 9,00       PERCIBIDO  Bs 50,00|
|||BI G16,00%    Bs 22,00    IVA G16,00   Bs 3,52|
|||BI R8,00%      Bs 20,00      IVA R8,00%  Bs 1,60|
|||BI A31,00%    Bs 50,00<br>IVA A31,00 Bs 15,50|
|------------------------------------------------------|**--------------------------------------------------**|**-----------------------------------------------------**|
|Subtotal de la Factura||SUBTTL          Bs 151,00   IVA              Bs 20,62|
|**--------------------------------------**|**--------------------------------------------------**|**-----------------------------------------------------**|
|Pago Parcial (Efectivo 1)|**201000000002062**|EFECTIVO 1<br>Bs 20,62|
|Pago Parcial (Cheque 5)|**211000000005100**|CHEQUE 5<br>Bs 51,00|
|Pago Directo(Divisa 3)|**122**|DIVISA 3                                                Bs 103,00|
|**--------------------------------------**|**--------------------------------------------------**|**-----------------------------------------------------**|
|||BI IGTF3,00% Bs 100,00    IGTF3,00%  Bs 3,00|
|Cierre de la Factura|**199**|**TOTAL**<br>**Bs 174,62**|
|Líneas Adicionales|**i01 Línea Adicional 01**|Línea Adicional 01|
||||
|Líneas Adicionales|**i09 Línea Adicional 09**|Línea Adicional 09|
|Pie de Ticket|**PH91Pie de Ticket 01**|Pie de Ticket 01|
||||
|Pie de Ticket|**PH98Pie de Ticket 01**|Pie de Ticket 08|
|Código de barra de Pie de Ticket|**y1234567890128**||
|||_MH_<br>Z1F9999988|
|**IMPORTANTE:**|**Para generar esta Nota de Crédito se activaron los siguientes Flags.**<br>**2100**<br>Se mantiene la confguración estándar de los montos que maneja la impresora.(Ver.<br>Tabla 21)<br>**5001**<br>Se activa para realizar cálculo del IGTF aplicando pagos en moneda extranjera<br>**3001**<br>Imprime el código de barra con el número asociado bajo él código<br>**4300**<br>Se activa el codigo de barra**EAN13**<br>**199**<br>Comando que es de uso obligatorio para cerrar los documentos fscales ( Factura de venta,<br>Nota de Crédito, Nota de Débito) cuando el fag**50**está en**01.**||


Tabla 38. Ejemplo de comandos para comandos generales en Notas de Débito.

**The Factory HKA, C.A. VENEZUELA**

||**MANUAL DE PROTOCOLOS Y COMANDOS**<br>**V8.5.0**|Código:**MIA-CINT-01**|
|---|---|---|
|||Versión N°**8.5.0**|
||**INTEGRACIÓN**|Fecha:**23/08/2022**|
|||Página  49|


## **17. REIMPRESIÓN DE DOCUMENTOS DE LA MEMORIA DE AUDITORIA**

Todos  los  documentos  que  se  generen  con  la  impresora  fiscal,  quedarán  registrados  en  la memoria  de  auditoría,  por  lo  cual  se  puede  acceder  a  ellos  mediante  la  reimpresión  o  extracción de los documentos existentes en dicha memoria.

## **17.1. REIMPRESIÓN POR RANGO DE NÚMERO**

Este comando permite reimprimir documentos ya registrados en la memoria de auditoría por un rango de números.

|**Descripción**|**Comandos**|
|---|---|
|Facturas|**RF00000010000001**|
|Notas de Crédito|**RC00000010000001**|
|Notas de Débito|**RD00000010000001**|
|Todos los documentos no fscales|**RT00000010000001**|
|Reportes X|**RX00000010000001**|
|Reportes Z|**RZ00000010000001**|
|Reportes de lectura de memoria fscal|**RR00000010000001**|
|RAM CLEAR|**RY00000010000001**|
|Copias|**RE00000010000001**|
|Facturas, Notas de Crédito y Notas de Débito|**RS00000010000001**|
|Todos los documentos excepto copias y errores de bloqueo|**RA00000010000001**|
|Documentos no Fiscales excepto RAM CLEAR, copias y Reportes X|**RN00000010000001**|
|Todos los documentos|**R@00000010000001**|
|Último documento registrado|**RU00000000000000**|
|Reimpresión por rango de número (Inicio: 7 Dígitos y Fin: 7 Dígitos)||


Tabla 39. Comandos para reimpresión de documentos por número.

**The Factory HKA, C.A. VENEZUELA**

||**MANUAL DE PROTOCOLOS Y COMANDOS**<br>**V8.5.0**|Código:**MIA-CINT-01**|
|---|---|---|
|||Versión N°**8.5.0**|
||**INTEGRACIÓN**|Fecha:**23/08/2022**|
|||Página  50|


## **17.2. REIMPRESIÓN POR RANGO DE FECHA**

Este comando permite reimprimir documentos ya registrados en la memoria de auditoría por un rango de fechas.

|**Descripción**|**Comandos**|
|---|---|
|Facturas|**Rf03006220300622**|
|Notas de Crédito|**Rc03006220300622**|
|Notas de Débito|**Rd03006220300622**|
|Todos los documentos no fscales|**Rt03006220300622**|
|Reportes X|**Rx03006220300622**|
|Reportes Z|**Rz03006220300622**|
|Reportes de lectura de memoria fscal|**Rr03006220300622**|
|RAM CLEAR|**Ry03006220300622**|
|Copias|**Re03006220300622**|
|Facturas, Notas de Crédito y Notas de Débito|**Rs03006220300622**|
|Todos los documentos excepto copias y errores de bloqueo|**Ra03006220300622**|
|Documentos no Fiscales excepto RAM CLEAR, copias y Reportes X|**Rn03006220300622**|
|Todos los documentos|**R*03006220300622**|
|||
|Reimpresión por rango de fechas (Inicio: 7 Dígitos y Fin: 7 Dígitos)||


Tabla 40. Comandos para reimpresión de documentos por fechas.

## **17.3. REIMPRESIÓN POR NÚMERO DE CÉDULA O RIF**

Para  reimprimir  documentos  por  el  número  de  cédula  del  cliente,  se  debe  enviar  el  número  de cédula  del  mismo  modo  que  en  el  comando  de  registro  del  cliente.  La  forma  general  del comando es la siguiente:

||**Descripción**|**Comandos**||
|---|---|---|---|
||Número de RIF o C.I. del cliente.|**RK21221012**||
|Tabla 41. Comandos para reimpresión de documentos por número de cédula/RIF||||


**The Factory HKA, C.A. VENEZUELA**

||**MANUAL DE PROTOCOLOS Y COMANDOS**<br>**V8.5.0**|Código:**MIA-CINT-01**|
|---|---|---|
|||Versión N°**8.5.0**|
||**INTEGRACIÓN**|Fecha:**23/08/2022**|
|||Página  51|


## **18. EXTRACCIÓN DE DOCUMENTOS DE LA MEMORIA DE AUDITORIA 18.1. EXTRACCIÓN POR RANGO DE NÚMERO**

Este comando permite la subida de un documento ya registrado en la memoria de auditoría por un rango de números.

|**Descripción**|**Comandos**|
|---|---|
|Facturas|**U4F00000010000001**|
|Notas de Crédito|**U4C00000010000001**|
|Notas de Débito|**U4D00000010000001**|
|Todos los documentos no fscales|**U4T00000010000001**|
|Reportes X|**U4X00000010000001**|
|Reportes Z|**U4Z00000010000001**|
|Reportes de lectura de memoria fscal|**U4R00000010000001**|
|RAM CLEAR|**U4Y00000010000001**|
|Copias|**U4E00000010000001**|
|Facturas, Notas de Crédito y Notas de Débito|**U4S00000010000001**|
|Todos los documentos excepto copias y errores de bloqueo|**U4A00000010000001**|
|Documentos no Fiscales excepto RAM CLEAR, copias y Reportes X|**U4N00000010000001**|
|Todos los documentos|**U4@00000010000001**|
|||
|Extracción por rango de número (Inicio: 7 Dígitos y Fin: 7 Dígitos)||


Tabla 42. Comandos para extracción de documentos por número.

## **18.2. EXTRACCIÓN POR RANGO DE FECHA**

Este comando permite la carga de un documento ya registrado en la memoria de auditoría por un rango de fechas.

|**Descripción**|**Comandos**|
|---|---|
|Facturas|**U4f03006220300622**|
|Notas de Crédito|**U4c03006220300622**|
|Notas de Débito|**U4d03006220300622**|
|Todos los documentos no fscales|**U4t03006220300622**|


**The Factory HKA, C.A. VENEZUELA**

|||**MANUAL DE PROTOCOLOS Y COMANDOS**<br>**V8.5.0**|**MANUAL DE PROTOCOLOS Y COMANDOS**<br>**V8.5.0**|Código:**MIA-CINT-01**|
|---|---|---|---|---|
|||||Versión N°**8.5.0**|
|||**INTEGRACIÓN**||Fecha:**23/08/2022**|
|||||Página  52|
||||||
||||||
||Reportes X||**U4x03006220300622**||
||Reportes Z||**U4z03006220300622**||
||Reportes de lectura de memoria fscal||**U4r03006220300622**||
||RAM CLEAR||**U4y03006220300622**||
||Copias||**U4e03006220300622**||
||Facturas, Notas de Crédito y Notas de Débito||**U4s03006220300622**||
||Todos los documentos excepto copias y errores de bloqueo||**U4a03006220300622**||
||Documentos no Fiscales excepto RAM CLEAR, copias y Reportes X||**U4n03006220300622**||
||Todos los documentos||**U4*03006220300622**||
||||||
||Extracción por rango de fechas (Inicio: 7 Dígitos y Fin: 7 Dígitos)||||


Tabla 43. Comandos para reimpresión de documentos por fecha.

## **18.3. EXTRACCIÓN POR NÚMERO DE CÉDULA O RIF**

Para  cargar  documentos  por  el  número  de  cédula  del  cliente,  se  debe  enviar  el  número  de  cédula del  mismo  modo  que  en  el  comando  de  registro  del  cliente.  La  forma  general  del  comando  es  la siguiente:

|**Descripción**|**Comandos**|
|---|---|
|Número de RIF o C.I. del cliente.|**U4K21221012**|


## **19. LEER STATUS DE INFORMACIÓN**

Se  puede  tener  acceso  a  la  información  que  posee  la  impresora  Fiscal,  dicha  información  es repartida en diversos status informativos.

En  el  caso  de  que  se  utilice  protocolo  directo,  debe  enviar  la  trama  de  la  solicitud  que  desee  y leer  la  respuesta  en  el  puerto  de  comunicaciones  basándose  en  las  tablas  de  respuesta  aquí descritas.  En  el  caso  de  que  use  algunos  de  los  componentes  de  The  Factory  HKA  (DLL,  API, App  consola)  debe  usar  la  función **UploadStatusCmd  (String  cmd,  String  file)** , **UploadStatusDin (Status  As  Long,  Error  As  Long,  cmd  As  String,  Cadena  As  String)** o  hacer  uso  de  los  atributos públicos de la clase Tfhka (aplica para desarrollos en .NET y Java).

**The Factory HKA, C.A. VENEZUELA**

**==> picture [95 x 43] intentionally omitted <==**

**MANUAL DE PROTOCOLOS Y COMANDOS V8.5.0 INTEGRACIÓN**

Código: **MIA-CINT-01** Versión N° **8.5.0** Fecha: **23/08/2022** Página  53

## **19.1. STATUS S1**

Este  comando  permite  consultar  información  referente  a  parámetros  de  la  impresora  fiscal como  Serial  de  la  misma,  RIF,  datos  de  factura,  entre  otros.  Este  comando  es  posible  ejecutarlo en cualquier condición .

|**Descripción**|**Para las impresoras: SRP350,**<br>**HSP7000, TD1125, HKA112, KUBE.**|**Para las impresoras: SRP350,**<br>**HSP7000, TD1125, HKA112, KUBE.**|**Para las impresoras: SRP350,**<br>**HSP7000, TD1125, HKA112, KUBE.**|**Para las impresoras: SRP350,**<br>**HSP7000, TD1125, HKA112, KUBE.**|**Para las impresoras: SRP350,**<br>**HSP7000, TD1125, HKA112, KUBE.**||
|---|---|---|---|---|---|---|
||**Librería**||**Protocolo**<br>**Directo**||**L**||
||**Desde**|**Hasta**|**Desde**|**Hasta**|||
|**Status y Número de Cajero.**|0|3|0|3|4||
|**Subtotal de Ventas (Bs.)**|5|21|4|20|17||
|**Número de la Última Factura.**|23|30|21|28|8||
|**Cantidad de Facturas Emitidas en el día.**|32|36|29|33|5||
|**Número del Último Documento No Fiscal.**|38|45|34|41|8||
|**Cantidad de Documentos No Fiscales.**|47|51|42|46|5||
|**Contador de Cierres Diarios (Z).**|53|56|47|50|4||
|**Contador de Reportes de Memoria Fiscal.**|58|61|51|54|4||
|**RIF.**|63|73|55|65|11||
|**Número de Registro de la Máquina.**|75|84|66|75|10||
|**Hora Actual de la Impresora.**|86|91|76|81|6||
|**Fecha Actual de la Impresora.**|93|98|82|87|6||
|**Número de Última Nota de Crédito.**|100|107|88|95|8||
|**Cantidad de Notas de Crédito.**|109|113|96|100|5||
|**Longitud Total.**|**114**||**100**||**114**||


**The Factory HKA, C.A. VENEZUELA**

**==> picture [95 x 43] intentionally omitted <==**

## **MANUAL DE PROTOCOLOS Y COMANDOS V8.5.0**

**INTEGRACIÓN**

Código: **MIA-CINT-01** Versión N° **8.5.0** Fecha: **23/08/2022** Página  54

|**Descripción**|**Para las impresoras: SRP812, DT230,**<br>**HKA80, P3100DL, PP9, ACLAS**<br>**PP9-PLUS, TD1140**|**Para las impresoras: SRP812, DT230,**<br>**HKA80, P3100DL, PP9, ACLAS**<br>**PP9-PLUS, TD1140**|**Para las impresoras: SRP812, DT230,**<br>**HKA80, P3100DL, PP9, ACLAS**<br>**PP9-PLUS, TD1140**|**Para las impresoras: SRP812, DT230,**<br>**HKA80, P3100DL, PP9, ACLAS**<br>**PP9-PLUS, TD1140**|**Para las impresoras: SRP812, DT230,**<br>**HKA80, P3100DL, PP9, ACLAS**<br>**PP9-PLUS, TD1140**||
|---|---|---|---|---|---|---|
||**Librería**||**Protocolo**<br>**Directo**||**L**||
||**Desde**|**Hasta**|**Desde**|**Hasta**|||
|**Status y Número de Cajero.**|0|3|0|3|4||
|**Subtotal de Ventas (Bs.)**|5|21|4|20|17||
|**Número de la Última Factura.**|23|30|21|28|8||
|**Cantidad de Facturas Emitidas en el día.**|32|36|29|33|5||
|**Número de la última nota de débito.**|38|45|34|41|8||
|**Cantidad de notas de débito del día.**|47|51|42|46|5||
|**Número de Última Nota de Crédito.**|53|60|47|54|8||
|**Cantidad de Notas de Crédito.**|62|66|55|59|5||
|**Número del Último Documento No Fiscal.**|68|75|60|67|8||
|**Cantidad de Documentos No Fiscales.**|77|81|68|72|5||
|**Contador de Cierres Diarios (Z).**|83|86|73|76|4||
|**Contador de Reportes de Memoria Fiscal.**|88|91|77|80|4||
|**RIF.**|93|103|81|91|11||
|**Número de Registro de la Máquina.**|105|114|92|101|10||
|**Hora Actual de la Impresora.**|116|121|102|107|6||
|**Fecha Actual de la Impresora.**|123|128|108|113|6||
|**Longitud Total.**|**129**||**113**||**129**||


Tabla 45. Comandos para consulta de status S1.

**The Factory HKA, C.A. VENEZUELA**

||**MANUAL DE PROTOCOLOS Y COMANDOS**<br>**V8.5.0**|Código:**MIA-CINT-01**|
|---|---|---|
|||Versión N°**8.5.0**|
||**INTEGRACIÓN**|Fecha:**23/08/2022**|
|||Página  55|


## **19.2. STATUS S2**

Este  comando  permite  consultar  información  referente  al  estado  de  la  Factura,  Nota  de  Crédito o  Nota  de  Débito  en  curso.  Si  es  ejecutado  y  no  existe  un  documento  abierto,  los  valores obtenidos  serán  cero.  Los  espacios  faltantes  en  la  columna  de  protocolo  directo  corresponden a los separadores **espacio y 0x0A.** Si solo falta un espacio corresponde al separador espacio.

|Descripción|**Para las impresoras: SRP350, HSP7000,**<br>**TD1125, HKA112, KUBE.**|**Para las impresoras: SRP350, HSP7000,**<br>**TD1125, HKA112, KUBE.**|**Para las impresoras: SRP350, HSP7000,**<br>**TD1125, HKA112, KUBE.**|**Para las impresoras: SRP350, HSP7000,**<br>**TD1125, HKA112, KUBE.**|**Para las impresoras: SRP350, HSP7000,**<br>**TD1125, HKA112, KUBE.**|**Para las impresoras: SRP812, DT230,**<br>**HKA80, P3100DL, PP9, ACLAS**<br>**PP9-PLUS, TD1140.**|**Para las impresoras: SRP812, DT230,**<br>**HKA80, P3100DL, PP9, ACLAS**<br>**PP9-PLUS, TD1140.**|**Para las impresoras: SRP812, DT230,**<br>**HKA80, P3100DL, PP9, ACLAS**<br>**PP9-PLUS, TD1140.**|**Para las impresoras: SRP812, DT230,**<br>**HKA80, P3100DL, PP9, ACLAS**<br>**PP9-PLUS, TD1140.**|**Para las impresoras: SRP812, DT230,**<br>**HKA80, P3100DL, PP9, ACLAS**<br>**PP9-PLUS, TD1140.**|
|---|---|---|---|---|---|---|---|---|---|---|
||**Librería**||**Protocolo**<br>**Directo**||**L**|**Librería**||**Protocolo**<br>**Directo**||**L**|
||**Desde**|**Hasta**|**Desde**|**Hasta**||**Desde**|**Hasta**|**Desde**|**Hasta**||
|**“S2”**|0|1|0|1|2|0|1|0|1|2|
|**Subtotal de bases**<br>**imponibles.***|3|15|3|15|*13|3|19|3|19|*17|
|**Subtotal de Impuesto.***|18|30|17|29|*13|22|39|21|37|*17|
|**Para uso futuro.***|33|45|31|43|*13|41|57|39|55|*17|
|**Cantidad de artículos.****|47|59|44|57|*13|59|75|56|72|*17|
|**Monto a Pagar.***|62|74|59|71|*13|78|94|74|90|*17|
|**Cantidad de pagos**<br>**realizados.***|76|79|72|75|4|96|99|91|94|4|
|**Tipo de Documento.***|81|81|76|76|1|101|101|95|95|1|
|**Longitud Total**|**82**||**76**||**82**|**102**||**95**||**102**|
|**Importante(*)**|**(11 enteros + 2 decimales)**|||||**(15 enteros + 2 decimales)**|||||
|**Nota**:**|El campo Tipo de Documento puede tomar los siguientes valores:<br>0 = No transacción           2 = En Nota de Crédito<br>1 = En Factura                   3 = En Nota de Débito||||||||||


Tabla 46. Comandos para consulta de status S2.

**The Factory HKA, C.A. VENEZUELA**

||**MANUAL DE PROTOCOLOS Y COMANDOS**<br>**V8.5.0**|Código:**MIA-CINT-01**|
|---|---|---|
|||Versión N°**8.5.0**|
||**INTEGRACIÓN**|Fecha:**23/08/2022**|
|||Página  56|


## **19.2.1. ESTRUCTURA DE LA TRAMA DEL STATUS S2E**

Éste  comando  permite  consultar  información  referente  a  los  acumulados  de  la  tasa  exenta  de  la transacción en curso.

|**Solo es admitido por las impresoras: SRP812, DT230,  HKA80, P3100DL, PP9, ACLAS PP9-PLUS, TD1140**|**Solo es admitido por las impresoras: SRP812, DT230,  HKA80, P3100DL, PP9, ACLAS PP9-PLUS, TD1140**|**Solo es admitido por las impresoras: SRP812, DT230,  HKA80, P3100DL, PP9, ACLAS PP9-PLUS, TD1140**|**Solo es admitido por las impresoras: SRP812, DT230,  HKA80, P3100DL, PP9, ACLAS PP9-PLUS, TD1140**|**Solo es admitido por las impresoras: SRP812, DT230,  HKA80, P3100DL, PP9, ACLAS PP9-PLUS, TD1140**|**Solo es admitido por las impresoras: SRP812, DT230,  HKA80, P3100DL, PP9, ACLAS PP9-PLUS, TD1140**|**Solo es admitido por las impresoras: SRP812, DT230,  HKA80, P3100DL, PP9, ACLAS PP9-PLUS, TD1140**|
|---|---|---|---|---|---|---|
|**Descripción**|**Libreria**||**Protocolo**<br>**Directo**||**L**|**Clase**|
||**Desde**|**Hasta**|**Desde**|**Hasta**|||
|**S2E**|0|1|0|1|2|ASCII|
|**Subtotal de ventas excepto* **|3|19|3|19|*17|ASCII|
|**Para uso futuro* **|22|39|21|37|*17|ASCII|
|**Para uso futuro* **|41|57|39|55|*17|ASCII|
|**Cantidad de artículos****|59|75|56|72|*17|ASCII|
|**Total a pagar* **|78|94|74|90|*17|ASCII|
|**Cantidad de pagos**|96|99|91|94|4|ASCII|
|**Tipos de documentos**|101|101|95|95|1|ASCII|
|**Longitud Total**|**102**||**95**||**102**||
|**NOTA(*):**Con el fag 63 confgurado en 1 o 3, los montos se expresaran( 15 + 2 )<br>Con el fag 63 confgurado diferente de 1 o 3, los montos se expresaran( 11 + 2 )<br>**NOTA(**)**:Con el fag 63 confgurado en 1 o 3, los montos se expresaran( 14 + 3 )<br>Con el Flag 63 confgurado diferente de 1 o 3, los montos se expresaran( 3 + 3 )|||||||


Tabla 47. Comandos para consulta de Status S2E.

**The Factory HKA, C.A. VENEZUELA**

||**MANUAL DE PROTOCOLOS Y COMANDOS**<br>**V8.5.0**|Código:**MIA-CINT-01**|
|---|---|---|
|||Versión N°**8.5.0**|
||**INTEGRACIÓN**|Fecha:**23/08/2022**|
|||Página  57|


## **19.2.2. ESTRUCTURA DE LA TRAMA DEL STATUS S21**

Este  comando  permite  consultar  información  referente  a  los  acumulados  de  la  tasa  1  de  la transacción en curso.

|**Solo es admitido por las impresoras: SRP812, DT230,  HKA80, P3100DL, PP9, ACLAS PP9-PLUS, TD1140**|**Solo es admitido por las impresoras: SRP812, DT230,  HKA80, P3100DL, PP9, ACLAS PP9-PLUS, TD1140**|**Solo es admitido por las impresoras: SRP812, DT230,  HKA80, P3100DL, PP9, ACLAS PP9-PLUS, TD1140**|**Solo es admitido por las impresoras: SRP812, DT230,  HKA80, P3100DL, PP9, ACLAS PP9-PLUS, TD1140**|**Solo es admitido por las impresoras: SRP812, DT230,  HKA80, P3100DL, PP9, ACLAS PP9-PLUS, TD1140**|**Solo es admitido por las impresoras: SRP812, DT230,  HKA80, P3100DL, PP9, ACLAS PP9-PLUS, TD1140**|**Solo es admitido por las impresoras: SRP812, DT230,  HKA80, P3100DL, PP9, ACLAS PP9-PLUS, TD1140**|
|---|---|---|---|---|---|---|
|**Descripción**|**Libreria**||**Protocolo**<br>**Directo**||**L**|**Clase**|
||**Desde**|**Hasta**|**Desde**|**Hasta**|||
|**S21**|0|1|0|1|2|ASCII|
|**Subtotal de ventas Tasa 1 ***|3|19|3|19|*17|ASCII|
|**Para uso futuro ***|22|39|21|37|*17|ASCII|
|**Para uso futuro ***|41|57|39|55|*17|ASCII|
|**Cantidad de artículos ****|59|75|56|72|*17|ASCII|
|**Total a pagar ***|78|94|74|90|*17|ASCII|
|**Cantidad de pagos**|96|99|91|94|4|ASCII|
|**Tipos de documentos**|101|101|95|95|1|ASCII|
|**Longitud Total**|**102**||**95**||**102**||
|**NOTA(*):**Con el fag 63 confgurado en 1 o 3, los montos se expresaran( 15 + 2 )<br>Con el fag 63 confgurado diferente de 1 o 3, los montos se expresaran( 11 + 2 )<br>**NOTA (**)**:Con el fag 63 confgurado en 1 o 3, los montos se expresaran( 14 + 3 )<br>Con el Flag 63 confgurado diferente de 1 o 3, los montos se expresaran( 3 + 3 )|||||||


Tabla 48. Comandos para consulta de Status S21.

**The Factory HKA, C.A. VENEZUELA**

||**MANUAL DE PROTOCOLOS Y COMANDOS**<br>**V8.5.0**|Código:**MIA-CINT-01**|
|---|---|---|
|||Versión N°**8.5.0**|
||**INTEGRACIÓN**|Fecha:**23/08/2022**|
|||Página  58|


## **19.2.3. ESTRUCTURA DE LA TRAMA DEL STATUS S22**

Este  comando  permite  consultar  información  referente  a  los  acumulados  de  la  tasa  2  de  la transacción en curso.

|**Solo  es  admitido  por  las  impresoras:  SRP812,  DT230,  HKA80,  P3100DL,  PP9,  ACLAS  PP9-PLUS,**<br>**TD1140**|**Solo  es  admitido  por  las  impresoras:  SRP812,  DT230,  HKA80,  P3100DL,  PP9,  ACLAS  PP9-PLUS,**<br>**TD1140**|**Solo  es  admitido  por  las  impresoras:  SRP812,  DT230,  HKA80,  P3100DL,  PP9,  ACLAS  PP9-PLUS,**<br>**TD1140**|**Solo  es  admitido  por  las  impresoras:  SRP812,  DT230,  HKA80,  P3100DL,  PP9,  ACLAS  PP9-PLUS,**<br>**TD1140**|**Solo  es  admitido  por  las  impresoras:  SRP812,  DT230,  HKA80,  P3100DL,  PP9,  ACLAS  PP9-PLUS,**<br>**TD1140**|**Solo  es  admitido  por  las  impresoras:  SRP812,  DT230,  HKA80,  P3100DL,  PP9,  ACLAS  PP9-PLUS,**<br>**TD1140**|**Solo  es  admitido  por  las  impresoras:  SRP812,  DT230,  HKA80,  P3100DL,  PP9,  ACLAS  PP9-PLUS,**<br>**TD1140**|
|---|---|---|---|---|---|---|
|**Descripción**|**Libreria**||**Protocolo Directo**||**L**|**Clase**|
||**Desde**|**Hasta**|**Desde**|**Hasta**|||
|**S22**|0|1|0|1|2|ASCII|
|**Subtotal de ventas Tasa 2 ***|3|19|3|19|*17|ASCII|
|**Para uso futuro ***|22|39|21|37|*17|ASCII|
|**Para uso futuro ***|41|57|39|55|*17|ASCII|
|**Cantidad de artículos ****|59|75|56|72|*17|ASCII|
|**Total a pagar ***|78|94|74|90|*17|ASCII|
|**Cantidad de pagos**|96|99|91|94|4|ASCII|
|**Tipos de documentos**|101|101|95|95|1|ASCII|
|**Longitud Total**|**102**||**95**||**102**||
|**NOTA(*):**Con el fag 63 confgurado en 1 o 3, los montos se expresaran( 15 + 2 )<br>Con el fag 63 confgurado diferente de 1 o 3, los montos se expresaran( 11 + 2 )<br>**NOTA(**): **Con el fag 63 confgurado en 1 o 3, los montos se expresaran( 14 + 3 )<br>Con el Flag 63 confgurado diferente de 1 o 3, los montos se expresaran( 3 + 3 )|||||||


Tabla 49. Comandos para consulta de Status S22.

**The Factory HKA, C.A. VENEZUELA**

**==> picture [95 x 43] intentionally omitted <==**

**MANUAL DE PROTOCOLOS Y COMANDOS** Código: **MIA-CINT-01 V8.5.0** Versión N° **8.5.0** Fecha: **23/08/2022 INTEGRACIÓN** Página  59

## **19.2.4. ESTRUCTURA DE LA TRAMA DEL STATUS S23**

Este  comando  permite  consultar  información  referente  a  los  acumulados  de  la  tasa  3  de  la transacción en curso.

|**Solo es admitido por las impresoras: SRP812, DT230,  HKA80, P3100DL, PP9, ACLAS PP9-PLUS, TD1140**|**Solo es admitido por las impresoras: SRP812, DT230,  HKA80, P3100DL, PP9, ACLAS PP9-PLUS, TD1140**|**Solo es admitido por las impresoras: SRP812, DT230,  HKA80, P3100DL, PP9, ACLAS PP9-PLUS, TD1140**|**Solo es admitido por las impresoras: SRP812, DT230,  HKA80, P3100DL, PP9, ACLAS PP9-PLUS, TD1140**|**Solo es admitido por las impresoras: SRP812, DT230,  HKA80, P3100DL, PP9, ACLAS PP9-PLUS, TD1140**|**Solo es admitido por las impresoras: SRP812, DT230,  HKA80, P3100DL, PP9, ACLAS PP9-PLUS, TD1140**|**Solo es admitido por las impresoras: SRP812, DT230,  HKA80, P3100DL, PP9, ACLAS PP9-PLUS, TD1140**|
|---|---|---|---|---|---|---|
|**Descripción**|**Libreria**||**Protocolo**<br>**Directo**||**L**|**Clase**|
||**Desde**|**Hasta**|**Desd**<br>**e**|**Hasta**|||
|**S23**|0|1|0|1|2|ASCII|
|**Subtotal de ventas Tasa 3 ***|3|19|3|19|*17|ASCII|
|**Para uso futuro* **|22|39|21|37|*17|ASCII|
|**Para uso futuro* **|41|57|39|55|*17|ASCII|
|**Cantidad de artículos ****|59|75|56|72|*17|ASCII|
|**Total a pagar ***|78|94|74|90|*17|ASCII|
|**Cantidad de pagos**|96|99|91|94|4|ASCII|
|**Tipos de documentos**|101|101|95|95|1|ASCII|
|**Longitud Total**|**102**||**95**||**102**||
|**NOTA(*): **Con el fag 63 confgurado en 1 o 3, los montos se expresaran (15+2)<br>Con el fag 63 confgurado diferente de 1 o 3, los montos se expresaran (11+2)<br>**NOTA(**): **Con el fag 63 confgurado en 1 o 3, los montos se expresaran (14+3)<br>Con el Flag 63 confgurado diferente de 1 o 3, los montos se expresaran (3+3)|||||||


Tabla 50. Comandos para consulta de Status S23.

**The Factory HKA, C.A. VENEZUELA**

**==> picture [95 x 43] intentionally omitted <==**

**MANUAL DE PROTOCOLOS Y COMANDOS** Código: **MIA-CINT-01 V8.5.0** Versión N° **8.5.0** Fecha: **23/08/2022 INTEGRACIÓN** Página  60

## **19.2.5. ESTRUCTURA DE LA TRAMA DEL STATUS S24**

Este  comando  permite  consultar  información  referente  a  los  acumulados  de  la  tasa  4  de  la transacción en curso.

|**Solo  es  admitido  por  las  impresoras:  SRP812,  DT230,  HKA80,  P3100DL,  PP9,  ACLAS  PP9-PLUS,**<br>**TD1140**|**Solo  es  admitido  por  las  impresoras:  SRP812,  DT230,  HKA80,  P3100DL,  PP9,  ACLAS  PP9-PLUS,**<br>**TD1140**|**Solo  es  admitido  por  las  impresoras:  SRP812,  DT230,  HKA80,  P3100DL,  PP9,  ACLAS  PP9-PLUS,**<br>**TD1140**|**Solo  es  admitido  por  las  impresoras:  SRP812,  DT230,  HKA80,  P3100DL,  PP9,  ACLAS  PP9-PLUS,**<br>**TD1140**|**Solo  es  admitido  por  las  impresoras:  SRP812,  DT230,  HKA80,  P3100DL,  PP9,  ACLAS  PP9-PLUS,**<br>**TD1140**|**Solo  es  admitido  por  las  impresoras:  SRP812,  DT230,  HKA80,  P3100DL,  PP9,  ACLAS  PP9-PLUS,**<br>**TD1140**|**Solo  es  admitido  por  las  impresoras:  SRP812,  DT230,  HKA80,  P3100DL,  PP9,  ACLAS  PP9-PLUS,**<br>**TD1140**|
|---|---|---|---|---|---|---|
|**Descripción**|**Libreria**||**Protocolo Directo**||**L**|**Clase**|
||**Desde**|**Hasta**|**Desde**|**Hasta**|||
|**S24**|0|1|0|1|2|ASCII|
|**Subtotal de ventas Percibido ***|3|19|3|19|*17|ASCII|
|**Para uso futuro ***|22|39|21|37|*17|ASCII|
|**Para uso futuro* **|41|57|39|55|*17|ASCII|
|**Cantidad de artículos ****|59|75|56|72|*17|ASCII|
|**Total a pagar* **|78|94|74|90|*17|ASCII|
|**Cantidad de pagos**|96|99|91|94|4|ASCII|
|**Tipos de documentos**|101|101|95|95|1|ASCII|
|**Longitud Total**|**102**||**95**||**102**||
|**NOTA (*):**Con el fag 63 confgurado en 1 o 3, los montos se expresaran<br>Con el fag 63 confgurado diferente de 1 o 3, los montos se expresaran<br>**NOTA (**): **Con el fag 63 confgurado en 1 o 3, los montos se expresaran<br>Con el Flag 63 confgurado diferente de 1 o 3, los montos se expresaran|||||||


Tabla 51. Comandos para consulta de Status S24.

**The Factory HKA, C.A. VENEZUELA**

**==> picture [95 x 43] intentionally omitted <==**

**MANUAL DE PROTOCOLOS Y COMANDOS** Código: **MIA-CINT-01 V8.5.0** Versión N° **8.5.0** Fecha: **23/08/2022 INTEGRACIÓN** Página  61

## **19.2.6. ESTRUCTURA DE LA TRAMA DEL STATUS S25**

Este  comando  permite  consultar  información  referente  al  estado  de  la  Factura,  Nota  de  Crédito o  Nota  de  Débito  en  curso.  Si  es  ejecutado  y  no  existe  un  documento  abierto,  los  valores obtenidos serán cero.

|**Solo  es  admitido  por  las  impresoras:  SRP812,  DT230,  HKA80,  P3100DL,  PP9,**<br>**ACLAS PP9-PLUS, TD1140**|**Solo  es  admitido  por  las  impresoras:  SRP812,  DT230,  HKA80,  P3100DL,  PP9,**<br>**ACLAS PP9-PLUS, TD1140**|**Solo  es  admitido  por  las  impresoras:  SRP812,  DT230,  HKA80,  P3100DL,  PP9,**<br>**ACLAS PP9-PLUS, TD1140**|**Solo  es  admitido  por  las  impresoras:  SRP812,  DT230,  HKA80,  P3100DL,  PP9,**<br>**ACLAS PP9-PLUS, TD1140**|**Solo  es  admitido  por  las  impresoras:  SRP812,  DT230,  HKA80,  P3100DL,  PP9,**<br>**ACLAS PP9-PLUS, TD1140**|**Solo  es  admitido  por  las  impresoras:  SRP812,  DT230,  HKA80,  P3100DL,  PP9,**<br>**ACLAS PP9-PLUS, TD1140**|
|---|---|---|---|---|---|
|**Descripción**|**Librería**||**Protocolo**<br>**Directo**||**L**|
||**Desde**|**Hasta**|**Desde**|**Hasta**||
|**S25**|0|1|0|1|2|
|**Subtotal de bases imponibles.**|3|19|3|19|*17|
|**Subtotal de Impuesto.**|22|39|21|37|*17|
|**Para uso futuro.**|41|57|39|55|*17|
|**Cantidad de artículos.**|59|75|56|72|*17|
|**Monto a Pagar.**|78|94|74|90|*17|
|**Cantidad de pagos realizados.**|96|99|91|94|4|
|**Tipo de Documento.**|101|101|95|95|1|
|**Longitud Total**|**102**||**95**||**102**|
|Tabla 52. Comandos para consulta de Status S25.||||||


**The Factory HKA, C.A. VENEZUELA**

**==> picture [95 x 43] intentionally omitted <==**

**MANUAL DE PROTOCOLOS Y COMANDOS** Código: **MIA-CINTV8.5.0** Versión N° **8.5.0** Fecha: **23/08/2022 INTEGRACIÓN** Página  62

## **19.3. STATUS S3**

Este  comando  permite  consultar  información  referente  a  la  configuración  de  las  tasas  de impuesto y flags.

|**Descripción**|**Para las impresoras: SRP350,**<br>**HSP7000, TD1125, HKA112, KUBE.**|**Para las impresoras: SRP350,**<br>**HSP7000, TD1125, HKA112, KUBE.**|**Para las impresoras: SRP350,**<br>**HSP7000, TD1125, HKA112, KUBE.**|**Para las impresoras: SRP350,**<br>**HSP7000, TD1125, HKA112, KUBE.**|**Para las impresoras: SRP350,**<br>**HSP7000, TD1125, HKA112, KUBE.**|**Para las impresoras: SRP812, DT230,**<br>**HKA80, P3100DL, PP9, ACLAS**<br>**PP9-PLUS, TD1140.**|**Para las impresoras: SRP812, DT230,**<br>**HKA80, P3100DL, PP9, ACLAS**<br>**PP9-PLUS, TD1140.**|**Para las impresoras: SRP812, DT230,**<br>**HKA80, P3100DL, PP9, ACLAS**<br>**PP9-PLUS, TD1140.**|**Para las impresoras: SRP812, DT230,**<br>**HKA80, P3100DL, PP9, ACLAS**<br>**PP9-PLUS, TD1140.**|**Para las impresoras: SRP812, DT230,**<br>**HKA80, P3100DL, PP9, ACLAS**<br>**PP9-PLUS, TD1140.**|
|---|---|---|---|---|---|---|---|---|---|---|
||**Librería**||**Protocolo**<br>**Directo**||**L**|**Librería**||**Protocolo**<br>**Directo**||**L**|
||**Desde**|**Hasta**|**Desde**|**Hasta**||**Desde**|**Hasta**|**Desde**|**Hasta**||
|**S3**|0|1|0|1|2|0|1|0|1|2|
|**Tipo de Tasa 1 (1= Incluido, 2=**<br>**Excluido)**|2|2|2|2|1|2|2|2|2|1|
|**Valor Tasa 1**|3|6|3|6|*4|3|6|3|6|*4|
|**Tipo de Tasa 2 (1= Incluido, 2=**<br>**Excluido)**|8|8|7|7|1|8|8|7|7|1|
|**Valor Tasa 2**|9|12|8|11|*4|9|12|8|11|*4|
|**Tipo de Tasa 3 ( 1= Incluido, 2=**<br>**Excluido)**|14|14|12|12|1|14|14|12|12|1|
|**Valor Tasa 3**|15|18|13|16|*4|15|18|13|16|*4|
|**Tipo IGTF**||||||20|20|17|17|1|
|**Valor IGTF**||||||21|24|18|21|*4|
|**Flag 00**|20|21|17|18|2|26|27|22|23|2|
|**…….**|…|…|…|…|…|…|…|…|..|..|
|**Flag 63 (Firmware Versión con montos**<br>**máximos)**|146|147|143|144|2|152|153|147|148|2|
|**Longitud Total**|**149**||**144**||**149**|**154**||**148**||**154**|
|**NOTA(*)**:|**2 enteros + 2 decimales**||||||||||
|**INFORMACIÒN:**<br>**-**La tasa 3 programada en 0 es considerada como percibido sólo para los modelos SRP350, SRP280, HSP7000, KUBE, HKA112, TD1125.<br>**-**La  tasa  4  (Percibido)  que  es  soportada  solo  para  las  impresoras  SRP812,  DT230,  HKA80,  PP9,  PP9-PLUS,  P3100DL,  TD1140  no<br>se<br>refeja en el Status S3 ya que la misma se guarda tal como el exento.<br>**-**Cuando se utiliza alguna de nuestras librerías: TfhkaIf.dll, IntTFHKA.exe y Tfnulx, no retornan el Separador 0x0A.|||||||||||


Tabla 53. Comandos para consulta de status S3.

**The Factory HKA, C.A. VENEZUELA**

**MANUAL DE PROTOCOLOS Y COMANDOS V8.5.0 INTEGRACIÓN**

**==> picture [95 x 43] intentionally omitted <==**

Código: **MIA-CINT-01** Versión N° **8.5.0** Fecha: **23/08/2022** Página  63

## **19.4. STATUS S4**

Este  comando  permite  extraer  información  referente  a  los  montos  acumulados  para  cada  medio de pago durante las ventas del día.

|**Descripción**|**Para las impresoras: SRP350,**<br>**HSP7000, TD1125, HKA112, KUBE.**|**Para las impresoras: SRP350,**<br>**HSP7000, TD1125, HKA112, KUBE.**|**Para las impresoras: SRP350,**<br>**HSP7000, TD1125, HKA112, KUBE.**|**Para las impresoras: SRP350,**<br>**HSP7000, TD1125, HKA112, KUBE.**|**Para las impresoras: SRP350,**<br>**HSP7000, TD1125, HKA112, KUBE.**|**Para las impresoras: SRP812, DT230,**<br>**HKA80, P3100DL, PP9, ACLAS**<br>**PP9-PLUS, TD1140.**|**Para las impresoras: SRP812, DT230,**<br>**HKA80, P3100DL, PP9, ACLAS**<br>**PP9-PLUS, TD1140.**|**Para las impresoras: SRP812, DT230,**<br>**HKA80, P3100DL, PP9, ACLAS**<br>**PP9-PLUS, TD1140.**|**Para las impresoras: SRP812, DT230,**<br>**HKA80, P3100DL, PP9, ACLAS**<br>**PP9-PLUS, TD1140.**|**Para las impresoras: SRP812, DT230,**<br>**HKA80, P3100DL, PP9, ACLAS**<br>**PP9-PLUS, TD1140.**|
|---|---|---|---|---|---|---|---|---|---|---|
||**Librería**||**Protocolo**<br>**Directo**||**L**|**Librería**||**Protocolo**<br>**Directo**||**L**|
||**Desde**|**Hasta**|**Desde**|**Hasta**||**Desde**|**Hasta**|**Desde**|**Hasta**||
|**S4**|0|1|0|1|2|0|1|0|1|2|
|**Medio de pago 1**|2|17|2|17|*16|3|19|3|19|*18|
|**Medio de pago 2**|19|34|18|33|*16|21|38|20|37|*18|
|**…**|…|…|…|…|…|…|…|…|…|…|
|**Medio de pago 24**|257|272|242|257|*16|439|456|416|433|*18|
|**Longitud Total**|**273**||**257**||**273**|**457**||**433**||**457**|
||Comando:**S4**||||||||||


Tabla 54. Comandos para consulta de status S4.

**The Factory HKA, C.A. VENEZUELA**

**==> picture [95 x 43] intentionally omitted <==**

**MANUAL DE PROTOCOLOS Y COMANDOS** Código: **MIA-CINT-01 V8.5.0** Versión N° **8.5.0** Fecha: **23/08/2022 INTEGRACIÓN** Página  64

## **19.5. STATUS S5**

Este comando permite consultar información referente al estado de la memoria de auditoría.

|||||||
|---|---|---|---|---|---|
|**Descripción**|**Librería**||**Protocolo**<br>**Directo**||**L**|
||**Desde**|**Hasta**|**Desde**|**Hasta**||
|**S5**|0|1|0|1|2|
|**RIF**|2|12|2|12|11|
|**Serial**|14|23|13|22|10|
|**Nùmero de la memoria de auditorìa**|25|28|23|26|4|
|**Capacidad en la memoria de auditorìa en MB**|30|33|27|30|4|
|**Espacio disponible en la memoria en MB**|35|38|31|34|4|
|**Nùmero de documentos registrados**|40|45|35|40|6|
|**Longitud Total**|**46**||**40**||**46**|
|Comando:**S5**||||||


Tabla 55. Comandos para consulta de status S5.

**The Factory HKA, C.A. VENEZUELA**

||**MANUAL DE PROTOCOLOS Y COMANDOS**<br>**V8.5.0**|Código:**MIA-CINT-01**|
|---|---|---|
|||Versión N°**8.5.0**|
||**INTEGRACIÓN**|Fecha:**23/08/2022**|
|||Página  65|


## **19.6. STATUS S8E**

Este  comando  permite  leer  la  información  de  los  datos  programados  en  las  líneas  del encabezado.

|**Descripción**|**Librería**|**Librería**|**Protocolo**<br>**Directo**|**Protocolo**<br>**Directo**|**L**|
|---|---|---|---|---|---|
||**Desde**|**Hasta**|**Desde**|**Hasta**||
|**S8E**|0|2|0|2|3|
|**Primera lìnea de encabezado**|3|42|3|42|40|
|**Segunda lìnea de encabezado**|44|83|43|82|40|
|**Tercera lìnea de encabezado**|85|124|83|122|40|
|**Cuarta lìnea de encabezado**|126|165|123|162|40|
|**Quinta lìnea de encabezado**|167|206|163|202|40|
|**Sexta lìnea de encabezado**|208|247|203|242|40|
|**Séptima lìnea de encabezado**|249|288|243|282|40|
|**Octava lìnea de encabezado**|290|329|283|322|40|
|**Longitud Total**|**330**||**322**||**330**|
|Comando:**S8E**||||||


Tabla 56. Comandos para consulta de status S8E.

**The Factory HKA, C.A. VENEZUELA**

||**MANUAL DE PROTOCOLOS Y COMANDOS**<br>**V8.5.0**|Código:**MIA-CINT-01**|
|---|---|---|
|||Versión N°**8.5.0**|
||**INTEGRACIÓN**|Fecha:**23/08/2022**|
|||Página  66|


## **19.7. STATUS S8P**

Este  comando  permite  leer  la  información  de  los  datos  programados  en  las  líneas  del  pie  de página.

|**Descripción**|**Librería**|**Librería**|**Protocolo**<br>**Directo**|**Protocolo**<br>**Directo**|**L**|
|---|---|---|---|---|---|
||**Desde**|**Hasta**|**Desde**|**Hasta**||
|**S8P**|0|2|0|2|3|
|**Primera lìnea de piè de pàgina**|3|42|3|42|40|
|**Segunda lìnea de piè de pàgina**|44|83|43|82|40|
|**Tercera lìnea de piè de pàgina**|85|124|83|122|40|
|**Cuarta lìnea de piè de pàgina**|126|165|123|162|40|
|**Quinta lìnea de piè de pàgina**|167|206|163|202|40|
|**Sexta lìnea de piè de pàgina**|208|247|203|242|40|
|**Séptima lìnea de piè de pàgina**|249|288|243|282|40|
|**Octava lìnea de pié de página**|290|329|283|322|40|
|**Longitud Total**|**330**||**322**||**330**|
|Comando:**S8P**||||||


Tabla 57. Comandos para consulta de status S8P.

**The Factory HKA, C.A. VENEZUELA**

||**MANUAL DE PROTOCOLOS Y COMANDOS**<br>**V8.5.0**|Código:**MIA-CINT-01**|
|---|---|---|
|||Versión N°**8.5.0**|
||**INTEGRACIÓN**|Fecha:**23/08/2022**|
|||Página  67|


## **19.8. STATUS SV**

Extrae información del país y modelo de la impresora fiscal.

|**Descripción**|**Comandos**|
|---|---|
|Z7C: Modelo HKA80<br>Z7A: Modelo HKA112<br>Z1A: Modelo SRP-270<br>Z1B: Modelo SRP-350<br>Z1E: Modelo SRP-280<br>Z1F: Modelo SRP-812<br>ZPA: Modelo HSP7000<br>Z6A: Modelo TALLY 1125<br>Z6B: Modelo DT-230<br>Z6C: Modelo TALLY 1140<br>ZYA: Modelo P3100DL<br>ZZH: Modelo PP9<br>ZZP : Modelo PP9-PLUS<br>VE: Venezuela|**SV**|


Tabla 58. Comandos para status SV.

## **20. IMPRIMIR REPORTES**

|**Descripción**|**Descripción**|**Comandos**|
|---|---|---|
|Reporte X||**I0X**|
|Reporte X2||**I1X**|
|Borrar acumulado del reporte X2||**X1X**|
|Reporte de cierre diario Z||**I0Z**|
|Reporte Z2||**I1Z**|
|Borrar acumulado del reporte Z2||**X1Z**|
|**Atención:**|Cuando se envía el (comando I0Z) para imprimir un reporte Z<br>es necesario esperar unos segundos hasta la emisión del<br>"reporte de estado de transmisión" para proceder a enviar<br>Un nuevo comando. (20 seg aprox)||
|**Importante:**|**Z**: Una vez procesada la información se debe esperar un<br>tiempo de 3 segundos (aproximadamente) mientras emite<br>tickets del DNF.<br>**X:**Una vez procesada la información se debe esperar un<br>tiempo de 3 segundos (aproximadamente) mientras emite<br>tickets del DNF.||


Tabla 59. Comandos para impresión de reportes.

**The Factory HKA, C.A. VENEZUELA**

||**MANUAL DE PROTOCOLOS Y COMANDOS**<br>**V8.5.0**|Código:**MIA-CINT-01**|
|---|---|---|
|||Versión N°**8.5.0**|
||**INTEGRACIÓN**|Fecha:**23/08/2022**|
|||Página  68|


## **20.1. IMPRIMIR REPORTE DE MEMORIA FISCAL POR NÚMERO**

Este comando permite imprimir un reporte fiscal definido entre dos números.

|**Descripción**|**Comandos**|
|---|---|
|Se incluye toda la información de los reportes|**I3A000001000005**|
|Un resumen del total de los reportes|**I3S000001000005**|
|Un reporte mensual del conjunto de reportes|**I3M000001000005**|
|||
|Impresión por rango de número (Inicio: 4 Dígitos y Fin: 4 Dígitos)||


Tabla 60. Comandos para impresión de reportes por número.

## **20.2. IMPRIMIR REPORTE DE MEMORIA FISCAL POR FECHA**

Este comando permite imprimir un reporte fiscal definido entre dos fechas..

|**Descripción**|**Comandos**|
|---|---|
|Se incluye toda la información de los reportes|**I2A300622010722**|
|Un resumen del total de los reportes|**I2S300622010722**|
|Un reporte mensual del conjunto de reportes|**I2M300622010722**|
|||
|Impresión por rango de fecha (Inicio: 6 Dígitos y Fin: 6 Dígitos) DDMMYY||


Tabla 61. Comandos para impresión de reportes por fecha.

**The Factory HKA, C.A. VENEZUELA**

||**MANUAL DE PROTOCOLOS Y COMANDOS**<br>**V8.5.0**|Código:**MIA-CINT-01**|
|---|---|---|
|||Versión N°**8.5.0**|
||**INTEGRACIÓN**|Fecha:**23/08/2022**|
|||Página  69|


## **21. EXTRACCIÓN DE REPORTES**

Este  comando  extrae  la  información  de  las  ventas  actuales.  Las  tramas  devueltas  que  se muestran en esta sección corresponden a la impresoras tomando en cuenta el flag 63.

## **21.1. REPORTE X**

|**Descripción**|**Para las impresoras: SRP350, HSP7000,**<br>**TD1125, HKA112, KUBE.**|**Para las impresoras: SRP350, HSP7000,**<br>**TD1125, HKA112, KUBE.**|**Para las impresoras: SRP350, HSP7000,**<br>**TD1125, HKA112, KUBE.**|**Para las impresoras: SRP350, HSP7000,**<br>**TD1125, HKA112, KUBE.**|**Para las impresoras: SRP350, HSP7000,**<br>**TD1125, HKA112, KUBE.**|
|---|---|---|---|---|---|
||**Librería**||**Protocolo**<br>**Directo**||**L**|
||**Desde**|**Hasta**|**Desde**|**Hasta**||
|**Número del próximo reporte Z**|0|3|0|3|4|
|**Fecha del último reporte Z emitido**|5|10|4|9|6|
|**Número de la última factura emitida**|12|19|10|17|8|
|**Fecha de emisión de la última factura**|21|26|18|23|6|
|**Hora de emisión de la última factura**|28|31|24|27|4|
|**Acumulado exento**|33|45|28|40|*13|
|**Acumulado Base Imponible Tasa 1**|47|59|41|53|*13|
|**Acumulado Impuesto Tasa 1**|61|73|54|66|*13|
|**Acumulado Base Imponible Tasa 2**|75|87|67|79|*13|
|**Acumulado Impuesto Tasa 2**|89|101|80|92|*13|
|**Acumulado Base Imponible Tasa 3**|103|115|93|105|*13|
|**Acumulado Imponible Tasa 3**|117|129|106|118|*13|
|**Acumulado exento Nota de Crédito**|131|143|119|131|*13|
|**Acumulado Base Imponible Tasa 1 Nota de Crédito**|145|157|132|144|*13|
|**Acumulado Imponible Tasa 1 Nota de Crédito**|159|171|145|157|*13|
|**Acumulado Base Imponible Tasa 2 Nota de Crédito**|173|185|158|170|*13|


**The Factory HKA, C.A. VENEZUELA**

|||**MANUAL DE PROTOCOLOS Y COMANDOS**<br>**V8.5.0**|**MANUAL DE PROTOCOLOS Y COMANDOS**<br>**V8.5.0**|**MANUAL DE PROTOCOLOS Y COMANDOS**<br>**V8.5.0**|**MANUAL DE PROTOCOLOS Y COMANDOS**<br>**V8.5.0**|Código:**MIA-CINT-01**|Código:**MIA-CINT-01**|Código:**MIA-CINT-01**|
|---|---|---|---|---|---|---|---|---|
|||||||Versión N°**8.5.0**|||
|||**INTEGRACIÓN**||||Fecha:**23/08/2022**|||
|||||||Página  70|||
||||||||||
|||||||183<br>*13<br>196<br>*13<br>209<br>*13<br>217<br>8<br>**217**<br>**242**|||
||**Acumulado Imponible Tasa 2 Nota de Crédito**||187|199|171||183|*13|
||**Acumulado Base Imponible Tasa 3 Nota de Crédito**||201|213|184||196|*13|
||**Acumulado Imponible Tasa 3 Nota de Crédito**||215|227|197||209|*13|
||**Número de la última nota de crédito**||229|241|210||217|8|
||**Longitud Total**||**242**|||**217**||**242**|
||Comando:**U0X**||||||||


Tabla 62. Comandos para extracción de reporte X.

|**Descripción**|**Para las impresoras: SRP812, DT230,**<br>**HKA80, P3100DL, PP9, ACLAS**<br>**PP9-PLUS, TD1140.**|**Para las impresoras: SRP812, DT230,**<br>**HKA80, P3100DL, PP9, ACLAS**<br>**PP9-PLUS, TD1140.**|**Para las impresoras: SRP812, DT230,**<br>**HKA80, P3100DL, PP9, ACLAS**<br>**PP9-PLUS, TD1140.**|**Para las impresoras: SRP812, DT230,**<br>**HKA80, P3100DL, PP9, ACLAS**<br>**PP9-PLUS, TD1140.**|**Para las impresoras: SRP812, DT230,**<br>**HKA80, P3100DL, PP9, ACLAS**<br>**PP9-PLUS, TD1140.**|
|---|---|---|---|---|---|
||**Librería**||**Protocolo**<br>**Directo**||**L**|
||**Desde**|**Hasta**|**Desde**|**Hasta**||
|**Número del próximo reporte Z**|0|3|0|3|4|
|**Fecha del último reporte Z emitido**|5|10|4|9|6|
|**Hora del último reporte Z emitido**|12|15|10|13|4|
|**Número de la última factura emitida**|17|24|14|21|8|
|**Fecha de emisión de la última factura**|26|31|22|27|6|
|**Hora de emisión de la última factura**|33|36|28|31|4|
|**Número de la última nota de crédito**|38|45|32|39|8|
|**Número de la última nota de débito**|47|54|40|47|8|
|**Número del último documento no fscal**|56|63|48|55|8|
|**Acumulado exento**|65|82|56|73|*18|
|**Acumulado Base Imponible Tasa 1**|84|101|74|91|*18|
|**Acumulado Impuesto Tasa 1**|103|120|92|109|*18|


**The Factory HKA, C.A. VENEZUELA**

|||**MANUAL DE PROTOCOLOS Y COMANDOS**<br>**V8.5.0**|**MANUAL DE PROTOCOLOS Y COMANDOS**<br>**V8.5.0**|**MANUAL DE PROTOCOLOS Y COMANDOS**<br>**V8.5.0**|**MANUAL DE PROTOCOLOS Y COMANDOS**<br>**V8.5.0**|Código:**MIA-CINT-01**|Código:**MIA-CINT-01**|
|---|---|---|---|---|---|---|---|
|||||||Versión N°**8.5.0**||
|||**INTEGRACIÓN**||||Fecha:**23/08/2022**||
|||||||Página  71||
|||||||||
|||||||127<br>*18<br>145<br>*18<br>163<br>*18<br>181<br>*18<br>199<br>*18<br>217<br>*18<br>235<br>*18<br>253<br>*18<br>271<br>*18<br>289<br>*18<br>307<br>*18<br>325<br>*18<br>343<br>*18<br>361<br>*18<br>379<br>*18<br>397<br>*18<br>415<br>*18<br>433<br>*18<br>451<br>*18<br>469<br>*18<br>487<br>*18<br>505<br>*18<br>523<br>*18<br>541<br>*18||
||**Acumulado Base Imponible Tasa 2**||122|139|110|127|*18|
||**Acumulado Impuesto Tasa 2**||141|158|128|145|*18|
||**Acumulado Base Imponible Tasa 3**||160|177|146|163|*18|
||**Acumulado Imponible Tasa 3**||179|196|164|181|*18|
||**Acumulado exento Nota de Débito**||198|215|182|199|*18|
||**Acumulado Base Imponible Tasa 1 Nota de Débito**||217|234|200|217|*18|
||**Acumulado Imponible Tasa 1 Nota de Débito**||236|253|218|235|*18|
||**Acumulado Base Imponible Tasa 2 Nota de Débito**||255|272|236|253|*18|
||**Acumulado Imponible Tasa 2 Nota de Débito**||274|291|254|271|*18|
||**Acumulado Base Imponible Tasa 3 Nota de Débito**||293|310|272|289|*18|
||**Acumulado Imponible Tasa 3 Nota de Débito**||312|329|290|307|*18|
||**Acumulado exento Nota de Crédito**||331|348|308|325|*18|
||**Acumulado Base Imponible Tasa 1 Nota de Crédito**||350|367|326|343|*18|
||**Acumulado Imponible Tasa 1 Nota de Crédito**||369|386|344|361|*18|
||**Acumulado Base Imponible Tasa 2 Nota de Crédito**||388|405|362|379|*18|
||**Acumulado Imponible Tasa 2 Nota de Crédito**||407|424|380|397|*18|
||**Acumulado Base Imponible Tasa 3 Nota de Crédito**||426|443|398|415|*18|
||**Acumulado Imponible Tasa 3 Nota de Crédito**||445|462|416|433|*18|
||**Acumulado Base Imponible IGTF**||464|481|434|451|*18|
||**Acumulado Impuesto Percibido Ventas.**||483|500|452|469|*18|
||**Acumulado Impuesto Percibido Débito.**||502|519|470|487|*18|
||**Acumulado Impuesto Percibido Crédito.**||521|538|488|505|*18|
||**Valor IGTF**||540|557|506|523|*18|
||**Acumulado Base Imponible IGTF Nota de Crédito**||559|576|524|541|*18|


**The Factory HKA, C.A. VENEZUELA**

|||**MANUAL DE PROTOCOLOS Y COMANDOS**<br>**V8.5.0**|**MANUAL DE PROTOCOLOS Y COMANDOS**<br>**V8.5.0**|**MANUAL DE PROTOCOLOS Y COMANDOS**<br>**V8.5.0**|**MANUAL DE PROTOCOLOS Y COMANDOS**<br>**V8.5.0**|Código:**MIA-CINT-01**|Código:**MIA-CINT-01**|
|---|---|---|---|---|---|---|---|
|||||||Versión N°**8.5.0**||
|||**INTEGRACIÓN**||||Fecha:**23/08/2022**||
|||||||Página  72||
|||||||||
|||||||||
||**Valor IGTF Nota de Crédito**||578|595|542|559|*18|
||**Acumulado Base Imponible IGTF Nota de Débito**||597|614|560|577|*18|
||**Valor IGTF Nota de Débito**||616|633|578|595|*18|
||**Longitud Total**||**634**||**595**||**634**|
||Comando:**U0X**|||||||


Tabla 63. Comandos para extracción de reporte X.

## **21.2. REPORTE Z**

|**Descripción**|**Para las impresoras: SRP350, HSP7000,**<br>**TD1125, HKA112, KUBE.**|**Para las impresoras: SRP350, HSP7000,**<br>**TD1125, HKA112, KUBE.**|**Para las impresoras: SRP350, HSP7000,**<br>**TD1125, HKA112, KUBE.**|**Para las impresoras: SRP350, HSP7000,**<br>**TD1125, HKA112, KUBE.**|**Para las impresoras: SRP350, HSP7000,**<br>**TD1125, HKA112, KUBE.**|
|---|---|---|---|---|---|
||**Librería**||**Protocolo**<br>**Directo**||**L**|
||**Desde**|**Hasta**|**Desde**|**Hasta**||
|**Número del próximo reporte Z**|0|3|0|3|4|
|**Fecha del último reporte Z emitido**|5|10|4|9|6|
|**Número de la última factura emitida**|12|19|10|17|8|
|**Fecha de emisión de la última factura**|21|26|18|23|6|
|**Hora de emisión de la última factura**|28|31|24|27|4|
|**Acumulado exento**|33|45|28|40|*13|
|**Acumulado Base Imponible Tasa 1**|47|59|41|53|*13|
|**Acumulado Impuesto Tasa 1**|61|73|54|66|*13|
|**Acumulado Base Imponible Tasa 2**|75|87|67|79|*13|
|**Acumulado Impuesto Tasa 2**|89|101|80|92|*13|
|**Acumulado Base Imponible Tasa 3**|103|115|93|105|*13|
|**Acumulado Imponible Tasa 3**|117|129|106|118|*13|
|**Acumulado exento Nota de Crédito**|131|143|119|131|*13|


**The Factory HKA, C.A. VENEZUELA**

**==> picture [95 x 43] intentionally omitted <==**

## **MANUAL DE PROTOCOLOS Y COMANDOS V8.5.0 INTEGRACIÓN**

Código: **MIA-CINT-** Versión N° **8.5.0** Fecha: **23/08/2022** Página  73

|**Acumulado Base Imponible Tasa 1 Nota de Crédito**|145|157|132|144|*13|
|---|---|---|---|---|---|
|**Acumulado Imponible Tasa 1 Nota de Crédito**|159|171|145|157|*13|
|**Acumulado Base Imponible Tasa 2 Nota de Crédito**|173|185|158|170|*13|
|**Acumulado Imponible Tasa 2 Nota de Crédito**|187|199|171|183|*13|
|**Acumulado Base Imponible Tasa 3 Nota de Crédito**|201|213|184|196|*13|
|**Acumulado Imponible Tasa 3 Nota de Crédito**|215|227|197|209|*13|
|**Número de la última nota de crédito**|229|241|210|217|8|
|**Longitud Total**|**242**||**217**||**242**|
|Comando:**U0Z**||||||


Tabla 64. Comandos para extracción de reporte Z.

|**Descripción**|**Para las impresoras: SRP812, DT230,**<br>**HKA80, P3100DL, PP9, ACLAS**<br>**PP9-PLUS, TD1140.**|**Para las impresoras: SRP812, DT230,**<br>**HKA80, P3100DL, PP9, ACLAS**<br>**PP9-PLUS, TD1140.**|**Para las impresoras: SRP812, DT230,**<br>**HKA80, P3100DL, PP9, ACLAS**<br>**PP9-PLUS, TD1140.**|**Para las impresoras: SRP812, DT230,**<br>**HKA80, P3100DL, PP9, ACLAS**<br>**PP9-PLUS, TD1140.**|**Para las impresoras: SRP812, DT230,**<br>**HKA80, P3100DL, PP9, ACLAS**<br>**PP9-PLUS, TD1140.**|
|---|---|---|---|---|---|
||**Librería**||**Protocolo**<br>**Directo**||**L**|
||**Desde**|**Hasta**|**Desde**|**Hasta**||
|**Número del próximo reporte Z**|0|3|0|3|4|
|**Fecha del último reporte Z emitido**|5|10|4|9|6|
|**Hora del último reporte Z emitido**|12|15|10|13|4|
|**Número de la última factura emitida**|17|24|14|21|8|
|**Fecha de emisión de la última factura**|26|31|22|27|6|
|**Hora de emisión de la última factura**|33|36|28|31|4|
|**Número de la última nota de crédito**|38|45|32|39|8|
|**Número de la última nota de débito**|47|54|40|47|8|
|**Número del último documento no fscal**|56|63|48|55|8|


**The Factory HKA, C.A. VENEZUELA**

||**MANUAL DE PROTOCOLOS Y COMANDOS**<br>**V8.5.0**|Código:**MIA-CINT-01**|
|---|---|---|
|||Versión N°**8.5.0**|
||**INTEGRACIÓN**|Fecha:**23/08/2022**|
|||Página  74|


|**Acumulado exento**|65|82|56|73|*18|
|---|---|---|---|---|---|
|**Acumulado Base Imponible Tasa 1**|84|101|74|91|*18|
|**Acumulado Impuesto Tasa 1**|103|120|92|109|*18|
|**Acumulado Base Imponible Tasa 2**|122|139|110|127|*18|
|**Acumulado Impuesto Tasa 2**|141|158|128|145|*18|
|**Acumulado Base Imponible Tasa 3**|160|177|146|163|*18|
|**Acumulado Imponible Tasa 3**|179|196|164|181|*18|
|**Acumulado exento Nota de Débito**|198|215|182|199|*18|
|**Acumulado Base Imponible Tasa 1 Nota de Débito**|217|234|200|217|*18|
|**Acumulado Imponible Tasa 1 Nota de Débito**|236|253|218|235|*18|
|**Acumulado Base Imponible Tasa 2 Nota de Débito**|255|272|236|253|*18|
|**Acumulado Imponible Tasa 2 Nota de Débito**|274|291|254|271|*18|
|**Acumulado Base Imponible Tasa 3 Nota de Débito**|293|310|272|289|*18|
|**Acumulado Imponible Tasa 3 Nota de Débito**|312|329|290|307|*18|
|**Acumulado exento Nota de Crédito**|331|348|308|325|*18|
|**Acumulado Base Imponible Tasa 1 Nota de Crédito**|350|367|326|343|*18|
|**Acumulado Imponible Tasa 1 Nota de Crédito**|369|386|344|361|*18|
|**Acumulado Base Imponible Tasa 2 Nota de Crédito**|388|405|362|379|*18|
|**Acumulado Imponible Tasa 2 Nota de Crédito**|407|424|380|397|*18|
|**Acumulado Base Imponible Tasa 3 Nota de Crédito**|426|443|398|415|*18|
|**Acumulado Imponible Tasa 3 Nota de Crédito**|445|462|416|433|*18|
|**Acumulado Base Imponible IGTF**|464|481|434|451|*18|
|**Acumulado Impuesto Percibido Ventas.**|483|500|452|469|*18|
|**Acumulado Impuesto Percibido Débito.**|502|519|470|487|*18|


**The Factory HKA, C.A. VENEZUELA**

||**MANUAL DE PROTOCOLOS Y COMANDOS**<br>**V8.5.0**|Código:**MIA-CINT-01**|
|---|---|---|
|||Versión N°**8.5.0**|
||**INTEGRACIÓN**|Fecha:**23/08/2022**|
|||Página  75|


|**Acumulado Impuesto Percibido Crédito.**|521|538|488|505|*18|
|---|---|---|---|---|---|
|**Valor IGTF**|540|557|506|523|*18|
|**Acumulado Base Imponible IGTF Nota de Crédito**|559|576|524|541|*18|
|**Valor IGTF Nota de Crédito**|578|595|542|559|*18|
|**Acumulado Base Imponible IGTF Nota de Débito**|597|614|560|577|*18|
|**Valor IGTF Nota de Débito**|616|633|578|595|*18|
|**Longitud Total**|**634**||**595**||**634**|
|Comando:**U0Z**||||||


Tabla 65. Comandos para extracción de reporte Z.

## **22. EXTRACCIÓN DE REPORTES DE LA MEMORIA DE AUDITORIA**

## **22.1. EXTRACCIÓN POR RANGO DE NÚMERO**

Este comando permite subir los reportes de memoria por un rango de números.

|**Descripción**|**Comandos**|
|---|---|
|Se incluye toda la información de los reportes|**U3A000001000005**|
|Un resumen del total de los reportes|**U3S000001000005**|
|Un reporte mensual del conjunto de reportes|**U3M000001000005**|
|||
|Impresión por rango de número (Inicio: 4 Dígitos y Fin: 4 Dígitos)||


Tabla 66. Comandos para extracción de reportes por número.

## **22.2. EXTRACCIÓN POR FECHA**

Este comando permite subir los reportes de memoria por rango de fecha.

|**Descripción**|**Comandos**|
|---|---|
|Se incluye toda la información de los reportes|**U2A300622010722**|
|Un resumen del total de los reportes|**U2S300622010722**|
|Un reporte mensual del conjunto de reportes|**U2M300622010722**|
|||


**The Factory HKA, C.A. VENEZUELA**

**MANUAL DE PROTOCOLOS Y COMANDOS** Código: **MIA-CINT-01 V8.5.0** Versión N° **8.5.0** Fecha: **23/08/2022 INTEGRACIÓN** Página  76

**==> picture [95 x 43] intentionally omitted <==**

Impresión por rango de fecha (Inicio: 6 Dígitos y Fin: 6 Dígitos) DDMMYY

Tabla 67. Comandos para extracción de reportes por fecha.

## **22.3. EXTRACCIÓN DETALLADA POR DOCUMENTO**

Este comando permite subir la información detallada de los reportes acumulados.

|**Descripción**|**Comandos**|
|---|---|
|Extrae los acumulados de las ventas|**U0X4**|
|Extrae los acumuladores de las notas de crédito|**U0X5**|
|Extrae los acumuladores de las notas de débito|**U0X6**|
|Devuelve la misma estructura que el comando S1|**U0X7**|


Tabla 68. Comandos para extracción de reportes por documentos.

## **22.4. RESUMEN DE LAS ESTRUCTURAS DE LAS TRAMAS (S1 - S2)**

|**Impresoras**|**S1**||**S2**|**S2**|**S2**|**S2**|**S2**|**S2**|**S2**|**S2**|
|---|---|---|---|---|---|---|---|---|---|---|
||||**FLAG 63**||||||||
||**FLAGS 63**||**00**|**01**|**02**|**03**|**16**|**17**|**18**|**19**|
||**Longitud**||**Longitud**||||||||
|**SRP-812**|131||77|104|77|104|77|104|77|104|
|**HKA-80**|131||77|104|77|104|77|104|77|104|
|**DT-230**|131||77|104|77|104|77|104|77|104|
|**PP9**|131||77|104|77|104|77|104|77|104|
|**PP9 PLUS**|131||77|104|77|104|77|104|77|104|
|**P3100DL**|131||77|104|77|104|77|104|77|104|
|**SRP-350**|116||77|84|77|77|-|-|-|-|
|**HKA-112**|116||77|84|77|77|-|-|-|-|
|**HSP7000**|116||77|84|77|77|-|-|-|-|
|**TALLY 1125**|116||77|84|77|77|-|-|-|-|
|**TALLY 1140**|131||77|104|77|104|77|104|77|104|
|**KUBE**|116||77|84|77|77|-|-|-|-|
|**SRP-280**|116||77|84|77|77|-|-|-|-|


Tabla 69. Resumen de las estructuras de las Tramas.

**The Factory HKA, C.A. VENEZUELA**

**==> picture [95 x 43] intentionally omitted <==**

**MANUAL DE PROTOCOLOS Y COMANDOS** Código: **MIA-CINT-01 V8.5.0** Versión N° **8.5.0** Fecha: **23/08/2022 INTEGRACIÓN** Página  77

## **22.5. RESUMEN DE LAS ESTRUCTURAS DE LAS TRAMAS (S3 - S4 - S5)**

|**Impresoras**|**S3**|**S3**|**S3**|**S3**|**S3**|**S3**|**S3**|**S3**|**S4**|**S4**|**S4**|**S4**|**S4**|**S4**|**S4**|**S4**|**S5**|
|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|
||<br>**FLAG 63**||||||||**FLAG 63**||||||||**FLAG 63**|
||<br>**00**|**01**|**02**|**03**|**16**|**17**|**18**|**19**|**00**|**01**|**02**|**03**|**16**|**17**|**18**|**19**||
||**Longitud**||||||||**Longitud**||||||||**Longitud**|
|**SRP-812**|150|150|150|150|156|156|156|156|339|459|339|459|339|459|339|459|<br>48|
|**HKA-80**|150|150|150|150|156|156|156|156|339|459|339|459|339|459|339|459|<br>48|
|**DT-230**|150|150|150|150|156|156|156|156|339|459|339|459|339|459|339|459|<br>48|
|**PP9**|150|150|150|150|156|156|156|156|339|459|339|459|339|459|339|459|<br>48|
|**Aclas PP9**<br>**PLUS**|150|150|150|150|156|156|156|156|339|459|339|459|339|459|339|459|<br>48|
|**P3100DL**|150|150|150|150|156|156|156|156|339|459|339|459|339|459|339|459|<br>48|
|**SRP-350**|122|150|122|122|-|-|-|-|179|275|179|179|-|-|-|-|48|
|**HKA-112**|142|150|142|142|-|-|-|-|179|275|179|179|-|-|-|-|48|
|**HSP7000**|122|150|122|122|-|-|-|-|179|275|179|179|-|-|-|-|48|
|**TALLY 1125**|122|150|122|122|-|-|-|-|179|275|179|179|-|-|-|-|48|
|**TALLY 1140**|150|150|150|150|156|156|156|156|339|459|339|459|339|459|339|459|<br>48|
|**KUBE**|122|150|122|122|-|-|-|-|179|275|179|179|-|-|-|-|48|
|**SRP-280**|122|150|122|122|-|-|-|-|179|275|179|179|-|-|-|-|48|


Tabla 70. Resumen de las estructuras de las Tramas.

**The Factory HKA, C.A. VENEZUELA**

**==> picture [95 x 43] intentionally omitted <==**

**MANUAL DE PROTOCOLOS Y COMANDOS** Código: **MIA-CINT-01 V8.5.0** Versión N° **8.5.0** Fecha: **23/08/2022 INTEGRACIÓN** Página  78

## **22.6. RESUMEN DE LAS ESTRUCTURAS DE LAS TRAMAS (X,Z)**

|**Impresoras**|**REPORTE X**|**REPORTE X**|**REPORTE X**|**REPORTE X**|**REPORTE X**|**REPORTE X**|**REPORTE X**|**REPORTE X**|**REPORTE Z**|**REPORTE Z**|**REPORTE Z**|**REPORTE Z**|**REPORTE Z**|**REPORTE Z**|**REPORTE Z**|**REPORTE Z**|
|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|
||**FLAG 63**||||||||**FLAG 63**||||||||
||**00**|**01**|**02**|**03**|**16**|**17**|**18**|**19**|**00**|**01**|**02**|**03**|**16**|**17**|**18**|**19**|
||**Longitud**||||||||**Longitud**||||||||
|**SRP-812**|362|467|419|524|533|638|533|638|362|467|419|524|533|638|533|638|
|**HKA-80**|362|362|362|362|467|467|467|467|362|362|362|362|467|467|467|467|
|**DT-230**|362|467|419|524|533|638|533|638|362|467|419|524|533|638|533|638|
|**PP9**|362|467|419|524|533|638|533|638|362|467|419|524|533|638|533|638|
|**PP9 PLUS**|362|467|419|524|533|638|533|638|362|467|419|524|533|638|533|638|
|**P3100DL**|362|467|419|524|533|638|533|638|362|467|419|524|533|638|533|638|
|**SRP-350**|119|241|199|199|-|-|-|-|119|241|199|199|-|-|-|-|
|**HKA-112**|241|241|241|241|-|-|-|-|241|241|241|241|-|-|-|-|
|**HSP7000**|119|241|199|199|-|-|-|-|119|241|199|199|-|-|-|-|
|**TALLY 1125**|199|241|199|199|-|-|-|-|199|241|199|199|-|-|-|-|
|**TALLY 1140**|362|467|419|524|533|638|533|638|362|467|419|524|533|638|533|638|
|**KUBE**|199|241|199|199|-|-|-|-|199|241|199|199|-|-|-|-|
|**SRP-280**|204|246|204|204|-|-|-|-|204|246|204|204|-|-|-|-|


Tabla 71. Resumen de las estructuras de las Tramas.

**The Factory HKA, C.A. VENEZUELA**

**MANUAL DE PROTOCOLOS Y COMANDOS V8.5.0**

**INTEGRACIÓN**

**==> picture [95 x 43] intentionally omitted <==**

Código: **MIA-CINT-01** Versión N° **8.5.0** Fecha: **23/08/2022** Página  79

## **23. TABLA DE FLAG DE CONFIGURACIÓN DEL USUARIO**

|**Flag**|**Descripción**|
|---|---|
|**21**|00= El precio unitario del producto se interpreta como 8 enteros y 2 decimales.<br>01= El precio unitario del producto se interpreta como 7 enteros y 3 decimales.<br>02= El precio unitario del producto se interpreta como 6 enteros y 4 decimales.<br>11= El precio unitario del producto se interpreta como 9 enteros y 1 decimal.<br>12= El precio unitario del producto se interpreta como 10 enteros sin decimales.<br>30= El precio unitario del producto se interpreta como 14 enteros y 2 decimales.|
|**30**|00= Imprime el Código de Barra sin el número asociado.<br>01= Imprime el Código de Barra con el número asociado|
|**43**|Tipo de código de barras soportados, defne el tipo de código de barra a emplear<br>00= EAN 13<br>01= ITF<br>02=CODE 128<br>03=CODE 39<br>**Códigos 2D soportados**<br>04=QR<br>05=PD|
|**50**|00= NO se habilita el uso del IGTF. No permite el uso de los medios de pagos del<br>20 al 24 (reservados para los cálculos e impresión del impuesto IGTF).<br>01= Se habilita el uso del IGTF. Activa el uso de los medios de pagos del 20 al 24 y<br>la ejecución del cálculo e impresión del impuesto IGTF.|
|**63**|00= Conserva las mismas estructuras de respuesta manejadas en la versión con<br>montos reducidos.<br>01= Activa las estructuras de respuesta ampliadas para extracción de reportes y<br>estatus.<br>02= Conserva las mismas estructuras de respuesta manejadas en la versión con<br>montos reducidos y se adiciona la tasa con valor percibido.<br>03=Activa las estructuras de respuesta ampliadas con el valor percibido.<br>16= Conserva las mismas estructuras de respuesta manejadas en la versión con<br>montos reducidos, SI se adiciona el valor IGTF y la tasa con valor percibido.<br>17= Activa las estructuras de respuesta ampliadas para extracción de reportes y<br>estatus, SI se adiciona el valor IGTF y la tasa con valor percibido.<br>18= Conserva las mismas estructuras de respuesta manejadas en la versión con<br>montos reducidos, SI se adiciona el valor IGTF y la tasa con valor percibido.<br>19= Activa las estructuras de respuesta ampliadas para extracción de reportes y<br>estatus, SI se adiciona el valor IGTF y la tasa con valor percibido.|


Tabla 72. Flag de Configuración de Usuario.

**The Factory HKA, C.A. VENEZUELA**

**MANUAL DE PROTOCOLOS Y COMANDOS V8.5.0 INTEGRACIÓN**

**==> picture [95 x 43] intentionally omitted <==**

Código: **MIA-CINT-01** Versión N° **8.5.0** Fecha: **23/08/2022** Página  80

## **24. CONFIGURACIÓN DEL IMPUESTO IGTF**

1.  En  el  proceso  de  configuración  para  trabajar  con  el  nuevo  impuesto  IGTF  deberá  realizar  la programación  del  valor  indicado  por  el  SENIAT  (3%)  usando  los  comandos  de  programación de tasas de impuesto. (ver Tabla.19).

2.  Flag  50:  En  el  valor  00  no  se  permite  el  uso  de  los  medios  de  pagos  del  20  al  24  reservados

para  divisas  que  no  sean  de  curso  legal  en  el  país,  y  no  se  efectúan  cálculos  que  contemplen  el impuesto  IGTF.  En  el  valor  01  se  habilita  el  uso  de  los  medios  de  pagos  del  20  al  24  y  la  máquina fiscal ejecutará el cálculo e impresión del impuesto IGTF, acorde a las disposiciones del SENIAT.

3. Para  totalizar  un  documento  en  divisas  y  hacer  uso  del  IGTF  se  deberá  emitir  por  cualquiera de  los  medios  de  pagos  entre  el  20  y  24  (PAGO  EN  DIVISAS)  y  tendrá  que  estar  habilitado  el flag 50 en 01.

4.  Se  admiten  pagos  parciales  en  divisas  y  moneda  nacional  para  el  uso  del  valor  IGTF,  solo  si el flag 50 está en 01.

5.  Es  de  uso  obligatorio  el  comando  199  para  cerrar  todos  los  documentos  fiscales  (Factura  de Venta, Nota Crédito, Nota Débito) cuando el flag 50 está en 01.

6.  Si  no  requiere  hacer  uso  de  pagos  en  divisas  y  no  hacer  uso  del  IGTF  bastará  con  enviar cualquiera  de  los  medios  de  pago  entre  el  01  y  el  19  (PAGO  EN  MONEDA  NACIONAL).  Debe tomarse  en  cuenta  que  cuando  el  flag  50  esté  en  00  se  bloquearán  los  medios  de  pago  del 20 al 24, ya que son de uso exclusivo del modo IGTF.

Es  importante  tomar  en  cuenta  que  al  usar  el **Status(S2** )  consultara  la  información  referente  al estado  de  la  Factura,  Nota  Crédito  o  Nota  de  Débito  en  curso.  Si  es  ejecutado  y  no  existe  una Factura,  Nota  de  Crédito  o  Nota  de  Débito  abierta,  los  valores  obtenidos  serán  cero,  es  muy  útil para evitar redondeos entre el sistema administrativo y la impresora fiscal. . (ver Tabla 46 ).

**The Factory HKA, C.A. VENEZUELA**

**MANUAL DE PROTOCOLOS Y COMANDOS V8.5.0**

**==> picture [95 x 43] intentionally omitted <==**

**INTEGRACIÓN**

Código: **MIA-CINT-01** Versión N° **8.5.0** Fecha: **23/08/2022** Página  81

|**Escenarios**|**Cálculos**|
|---|---|
|Cuando  el  pago  de  la  factura  es  efectuado  en  su<br>totalidad  en  divisas,  y  ese  monto  cancelado  por  el<br>cliente  supera  el  monto  total  refejado  en  la  factura,  el<br>cálculo  del  IGTF  será  sobre  todo  el  monto  total  a  pagar<br>del documento.|Base Imponible: 100 Bs<br>IVA 16%: 16 Bs<br>Subtotal: 100 + 16= 116 Bs<br>Pago en Divisa = 130 Bs<br>**IGTF:**116 * 3% =  3.48 Bs<br>Total a pagar: 119.48 Bs<br>Cambio: 10.52 Bs|
|Cuando  la  cancelación  de  la  deuda  es  efectuada  en  su<br>totalidad  en  divisas,  el  cálculo  del  IGTF  será  sobre  todo<br>el monto a pagar del documento fscal.|Base Imponible: 100 Bs<br>IVA 16%: 16 Bs<br>Subtotal: 100 + 16= 116 Bs<br>Pago en Divisa = 116 Bs<br>**IGTF:**116 * 3% =  3.48 Bs<br>Total a pagar: 119.48 Bs|
|Cuando  la  cancelación  de  la  deuda  es  efectuada<br>parcialmente  en  divisas,  el  cálculo  del  IGTF  será  sobre<br>ese monto parcial del documento fscal.|Base Imponible: 100 Bs<br>IVA 16%: 16 Bs<br>Subtotal: 100 + 16= 116 Bs<br>Pago en Divisa = 110 Bs<br>**IGTF:**110 * 3% =  3.3 Bs<br>Total a pagar: 119.3 Bs|


Tabla 73. CONFIGURACIÓN DEL IMPUESTO IGTF

**The Factory HKA, C.A. VENEZUELA**

||**MANUAL DE PROTOCOLOS Y COMANDOS**<br>**V8.5.0**|Código:**MIA-CINT-01**|
|---|---|---|
|||Versión N°**8.5.0**|
||**INTEGRACIÓN**|Fecha:**23/08/2022**|
|||Página  82|


## **25. SUGERENCIAS DE PROGRAMACIÓN PARA DESARROLLAR SU SISTEMA**

Esta sección hace referencia a la forma en la que el sistema administrativo o de facturación se comunica con la impresora fiscal. Tome en consideración los siguientes puntos:

## **¿Cuáles son las causas comunes que pueden generar error de comunicación con su sistema?**

Los errores comunes a los que debe estar atento son:

- Impresora apagada o desconectada: emplee el método _CheckFprinter()_ luego de abrir el puerto de comunicación si su sistema usa una de nuestras APIs.

- Configuración errónea de los puertos COM.

- Tasas de los productos no se encuentran programadas (deben programarse para poder enviar un producto). Solicite el estatus S3 para comprobación de las tasas.

- La impresora se encuentra en medio de una transacción fiscal, para ello compruebe el **status & error** de la impresora fiscal, emplee los métodos _ReadFpStatus()_ o _GetPrinterStatus()_ si su sistema usa uno de nuestros componentes de integración o el envío del comando 0x05 por el puerto serial en caso de usar el protocolo directo y lea la respuesta de la impresora basada en las tablas de Status y Error.

- Verificar si falta papel en la impresora a través de la variable de **error** .

- La lectura de las variables de **status & error** , es útil emplearla cuando el equipo está imprimiendo, sobre todo en los equipos que imprimen lento (ACLAS PP9, equipos matriz de punto, P3100DL), ya que si la impresora no ha terminado de imprimir está ocupada o en medio de una transacción fiscal y no puede procesar ciertos comandos, puede emplear un ciclo de espera que lea constantemente el **status** de la impresora y una vez se encuentre en estado “ _en espera_ ”, código de status 4 (cuatro) o 1 (uno) si usa nuestras APIs, status 0x40 o 0x60 si usa protocolo directo, en éste momento es posible enviar los siguientes comandos a la impresora fiscal.

## **¿Qué debe hacer al momento de iniciar el sistema?**

- Debe verificar la comunicación con la impresora, emplee el método _CheckFprinter()_ si su sistema usa una de nuestras APIs.

- Lea los status informativos (S1, S3, S5) y verifique los datos de la impresora referentes a: Tasas, Fecha, Hora, Serial, RIF, número de la última factura, número de la última nota de crédito y débito, número del último Reporte Z, cantidad de Reportes Z almacenados en la memoria fiscal, capacidad de la memoria de auditoria.

**The Factory HKA, C.A. VENEZUELA**

**==> picture [95 x 43] intentionally omitted <==**

**MANUAL DE PROTOCOLOS Y COMANDOS** Código: **MIA-CINT-01 V8.5.0** Versión N° **8.5.0** Fecha: **23/08/2022 INTEGRACIÓN** Página  83

## **¿Qué debe hacer cuando envíe comandos a la impresora fiscal?**

- Debe verificar primero si el puerto de comunicación con la impresora fiscal se encuentra abierto, luego chequee comunicación con la impresora a través del método _CheckFprinter()_ si su sistema usa una de nuestras APIs.

- Asegúrese de que la información esté en la impresora antes de procesarla en el sistema.

## **¿Qué debe hacer para evitar errores de redondeo entre el sistema y la impresora fiscal?**

- Realice consultas de Status S2 durante las transacciones (en medio de los pagos parciales) para comparar los cálculos del sistema administrativo con los de la impresora y realizar posibles ajustes de redondeo antes de cerrar y emitir el documento, de esta forma se lleva un control del monto que queda por pagar, emplee los métodos _GetS2PrinterData_ (), _UploadStatusCmd(Status Long, Error Long, String cmd, String file) o UploadStatusDin(Status As Long, Error As Long, cmd As String, Cadena As String)_ si su sistema usa una de nuestras APIs y lea el monto por pagar entre cada pago parcial.

## **Otras recomendaciones que debe tener en cuenta durante la integración son:**

- Utilice un programa Monitor de Puerto Serial para verificar las tramas enviadas y las respuestas de la impresora observando así el intercambio de información entre el sistema y la impresora. Con ésta herramienta es posible determinar las causas de los errores que pueden presentarse durante la integración de los sistemas de facturación con nuestras impresoras fiscales.

- Se recomienda el manejo de la impresora en un solo “thread” sincronizado.

**The Factory HKA, C.A. VENEZUELA**

||**MANUAL DE PROTOCOLOS Y COMANDOS**<br>**V8.5.0**|Código:**MIA-CINT-01**|
|---|---|---|
|||Versión N°**8.5.0**|
||**INTEGRACIÓN**|Fecha:**23/08/2022**|
|||Página  84|


## **26. TEST PARA AUTOEVALUAR INTEGRACIÓN DE SISTEMA ADMINISTRATIVO**

A continuación se encuentra una guía de prueba para autoevaluar si su sistema cumple con una integración exitosa:

|**Inicio del sistema (Utilizar Monitor de Puerto Serial)**|**Inicio del sistema (Utilizar Monitor de Puerto Serial)**|**Inicio del sistema (Utilizar Monitor de Puerto Serial)**|**Inicio del sistema (Utilizar Monitor de Puerto Serial)**|
|---|---|---|---|
|**Prueba**||**Resultado**|**Observaciones**|
|1|Verifcar que el_puerto de comunicación_se<br>está abriendo correctamente|||
|2|Verifcar que se está chuequeando la<br>_conexión con la impresora_|||
|3|Verifcar el valor de las variables de<br>_Status&Error_|||
|4|Verifcar que se están solicitando los_status_<br>_S1,S3,S5_para control interno del sistema|||
|5|Verifcar si su sistema lee el modelo de<br>impresora que está conectada (comando<br>SV)|||
|**Generación de facturas**||||
|**Prueba**||**Resultado**|**Observaciones**|
|6|Factura con datos de cliente: Rif, Razón<br>social, Información adicional )|||
|7|Factura con comentario|||
|8|Factura con corrección de ítem|||
|9|Factura con descuento sobre un ítem|||
|10|Factura con recargo sobre un ítem|||
|11|Factura que imprima el subtotal|||
|12|Factura con descuento sobre el subtotal|||
|13|Factura con recargo sobre el subtotal|||


**The Factory HKA, C.A. VENEZUELA**

**==> picture [95 x 43] intentionally omitted <==**

**MANUAL DE PROTOCOLOS Y COMANDOS** Código: **MIA-CINTV8.5.0** Versión N° **8.5.0** Fecha: **23/08/2022 INTEGRACIÓN** Página  85

|14|Factura con código de barras|||
|---|---|---|---|
|15|Factura con pago directo|||
|16|Factura con pagos parciales (mínimo 5<br>pagos)|||
|**Generación de Notas de Crédito**||||
|**Prueba**||**Resultado**|**Observaciones**|
|17|Nota de crédito con datos de cliente: Rif,<br>Razón social, #Fact afectada, fecha fact.<br>Afectada, serial de impresora, Información<br>adicional )|||
|18|Nota de crédito con comentario|||
|19|Nota de crédito con corrección de ítem|||
|20|Nota de crédito con descuento sobre un<br>ítem|||
|21|Nota de crédito con recargo sobre un ítem|||
|22|Nota de crédito que imprima el subtotal|||
|23|Nota de crédito con descuento sobre el<br>subtotal|||
|24|Nota de crédito con recargo sobre el<br>subtotal|||
|25|Nota de crédito con código de barras|||
|26|Nota de crédito con pago directo|||
|27|Nota de crédito con pagos parciales<br>(mínimo 5 pagos)|||
|28|Verifcar que se imprima la descripción<br>“NOTA DE CRÉDITO”|||
|**Generación de Notas de Débito (solo impresoras que aplica)**||||
|**Prueba**||**Resultado**|**Observaciones**|


**The Factory HKA, C.A. VENEZUELA**

**==> picture [95 x 43] intentionally omitted <==**

**MANUAL DE PROTOCOLOS Y COMANDOS** Código: **MIA-CINTV8.5.0** Versión N° **8.5.0** Fecha: **23/08/2022 INTEGRACIÓN** Página  86

|29|Nota de débito con datos de cliente: Rif,<br>Razón social, #Fact afectada, fecha fact.<br>Afectada, serial de impresora, Información<br>adicional )|||
|---|---|---|---|
|30|Nota de débito con comentario|||
|31|Nota de débito con corrección de ítem|||
|32|Nota de débito con descuento sobre un<br>ítem|||
|33|Nota de débito con recargo sobre un ítem|||
|34|Nota de débito que imprima el subtotal|||
|35|Nota de débito con descuento sobre el<br>subtotal|||
|36|Nota de débito con código de barras|||
|37|Nota de débito con pago directo|||
|38|Nota de débito con pagos parciales<br>(mínimo 5 pagos)|||
|39|Verifcar que se imprima la descripción<br>“NOTA DE DÉBITO”|||
|**Generación de documento de texto**||||
|**Prueba**||**Resultado**|**Observaciones**|
|40|Documento de texto no fscal con una<br>descripción específca, donde se apliquen<br>los diferentes efectos soportados por cada<br>impresora (negrita, centrado, expandido,<br>etc.)|||
|41|Documento de texto no fscal con código<br>de barras en el cuerpo del documento (solo<br>en las impresoras que aplique)|||
|**Fondo, retiro de caja y documento de programación**||||


**The Factory HKA, C.A. VENEZUELA**

**==> picture [95 x 43] intentionally omitted <==**

**MANUAL DE PROTOCOLOS Y COMANDOS** Código: **MIA-CINTV8.5.0** Versión N° **8.5.0** Fecha: **23/08/2022 INTEGRACIÓN** Página  87

|**Prueba**|**Prueba**|**Resultado**|**Observaciones**|
|---|---|---|---|
|42|Imprimir un documento no fscal “Fondo de<br>Caja”|||
|43|Imprimir un documento no fscal “Retiro de<br>Caja”|||
|44|Imprimir documento de programación de la<br>impresora fscal|||
|**Reportes**||||
|**Prueba**||**Resultado**|**Observaciones**|
|45|Imprimir reporte X|||
|46|Imprimir reporte X2 (si está implementado)|||
|47|Imprimir reporte Z2 (si está implementado)|||
|48|Imprimir reporte Z|||
|49|Imprimir reporte de memoria fscal por<br>número en formato completo y resumen|||
|50|Imprimir reporte de memoria fscal por<br>fecha en formato completo y resumen|||
|51|Imprimir reporte de memoria fscal<br>mensual|||
|52|Extraer último reporte Z generado (para ello<br>debe solicitar un S1 y leer el número del<br>último reporte z generado)|||
|**Reimpresión de documentos de la memoria de auditoria**||||
|**Prueba**||**Resultado**|**Observaciones**|
|53|Reimprimir facturas por rango de número|||
|54|Reimprimir notas de crédito por rango de<br>número|||


**The Factory HKA, C.A. VENEZUELA**

**==> picture [95 x 43] intentionally omitted <==**

**MANUAL DE PROTOCOLOS Y COMANDOS** Código: **MIA-CINTV8.5.0** Versión N° **8.5.0** Fecha: **23/08/2022 INTEGRACIÓN** Página  88

|55|Reimprimir notas de débito por rango de<br>número (si aplica)|||
|---|---|---|---|
|56|Reimprimir reportes Z por rango de número|||
|57|Reimprimir facturas por rango de fecha|||
|58|Reimprimir notas de crédito por rango de<br>fecha|||
|59|Reimprimir notas de débito por rango de<br>fecha (si aplica)|||
|60|Reimprimir reportes Z por rango de fecha|||
|**Extracción de documentos de la memoria de auditoria**||||
|**Prueba**||**Resultado**|**Observaciones**|
|61|Extraer facturas por rango de número|||
|62|Extraer notas de crédito por rango de<br>número|||
|63|Extraer notas de débito por rango de<br>número (si aplica)|||
|64|Extraer reportes Z por rango de número|||
|65|Extraer facturas por rango de fecha|||
|66|Extraer notas de crédito por rango de fecha|||
|67|Extraer notas de débito por rango de fecha<br>(si aplica)|||
|68|Extraer reportes Z por rango de fecha|||
|**Pruebas de rutina**||||
|**Prueba**||**Resultado**|**Observaciones**|
|69|Iniciar una factura, debe hacer lo siguiente:|||


**The Factory HKA, C.A. VENEZUELA**

**MANUAL DE PROTOCOLOS Y COMANDOS** Código: **MIA-CINTV8.5.0** Versión N° **8.5.0** Fecha: **23/08/2022 INTEGRACIÓN** Página  89

**==> picture [95 x 43] intentionally omitted <==**

|70|Registrar producto asociado a la tasa<br>exenta|||
|---|---|---|---|
|71|Registrar producto asociado a la tasa<br>general|||
|72|Registrar producto asociado a la tasa<br>reducida|||
|73|Registrar producto asociado a la tasa<br>adicional|||
|74|Solicitar el subtotal en pantalla o impreso|||
|75|Obtener el monto por pagar a través del<br>status S2|||
|76|Verifcar que el monto por pagar de la<br>impresora coincida con el monto por pagar<br>que se lleva en sistema, caso contrario<br>realizar el ajuste de redondeo en el<br>sistema.|||
|77|Realizar un pago parcial con el 25% del<br>subtotal (debe quedar abierta la factura)|||
|78|Obtener el monto por pagar a través del<br>status S2 (debe observarse el 75% del<br>subtotal)|||
|79|Verifcar que el monto por pagar de la<br>impresora coincida con el monto por pagar<br>que se lleva en sistema, caso contrario<br>realizar el ajuste de redondeo en el<br>sistema.|||
|80|Realizar un pago parcial con el 25% del<br>subtotal (debe quedar abierta la factura)|||
|81|Obtener el monto por pagar a través del<br>status S2 (debe observarse el 50% del<br>subtotal)|||


**The Factory HKA, C.A. VENEZUELA**

**MANUAL DE PROTOCOLOS Y COMANDOS** Código: **MIA-CINTV8.5.0** Versión N° **8.5.0** Fecha: **23/08/2022 INTEGRACIÓN** Página  90

**==> picture [95 x 43] intentionally omitted <==**

|82|Verifcar que el monto por pagar de la<br>impresora coincida con el monto por pagar<br>que se lleva en sistema, caso contrario<br>realizar el ajuste de redondeo en el<br>sistema.|||
|---|---|---|---|
|83|Realizar un pago parcial con el 50% del<br>subtotal (debe cerrarse la factura)|||
|84|Esperar a que se imprima la factura y la<br>impresora esté nuevamente disponible<br>(Status 1,4 ó 0x40,0x60)|||
|85|Solicitar status S1, leer el número de la<br>última factura para su registro en la base<br>de datos|||
|86|Iniciar una factura, debe hacer lo siguiente:|||
|87|Registrar producto asociado a la tasa<br>exenta|||
|88|Registrar producto asociado a la tasa<br>general|||
|89|Registrar producto asociado a la tasa<br>reducida|||
|90|Registrar producto asociado a la tasa<br>adicional|||
|91|Anular la factura abierta o en curso|||
|92|Esperar a que se imprima la factura<br>anulada y la impresora esté nuevamente<br>disponible (Status 1,4 ó 0x40,0x60)|||
|93|Iniciar una factura, debe hacer lo siguiente:|||
|94|Registrar producto asociado a la tasa<br>exenta|||
|95|Registrar producto asociado a la tasa<br>general|||


**The Factory HKA, C.A. VENEZUELA**

**MANUAL DE PROTOCOLOS Y COMANDOS** Código: **MIA-CINTV8.5.0** Versión N° **8.5.0** Fecha: **23/08/2022 INTEGRACIÓN** Página  91

**==> picture [95 x 43] intentionally omitted <==**

|96|Registrar producto asociado a la tasa<br>reducida|||
|---|---|---|---|
|97|Registrar producto asociado a la tasa<br>adicional|||
|98|Totalizar el monto total de la factura con el<br>medio de pago N° 10|||
|99|Esperar a que se imprima la factura<br>anulada y la impresora esté nuevamente<br>disponible (Status 1,4 ó 0x40,0x60)|||
|100|Solicitar status S1, leer el número de la<br>última factura para su registro en la base<br>de datos|||
|101|Generar la nota de crédito de la factura<br>anterior|||
|102|Esperar a que se imprima la nota de crédito<br>y la impresora esté nuevamente disponible<br>(Status 1,4 o 0x40,0x60)|||
|103|Iniciar una factura, debe hacer lo siguiente:|||
|104|Registrar producto asociado a la tasa<br>exenta|||
|105|Registrar producto asociado a la tasa<br>general|||
|106|Registrar producto asociado a la tasa<br>reducida|||
|107|Registrar producto asociado a la tasa<br>adicional|||
|108|Totalizar el monto total de la factura con el<br>medio de pago N° 5|||
|109|Solicitar status S1, leer el número de la<br>última factura para su registro en la base<br>de datos|||


**The Factory HKA, C.A. VENEZUELA**

||**MANUAL DE PROTOCOLOS Y COMANDOS**<br>**V8.5.0**|Código:**MIA-CINT-01**|
|---|---|---|
|||Versión N°**8.5.0**|
||**INTEGRACIÓN**|Fecha:**23/08/2022**|
|||Página  92|


|110|Generar la nota de débito de la factura<br>anterior (si aplica para la impresora)|||
|---|---|---|---|
|111|Esperar a que se imprima la nota de crédito<br>y la impresora esté nuevamente disponible<br>(Status 0,4 o 0x40,0x60)|||
|112|Generar Reporte X2 (si está implementado)|||
|113|Generar reporte X|||
|114|Generar Reporte Z|||


Tabla 74. Test de Autoevaluación.

**The Factory HKA, C.A. VENEZUELA**
