# Manual Técnico de Usuario

## 1. Introducción

Bienvenido al **Servidor API de Impresión Fiscal**. Este software ha sido diseñado para simplificar y optimizar la manera en que su sistema de facturación o punto de venta (POS) se comunica con las impresoras fiscales.

*   **¿Qué problema resuelve?** Facilita la emisión de documentos fiscales (facturas, notas de crédito, notas de débito) directamente desde sus aplicaciones de negocio, asegurando que se cumplan los requisitos técnicos y legales de las autoridades tributarias.
*   **¿Cómo funciona?** Actúa como un intermediario inteligente (un "middleware"). Su sistema de facturación envía la información del documento a este servidor API en un formato estándar. El servidor se encarga de traducir esta información a los comandos específicos que entiende su impresora fiscal y gestiona todo el proceso de impresión. Esto le ahorra la complejidad de tener que programar directamente para cada modelo de impresora fiscal y le asegura que los documentos se generen correctamente.

## 2. Requisitos del Sistema

*   **Sistema Operativo:** Microsoft Windows (versiones compatibles serán especificadas por su proveedor).
*   **Tipo de Aplicación:** El Servidor API de Impresión Fiscal se distribuye como un **programa ejecutable único** (un archivo `.exe`). Esto significa que **no requiere un proceso de instalación complejo**. Simplemente necesita el archivo ejecutable para funcionar.
*   **Recursos:** El programa es ligero y no consume una cantidad significativa de recursos del sistema.

## 3. Ejecución y Configuración Inicial

Dado que el Servidor API de Impresión Fiscal es un programa ejecutable, no hay un proceso de "instalación" tradicional. Siga estos pasos para ponerlo en marcha:

