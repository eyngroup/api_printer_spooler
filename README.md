# Proyecto -> API Rest | Spooler Fiscal | Proxy

## En Memoria de Ian Abdiel Graterol Santana (2024)

> *"Este proyecto es un tributo a la pasión tecnológica y legado de mi hijo, cuyo espíritu continúa guiándome en cada línea de código."*

![I will love you forever](resources/block.svg)

## Visión General

**API Printer Spooler** es un servidor API REST orientado exclusivamente a **impresión fiscal**.

En esta rama se eliminó todo el soporte no fiscal. El sistema mantiene solo el flujo fiscal vía puerto serial, con operación en dos modos:

- **SPOOLER**: procesa documentos y comandos directamente sobre la impresora fiscal conectada.
- **PROXY**: reenvía la solicitud a otro spooler fiscal.

## Alcance actual

- **Drivers fiscales soportados**: `TFHKA`, `PNP`
- **Operaciones disponibles**:
  - Impresión de documentos fiscales
  - Reporte X
  - Reporte Z
  - Envío de comandos fiscales directos
  - Edición web de configuración
  - Dashboard de estado

## Características Principales

- Gestión centralizada de impresión fiscal
- Comunicación serial mediante `pyserial`
- Validación de configuración con JSON Schema
- Dashboard web para estado del servicio y acciones fiscales
- Modo proxy para topologías remotas
- Plantilla fiscal configurable en `templates/template_fiscal_printer.json`

## Guía Rápida

### Requisitos mínimos

- Python 3.10 (64-bit)
- Entorno virtual recomendado
- Acceso al puerto serial de la impresora fiscal
- En Linux, entorno gráfico compatible con system tray y `python3-tk` si `tkinter` no está disponible

### Instalación

```bash
python3 -m venv .venv
source .venv/bin/activate
pip install --upgrade pip
pip install -r requirements.txt
```

En Windows PowerShell:

```powershell
python -m venv .venv
.venv\Scripts\Activate.ps1
python -m pip install --upgrade pip
pip install -r requirements.txt
```

### Ejecución

Con entorno tradicional:

```bash
python3 main.py
```

Si trabajas con `uv`:

```bash
uv run main.py
```

### Endpoints operativos principales

- `GET /api/ping`
- `GET /api/status`
- `POST /api/printers`
- `GET /api/report_x`
- `GET /api/report_z`
- `POST /api/command`
- `POST /api/config`
- `POST /api/auth/validate`

## Documentación

| Sección | Descripción |
|---------|-------------|
| [Proyecto](docs/project.md) | Arquitectura funcional y flujo fiscal |
| [Configuración](config/config.md) | Estructura y opciones de `config/config.json` |
| [Plantillas](templates/templates.md) | Campos y comportamiento del template fiscal |
| [Checklist](docs/CHECKLIST.md) | Despliegue y verificación operativa |
| [Memoria](docs/MEMORY.md) | Estado real del branch y continuidad técnica |

## Desarrollo

- Mantener el contrato **fiscal-only** en código, UI y documentación.
- Si se agrega un nuevo modelo fiscal, actualizar driver, `printer_manager.py`, schema, template y docs.
- Antes de desplegar, validar al menos:
  - `/api/status`
  - guardado de configuración
  - impresión fiscal
  - reporte X
  - reporte Z

## Apoyo

[![Un Café con PayPal](https://img.shields.io/badge/Cafe-PayPal-blue)](https://paypal.me/irongraterol)

<summary>❤️ Si te ha sido útil este código, considera invitarme un café ☕ para apoyar el proyecto. ¡Gracias! 😊 </summary>

##
Copyright © 2024, Iron Graterol

##
Todo el codigo está bajo los términos de la [GNU Affero General Public License v3.0](https://www.gnu.org/licenses/agpl-3.0.html).
Consulta el documento LICENSE incluido en este proyecto para más detalles.

