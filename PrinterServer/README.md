# API Printer Server

API Printer Server es una solución robusta para manejar diferentes 
tipos de impresoras a través de una interfaz HTTP. 
Soporta impresoras fiscales, térmicas ESCPOS y matriciales, 
ofreciendo una API unificada para todas las operaciones de impresión.

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
  - Impresoras Fiscales (TFHKA, PNP, RIGADZA)
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



















Necesito crear uno o mas prompts paso a paso, para una aplicacion en C# bajo el marco de .Net Framework Version v4.8

1- El objetivo inicial es crear un 'Servidor API Rest' modular, que recibira un json (en un formato que ya esta definido) y tambien servira una pagina web dinamica para indicar el estado del servidor y su configuracion.

2- El "Servidor API Rest" actuara por configuracion como "Test" para recibir el json, validar lo que se recibe y responder al usuario; dejando en todo momento una trazabilidad mediante log en registro (aunque realmente todos los procesos y configuraciones dejaran un registro) y en consola, que permita interactuar con el usuario (quizas usando NLog como libreria u otra).

3- El "Servidor API Rest" actuara por configuracion como "Spooler" para la impresion en tickeras termicas usando ESCPOS (libreria ESCPOS_NET);  tendra templates para hacer flexible los modelos de impresion, asi como su propias clases, manejadores, modelos y controladores independientes

4- El "Servidor API Rest" actuara por configuracion como "Spooler" para la impresion en maquinas fiscales usando los DLLs de cada maquina; tendra controladores, clases, modelos, manejadores y recursos separados por cada modelo que se indique independientes

5- El "Servidor API Rest" actuara por configuracion como "Spooler" para la impresion en matriz de punto (epson) usando puerto LPT; tendra templates para hacer flexible los modelos de impresion, asi como su propias clases, manejadores, modelos y controladores independientes

6- El "Servidor API Rest" actuara por configuracion como "Proxy" para recibir el json y reenviarlo a otro servidor igual que funcione como "Spooler" en otra pc o en la misma pc; por lo que es necesario que se identifique el URL destino y su puerto. Enviando el json, esperara la respuesta del otro servidor para responder al usuario.




Esto ofrecera una API unificada para todas las operaciones de impresión.

Características Resumidas:

**Múltiples Tipos de Impresoras**:
  - Impresoras Fiscales (TFHKA, PNP, RIGADZA)
  - Impresoras Térmicas ESCPOS
  - Impresoras Matriciales
  - Modo Proxy para reenvío de comandos
  - Modo Test para pruebas

**Templates Personalizables**:
  - Formato flexible para ESCPOS y matriz
  - Soporte para múltiples diseños
  - Variables dinámicas
  - Comandos de formato incorporados

**Interfaz Web**:
  - Monitor de estado en tiempo real
  - Información detallada del servidor
  - Estado de la impresora actual
  - Actualización automática

**Sistema de Logs**:
  - Niveles configurables
  - Rotación diaria de archivos
  - Salida a archivo y consola
  - Formato detallado de mensajes
  
  
  
  
  
  
  
Módulo 1: Configuración del Servidor API Rest
{
  "prompt": "Crea un proyecto ASP.NET Web Application (.NET Framework 4.8) que incluya una API REST. Configura OWIN y define rutas básicas en WebApiConfig.cs. Asegúrate de instalar los paquetes NuGet necesarios: Microsoft.AspNet.WebApi, Microsoft.AspNet.WebApi.Owin, Microsoft.Owin.Host.SystemWeb. Utiliza el archivo de configuración Startup.cs para inicializar la aplicación."
}


Módulo 2: Implementar el Modo Test
{
  "prompt": "Implementa un controlador en la API que reciba un JSON, lo valide y registre la información utilizando NLog. Configura NLog para registrar mensajes en archivos y consola. Asegúrate de que el controlador responda con un mensaje detallado sobre la validación del JSON."
}


Módulo 3: Implementar el Modo Spooler para Impresoras Térmicas ESCPOS
{
  "prompt": "Integra la librería ESCPOS_NET para manejar impresoras térmicas en la API. Configura templates flexibles que permitan adaptar los modelos de impresión. Implementa un controlador que gestione la impresión utilizando ESCPOS_NET."
}


Módulo 4: Implementar el Modo Spooler para Impresoras Fiscales
{
  "prompt": "Agrega los DLLs necesarios para cada modelo de impresora fiscal en la API. Define controladores, clases y modelos específicos para cada impresora fiscal. Asegúrate de que cada impresora pueda ser configurada y utilizada de manera independiente."
}


Módulo 5: Implementar el Modo Spooler para Impresoras Matriciales
{
  "prompt": "Configura la API para comunicarse con impresoras matriciales a través del puerto LPT. Define templates personalizables que permitan flexibilidad en los modelos de impresión. Implementa un controlador que gestione la impresión en impresoras matriciales."
}


Módulo 6: Implementar el Modo Proxy
{
  "prompt": "Implementa un controlador en la API que reciba un JSON y lo reenvíe a otro servidor configurado como 'Spooler'. Asegúrate de que el controlador pueda identificar el URL y puerto destino y maneje las respuestas adecuadamente. Implementa la lógica para reenviar el JSON y esperar la respuesta del otro servidor."
}