1.  **Obtenga el Ejecutable:** Asegúrese de tener el archivo ejecutable (`.exe`) proporcionado por su proveedor.
2.  **Ubicación (Recomendado):** Copie el archivo ejecutable a una carpeta dedicada en su equipo (por ejemplo, `C:\ApiPrinterFiscal\`).
3.  **Ejecución Manual:** Puede iniciar el programa haciendo doble clic en el archivo ejecutable.
4.  **Funcionamiento en Bandeja del Sistema:** Una vez iniciado, el programa se ejecutará discretamente en segundo plano. Usualmente, encontrará un icono representativo en la bandeja del sistema (cerca del reloj de Windows). Esto indica que el servidor está activo y listo para recibir solicitudes de impresión, sin interferir con sus otras tareas.
    *   (Espacio para captura de pantalla del icono en la bandeja del sistema)
5.  **Inicio Automático con Windows (Recomendado):** Para asegurar que el servidor de impresión esté siempre disponible cuando encienda su equipo, se recomienda configurarlo para que se inicie automáticamente:
    *   Puede crear un acceso directo al archivo ejecutable.
    *   Luego, copie este acceso directo en la carpeta "Inicio" de Windows. (Puede acceder a ella escribiendo `shell:startup` en el diálogo "Ejecutar" de Windows - Tecla Windows + R).
    *   (Espacio para captura de pantalla mostrando cómo agregar al inicio)

## 4. Primeros Pasos: El Panel de Control de Escritorio

El Servidor API de Impresión Fiscal se administra desde su propio **panel de control de escritorio** (no desde el navegador). Al iniciar el programa, la ventana del panel aparece automáticamente; también puede reabrirla en cualquier momento desde el icono de la bandeja del sistema:

1.  **Icono de la bandeja del sistema:** Haga clic derecho (o doble clic izquierdo) sobre el icono del programa en la bandeja del sistema.
2.  **"Abrir Panel":** Seleccione esta opción del menú para mostrar la ventana principal.
    *   (Espacio para captura de pantalla del menú de la bandeja)
3.  **Panel Principal:** La ventana muestra pestañas para Consola/Logs, Configuración del Servidor y Configuración Fiscal.
    *   (Espacio para captura de pantalla del Panel Principal)

Adicionalmente, existe una página web de **solo lectura** para monitoreo remoto — ver sección 6.

## 6. Interfaz de Usuario: Panel de Control y Dashboard Web

*   **Panel de Control (aplicación de escritorio):**
    *   **Pestaña Consola / Logs:**
        *   Visualización en vivo del archivo de log del día.
        *   Acciones rápidas: Imprimir Reporte X, Imprimir Reporte Z.
        *   Envío de comandos fiscales directos (para uso técnico).
        *   (Espacio para captura de pantalla de la pestaña Consola)
    *   **Pestaña Configuración del Servidor:**
        *   Host, Puerto, Modo Debug, Modo Servidor (SPOOLER/PROXY), orígenes permitidos.
        *   Proxy: Habilitar Proxy, URL Destino.
        *   Impresora Fiscal: Habilitar, Modelo, Puerto (con escaneo automático), Velocidad (Baudrate), Timeout.
        *   Logging: Salida a Consola, Archivo de Log, Nivel de Log, Formato, Días de Retención.
        *   Seguridad: Código de Seguridad.
        *   (Espacio para captura de pantalla de la pestaña Configuración del Servidor)
        *   Botón "Guardar Configuración del Servidor" aplica los cambios sin reiniciar el programa.
    *   **Pestaña Configuración Fiscal:**
        *   Datos de la impresora (modelo, serial, nombre de nota) y formato del documento (qué campos incluir en el encabezado y pie fiscal).
        *   (Espacio para captura de pantalla de la pestaña Configuración Fiscal)
        *   Botón "Guardar Plantilla Fiscal" aplica los cambios de inmediato.
*   **Dashboard Web (`http://localhost:5051`, solo lectura):**
    *   Muestra el estado del servidor y de la impresora fiscal, útil para monitoreo remoto.
    *   No permite realizar acciones (reportes, comandos, configuración) — esas se hacen únicamente desde el Panel de Control.
    *   (Espacio para captura de pantalla del Dashboard Web)

## 7. Opciones Generales y Funcionalidades

El Servidor API de Impresión Fiscal ofrece varias funcionalidades clave para la gestión de su impresora fiscal:

*   **Impresión de Documentos Fiscales:** Su función principal es procesar las solicitudes de su sistema de facturación para imprimir Facturas, Notas de Crédito y Notas de Débito.
*   **Impresión de Reportes Fiscales:**
    *   **Reporte X:** Este reporte proporciona un corte parcial de las ventas y operaciones realizadas por la impresora fiscal desde el último Reporte Z. Es útil para arqueos de caja durante el día. Puede solicitarlo desde la pestaña Consola del Panel de Control.
    *   **Reporte Z:** Este es un reporte de cierre diario que totaliza todas las operaciones realizadas por la impresora fiscal y usualmente reinicia los acumuladores para el siguiente día fiscal. Es un documento fiscal importante y obligatorio en muchas jurisdicciones. Puede solicitarlo desde la pestaña Consola del Panel de Control.
    *   (Espacio para captura de pantalla de los botones de Reporte X y Z)
*   **Modos de Operación (Configurable por el administrador del sistema):**
    *   **Modo API (Predeterminado):** En este modo, el servidor se conecta directamente a la impresora fiscal conectada a su equipo y gestiona todo el proceso de impresión.
    *   **Modo Proxy:** En este modo, el servidor actúa como un intermediario que reenvía las solicitudes de impresión a otro servidor de impresión fiscal (que podría estar en otra máquina o ser un servicio centralizado). Esta configuración es más avanzada y usualmente la gestiona el personal técnico.

## 8. Solución de Problemas Comunes (FAQ)

Aquí hay algunas situaciones comunes y cómo abordarlas:

*   **La impresora no imprime o muestra un error:**
    *   **Verifique la conexión física:** Asegúrese de que la impresora fiscal esté encendida y correctamente conectada al computador (usualmente por cable serial o USB según el modelo).
    *   **Papel y Tinta/Cinta:** Verifique que la impresora tenga papel y que la cinta (si aplica) esté en buen estado.
    *   **Estado en el Panel de Control:** Revise la pestaña Consola del Panel de Control (o el Dashboard Web). Puede indicar si hay un problema de comunicación con la impresora.
    *   **Mensajes de Error del Sistema de Facturación:** Su sistema de facturación (POS/ERP) puede mostrar mensajes de error más específicos devueltos por el Servidor API. Estos mensajes suelen ser informativos (ej. "Impresora Offline", "Error Fiscal: Comando no válido").
    *   (Espacio para captura de pantalla de un mensaje de error típico)
*   **¿Cómo sé qué error ocurrió?**
    *   **Logs del Servidor API:** El Servidor API de Impresión Fiscal genera archivos de registro (logs) que almacenan información detallada sobre cada operación y cualquier error que ocurra. Estos logs se encuentran en una carpeta llamada `logs` (dentro de la carpeta donde está el ejecutable). Su personal técnico puede revisar estos archivos para un diagnóstico más profundo. El nombre del archivo suele incluir la fecha (ej. `api_fiscal_AAAA-MM-DD.log`).
    *   **Ayuda Visual del Cliente (Sistema de Facturación):** Como se mencionó, su sistema de facturación a menudo interpretará la respuesta del API y le mostrará un mensaje de error más amigable o un código de error que puede ayudar a identificar el problema.
*   **El Panel de Control no aparece:**
    *   Asegúrese de que el Servidor API de Impresión Fiscal esté en ejecución (verifique el icono en la bandeja del sistema) y seleccione "Abrir Panel" desde su menú.
*   **El Dashboard Web no carga o no se puede acceder:**
    *   Asegúrese de que el Servidor API de Impresión Fiscal esté en ejecución (verifique el icono en la bandeja del sistema).
    *   Verifique que está usando la dirección y puerto correctos en el navegador (ej. `http://localhost:5051`).
    *   Recuerde que el Dashboard Web es solo de monitoreo; los reportes, comandos y configuración se hacen desde el Panel de Control.
    *   Consulte con su soporte técnico si el problema persiste.

(Esta sección puede expandirse con más preguntas y respuestas específicas a medida que se identifiquen problemas comunes).

## 9. Cumplimiento Normativo

El Servidor API de Impresión Fiscal está diseñado teniendo en cuenta la importancia del cumplimiento de las normativas fiscales. Así es como ayuda a su negocio a mantenerse en regla:

*   **Adaptación a Estándares Fiscales:** El software traduce la información de su sistema de facturación a los comandos y formatos exactos que exigen las impresoras fiscales homologadas por las autoridades tributarias de su país.
*   **Generación Correcta de Documentos:** Asegura que los documentos fiscales (facturas, notas de crédito/débito) se impriman con toda la información requerida por la ley, incluyendo datos del emisor, del cliente, detalles de los productos/servicios, impuestos desglosados, y números de control fiscal.
*   **Números de Control y Seriales:** El sistema trabaja con la impresora fiscal para asegurar la correcta generación y registro de números de control únicos y correlativos, así como el uso del número de serie de la máquina fiscal en los documentos, tal como lo exigen las regulaciones.
*   **Reportes Fiscales Obligatorios:** Facilita la emisión de reportes fiscales esenciales como el Reporte X (corte parcial) y el Reporte Z (cierre diario), que son fundamentales para la contabilidad y las auditorías fiscales.
*   **Registro Detallado para Auditorías:** Al interactuar directamente con la impresora fiscal, se asegura que cada transacción quede registrada en la memoria fiscal del dispositivo. Adicionalmente, los logs del propio Servidor API pueden servir como un rastro de auditoría de las solicitudes de impresión procesadas.
*   **Integración con Impresoras Homologadas:** El sistema está diseñado para ser compatible con modelos de impresoras fiscales que han sido aprobadas y certificadas por las entidades tributarias correspondientes (ej. TFHKA, PNP, y otros según la configuración).

**Importante:** Si bien este software es una herramienta poderosa para facilitar el cumplimiento fiscal, es responsabilidad del usuario final asegurarse de que todas las configuraciones (tasas de impuestos, datos de la empresa, etc.) sean correctas y que se sigan todos los procedimientos fiscales exigidos por la legislación local. Consulte siempre con su contador o asesor fiscal para cualquier duda específica sobre sus obligaciones tributarias.

## 10. Compatibilidad y Limitación de Responsabilidad

*   **Compatibilidad con Odoo:** El ejecutable es funcional con Odoo Community o Enterprise, tanto para la versión 17.0 como para la versión 18.0. Es compatible con instalaciones on-premise, locales, en la nube o en Odoo.sh.

*   **Limitación de Responsabilidad y Ausencia de Garantías:**
    *   El presente software se entrega **"TAL CUAL" (AS IS) y "SEGÚN DISPONIBILIDAD" (AS AVAILABLE)**, sin garantías de ningún tipo, ya sean expresas, implícitas o estatutarias, más allá de las explícitamente establecidas en un contrato de servicio suscrito y vigente entre el cliente y el desarrollador. Esto incluye, sin limitación, cualquier garantía implícita de comerciabilidad, idoneidad para un propósito particular, no infracción de derechos de terceros, o aquellas derivadas del curso de la negociación o del uso comercial.
    *   El desarrollador no se responsabiliza por la instalación, configuración o uso de este software por parte del cliente o de terceros no autorizados expresamente por el desarrollador. El uso correcto del software y la debida homologación del cliente o instalador ante el SENIAT son responsabilidad exclusiva del cliente.  
    *   La responsabilidad total del desarrollador, derivada de o relacionada con el uso o la imposibilidad de uso del software, se limitará estrictamente a los términos y condiciones especificados en el contrato de servicio suscrito y vigente. En ausencia de dicho contrato, o una vez expirada su vigencia, el desarrollador no asumirá responsabilidad alguna por cualquier daño directo, indirecto, incidental, especial, consecuencial o punitivo (incluyendo, sin limitación, pérdida de beneficios, sanciones, interrupción del negocio, pérdida de datos, o costos de adquisición de bienes o servicios sustitutos) que surjan del uso o la imposibilidad de uso del software, incluso si el desarrollador ha sido advertido de la posibilidad de tales daños.
    *   **Exenciones Específicas de Responsabilidad:** Sin perjuicio de la generalidad de lo anterior, el desarrollador queda exento de toda responsabilidad en los siguientes casos, entre otros:
        *   Cualquier manipulación, alteración, modificación no autorizada o ingeniería inversa del código fuente o del ejecutable del software.
        *   La emisión incorrecta, fraudulenta o inapropiada de documentos fiscales o no fiscales, o cualquier incumplimiento deliberado de las normativas fiscales vigentes por parte del usuario. 
        *   La instalación, integración o uso de software, hardware, complementos (add-ons) o servicios de terceros no autorizados o no certificados expresamente por el desarrollador para interactuar con este software, y cualquier malfuncionamiento derivado de dicha interacción.
        *   La desinstalación, eliminación, desactivación o cualquier forma de desincorporación del software por parte del cliente o terceros.
        *   Pérdida de datos, corrupción de información o fallos de seguridad no imputables directamente a un defecto comprobado del software original y no modificado, dentro del marco de un contrato de servicio vigente.
        *   Cualquier uso del software para fines ilícitos o no previstos en su diseño original.
        *   El cliente reconoce y acepta que, en caso de detectarse por parte del desarrollador cualquiera de las irregularidades o usos indebidos descritos anteriormente en las presentes exenciones específicas de responsabilidad, el desarrollador se reserva el derecho, y estara en la obligación legal, de notificar de manera inmediata a las autoridades fiscales competentes, sobre dichas actividades y proporcionar la información pertinente que posea.
    *   En todos los casos mencionados y cualquier otra circunstancia no cubierta por un contrato de servicio vigente, la responsabilidad última por el uso del software y sus consecuencias recaerá exclusivamente sobre el cliente.
