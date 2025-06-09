from cx_Freeze import setup, Executable
import configparser
import sys

config = configparser.ConfigParser()
config.read('config.ini')
test = config.getboolean("server", "debug")

# Incluye los archivos adicionales en la lista include_files
include_files = [('templates/index.html', 'templates/index.html'),
                 ('config.ini', 'config.ini')]
file_icon = "resources/printer_fiscal.ico"

base_win = None
# Para ejecutar la App en Modo Ventana Utilizar base_win = None:
# Si la plataforma es Windows, establece base a "Win32GUI"
if sys.platform == "win32" and not test:
    base_win = "Win32GUI"

setup(
    name="ApiProxy",
    version="1.4",
    description="ApiProxy Spooler",
    options={'build_exe': {'include_files': include_files}},
    executables=[Executable("app.py", base=base_win, icon=file_icon)]
)

# Ejecutar con: python setup.py build
