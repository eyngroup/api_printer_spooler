# Proyecto -> API Rest | Spooler de Impresión | Proxy

## En Memoria de Ian Abdiel Graterol Santana (2024)

> *"Este proyecto es un tributo a la pasión tecnológica y legado de mi hijo, cuyo espíritu continúa guiándome en cada línea de código."*

![I will love you forever](resources/block.svg)

## Visión General

**Servidor API REST** para gestión avanzada de colas de impresión con soporte para:

- **Impresoras Fiscales** (TFHKA, PNP, RIGAZSA [en desarrollo], BEMATECH [en desarrollo])
- **Impresoras de Tickets** (POS, Comandos ESC-POS)
- **Impresoras Matriciales** (EPSON, Comandos ESC/P)

## Características Principales

✅ Soporte multiplataforma (Windows/Linux [en desarrollo])

✅ Gestión centralizada de colas de impresión

✅ Protocolos de comunicación estandarizados

✅ Sistema de plantillas configurables

## Guía Rápida

### Requisitos minimos

- Python 3.10 (64-bit)
- Entorno virtual recomendado

### Instalación

<details>
<summary>🖥️ Windows</summary>

1. Instalar [Python 3.10 64-bit](https://www.python.org/ftp/python/3.10.0/python-3.10.0.exe)
```bash
git clone https://github.com/eyngroup/api_printer_server.git
cd api_printer_server
python -m venv .venv
.venv\Scripts\activate
python.exe -m pip install --upgrade pip
pip install -r requirements.txt
python setup.py build
```
</details>

<details>
<summary>🐧 Linux</summary>
  
* En proyecto con la adecuación e implementación de los módulos suministrados en "controllers".

</details>

### Documentación

| Sección | Descripción |
|---------|-------------|
| [Proyecto](docs/project.md) | Diseño general y componentes |
| [Configuración](config/config.md) | Parámetros del sistema |
| [Plantillas](templates/templates.md) | Personalización de formatos |

### Desarrollo

<details>
<summary>🛠️ Contribuciones</summary>

1. Revisar [issues abiertos](https://github.com/eyngroup/repo/issues)
2. Crear nuevo issue para propuestas
3. Actualizar documentación relacionada
</details>

## Apoyo

[![Un Café con PayPal](https://img.shields.io/badge/Cafe-PayPal-blue)](https://paypal.me/irongraterol)

<summary>❤️ Si te ha sido útil este código, considera invitarme un café ☕ para apoyar el proyecto. ¡Gracias! 😊 </summary>


##
Copyright © 2024, Iron Graterol

##
Todo el codigo está bajo los términos de la [GNU Affero General Public License v3.0](https://www.gnu.org/licenses/agpl-3.0.html).
Consulta el documento LICENSE incluido en este proyecto para más detalles.
