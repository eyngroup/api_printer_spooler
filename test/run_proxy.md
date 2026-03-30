# Ejecución de Pruebas: Proxy y Spooler

Este directorio contiene scripts para facilitar la ejecución y pruebas del servidor API en sus dos modos: **Spooler** (Impresión directa) y **Proxy** (Reenvío).

## Requisitos Previos

El proyecto utiliza `uv` para la gestión de dependencias y entornos virtuales. Asegúrese de tenerlo instalado.

```bash
pip install uv
```

## Scripts de Ejecución

### 1. Ejecutar Spooler (`run_spooler.bat`)

Este script inicia el servidor en modo **SPOOLER** utilizando la configuración principal (`config/config.json`).
Por defecto, escucha en el puerto **5051**.

```batch
test/run_spooler.bat
```
Equivalente a ejecutar: `uv run main.py`

### 2. Ejecutar Proxy (`run_proxy.bat`)

Este script inicia una segunda instancia del servidor en modo **PROXY**.
Para permitir la ejecución simultánea en la misma máquina, este script utiliza una configuración volátil (definida en `test/run_proxy.py`) con los siguientes ajustes:

*   **Puerto de Escucha**: `5052` (para no chocar con el Spooler en 5051).
*   **Modo**: `PROXY`.
*   **Target (Destino)**: `http://localhost:5051/api/printers` (redirecciona al Spooler local).

```batch
test/run_proxy.bat
```
Equivalente a ejecutar: `uv run test/run_proxy.py`

## Ejecución Simultánea (Prueba de Loopback)

Puede levantar ambos servidores al mismo tiempo para probar el flujo completo:

1.  Abra una terminal y ejecute `test/run_spooler.bat`.
2.  Abra **otra** terminal y ejecute `test/run_proxy.bat`.
3.  Envíe peticiones al puerto **5052** (Proxy). Este las reenviará automáticamente al puerto **5051** (Spooler), quien finalmente procesará la impresión.

Esto simula un entorno real donde el Proxy estaría en una máquina (ej. balanza, punto de venta remoto) y el Spooler en otra (servidor de impresión), pero facilitando la depuración en un solo equipo de desarrollo.