Trabajaremos en un proyecto de C# en entorno grafico, la solucion esta dentro de la carpeta "ApiPrinterServer" y lo haremos en conjunto con visual studio 2022.
por lo que agregaremos codigo o modificaciones y luego seran validadas en visual studio; se compilaran y se ejecutaran en ese entorno.
Si no existen errores continuaremos con los siguientes puntos y asi trabajaremos. 
No tenemos por que tocar o modificar nada del diseño. 
Por ahora nos concentraremos en 6 modulos que he ideado para el proyecto, no tengo una estructura de carpetas aun definida; por lo que estas libre de hacer tus recomendaciones, para seguir con las mejores practicas de desarrollo.

Tengo 6 prompts preparados para el proyecto, cuando estes listo iniciaremos


Aquí tienes los prompts claros y organizados para los 6 módulos del proyecto. 

---

### **Prompt 1: Crear el Servidor API Rest Modular**
**Objetivo:** Crear un servidor API Rest modular en C# bajo .NET Framework v4.8 que reciba JSON y sirva una página web dinámica para monitorear el estado del servidor y configuraciones.  

**Prompt:**
_Crea un Servidor API Rest modular en C# usando .NET Framework v4.8. Este servidor debe:_
1. Recibir un JSON en un formato predefinido (exite el ejemplo en la caperta ApiPrinterServer/Docs/invoice.json), validarlo y responder al usuario.
2. Servir una página web dinámica que muestre:
   - Estado actual del servidor.
   - Configuraciones en tiempo real.
3. Registrar trazabilidad en logs usando NLog (u otra librería similar), incluyendo logs detallados en consola y archivo.  
4. Diseñar el proyecto con una arquitectura extensible y modular para añadir funcionalidades futuras.  
5. Garantizar el soporte para configuraciones dinámicas cargadas desde un archivo `config.json`.  

---

### **Prompt 2: Módulo "Test" para Validación y Logs**
**Objetivo:** Implementar la funcionalidad de prueba que valide JSON entrante y registre la interacción.  

**Prompt:**
_Desarrolla un módulo "Test" para el Servidor API Rest en C#. Este módulo debe:_
1. Recibir y validar un JSON en un formato predefinido.
2. Responder al usuario con un mensaje de éxito o error según el resultado de la validación.
3. Generar trazabilidad mediante:
   - Logs detallados con NLog.
   - Mensajes en la consola para interacción del usuario.  
4. Permitir habilitar o deshabilitar este módulo a través de configuración dinámica.  

---

### **Prompt 3: Módulo "Spooler" para Impresoras Térmicas (ESCPOS)**
**Objetivo:** Gestionar impresión en impresoras térmicas ESCPOS con templates personalizables.  

**Prompt:**
_Desarrolla un módulo "Spooler" para impresión en impresoras térmicas ESCPOS en C#. Este módulo debe:_
1. Usar la librería **ESCPOS_NET** para gestionar las operaciones de impresión.
2. Soportar templates flexibles para modelos de impresión.
3. Diseñar clases, modelos y manejadores independientes.
4. Permitir manejar múltiples comandos ESCPOS para dar soporte a distintas funcionalidades de impresión.
5. Registrar logs detallados de las operaciones, incluyendo errores y estado de las impresoras.  

---

### **Prompt 4: Módulo "Spooler" para Impresoras Fiscales**
**Objetivo:** Gestionar impresión en máquinas fiscales usando DLLs específicas por modelo.  

**Prompt:**
_Desarrolla un módulo "Spooler" para impresoras fiscales en C#. Este módulo debe:_
1. Soportar múltiples modelos de impresoras fiscales (TFHKA, PNP, RIGADZA, etc.).
2. Usar los DLLs específicos proporcionados por cada fabricante.
3. Implementar clases, controladores y manejadores independientes por modelo.
4. Registrar logs detallados de las operaciones, como errores de comunicación y éxito en la impresión.
5. Diseñar una interfaz unificada para invocar comandos sin depender del modelo.  

---

### **Prompt 5: Módulo "Spooler" para Impresoras Matriciales**
**Objetivo:** Gestionar impresión en impresoras de matriz de punto (puerto LPT) con templates personalizables.  

**Prompt:**
_Desarrolla un módulo "Spooler" para impresoras matriciales en C#. Este módulo debe:_
1. Usar comunicación directa a través del puerto LPT.
2. Soportar templates flexibles para modelos de impresión.
3. Diseñar clases, modelos y controladores independientes.
4. Registrar logs detallados de todas las operaciones y estado de las impresoras.
5. Incluir variables dinámicas en los templates para ajustar datos de impresión.  

---

### **Prompt 6: Módulo "Proxy" para Reenvío de JSON**
**Objetivo:** Permitir que el servidor funcione como un proxy, reenviando JSON a otro servidor y manejando la respuesta.  

**Prompt:**
_Desarrolla un módulo "Proxy" para el Servidor API Rest en C#. Este módulo debe:_
1. Recibir un JSON y reenviarlo a otro servidor API configurado mediante URL y puerto.
2. Esperar la respuesta del servidor remoto y devolverla al cliente original.
3. Registrar todas las operaciones en logs con trazabilidad completa.
4