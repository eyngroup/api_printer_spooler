# Uso del Endpoint de Comandos Fiscales Directos

El endpoint `/api/command` permite enviar una serie de comandos "crudos" directamente a la impresora fiscal configurada y activa. Esto es útil para tareas de mantenimiento, configuración de encabezados, diagnósticos u operaciones específicas no cubiertas por el flujo estándar de documentos.

## Endpoint

*   **URL**: `/api/command`
*   **Método**: `POST`
*   **Content-Type**: `application/json`

## Estructura del Payload

El cuerpo de la solicitud debe ser un objeto JSON con una clave `commands` que contenga una lista de strings. Cada string es un comando que será enviado a la impresora.

```json
{
    "commands": [
        "CMD1",
        "CMD2",
        "CMD3"
    ]
}
```

### Ejemplo (`commands_example.json`)

```json
{
    "commands": [
        "S1",   
        "I0X",
        "I0Z"
    ]
}
```
*Nota: `S1` es un comando común en impresoras TFHKA para obtener estado, `I0X` para reporte X, etc. Los comandos dependen del protocolo de la impresora.*

## Comportamiento

1.  **Validación**: Se verifica que la impresora fiscal esté habilitada y en línea.
2.  **Ejecución Secuencial**: Los comandos se ejecutan uno por uno en el orden recibido.
3.  **Manejo de Errores**: Si un comando falla (la impresora retorna error), el sistema **NO** detiene la ejecución de los siguientes comandos. Se intentarán ejecutar todos.
4.  **Respuesta**: Retorna una lista con el resultado de cada comando enviado.

## Respuesta Ejemplo

```json
{
    "status": true,
    "message": "Comandos procesados",
    "data": [
        {
            "command": "S1",
            "success": true
        },
        {
            "command": "I0X",
            "success": false
        },
        {
            "command": "I0Z",
            "success": true
        }
    ]
}
```

## Ubicación del Archivo de Ejemplo

Puede encontrar un archivo JSON de ejemplo en:
`handy/commands_example.json`
