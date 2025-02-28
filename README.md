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

### Requisitos

- Python 3.10 (32-bit)
- Entorno virtual recomendado

### Instalación

<details>
<summary>🖥️ Windows</summary>

1. Instalar [Python 3.10 32-bit](https://www.python.org/ftp/python/3.10.0/python-3.10.0.exe)
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
3. Desarrollar en rama feature/fix
4. Ejecutar pruebas: 
```bash
pytest tests/
```
5. Actualizar documentación relacionada
</details>

## Apoyo

[![Un Café con PayPal](https://img.shields.io/badge/Cafe-PayPal-blue)](https://paypal.me/irongraterol)

<summary>❤️ Si te ha sido útil este código, considera invitarme a un café ☕ o un almuerzo 🍽 para apoyar el proyecto. ¡Gracias! 😊 </summary>

## 
Bajo los términos de la [Licencia Pública Mozilla v2.0](http://mozilla.org/MPL/2.0/).

## 
Copyright © 2024, Iron Graterol.
