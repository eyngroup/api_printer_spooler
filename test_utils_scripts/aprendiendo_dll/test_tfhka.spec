# -*- mode: python ; coding: utf-8 -*-

import os
import sys
from PyInstaller.utils.hooks import collect_dynamic_libs

block_cipher = None

# Obtener la ruta base del proyecto
SPEC_PATH = os.path.abspath(SPECPATH)
project_root = os.path.dirname(os.path.dirname(SPEC_PATH))  # Removemos un dirname

# Ruta al DLL
dll_path = os.path.join(project_root, 'library', 'TfhkaNet.dll')
print(f"Buscando DLL en: {dll_path}")
if not os.path.exists(dll_path):
    raise FileNotFoundError(f"DLL no encontrado en: {dll_path}")

# Definir el DLL y su ubicación
binary_files = [
    (dll_path, 'library')
]

# Ruta al runtime hook
runtime_hooks = [os.path.join(SPEC_PATH, 'runtime_hook.py')]

a = Analysis(
    ['test_tfhka_runtime.py'],
    pathex=[project_root],  # Agregamos el root del proyecto al path
    binaries=binary_files,
    datas=[],
    hiddenimports=['clr', 'pythonnet', 'System', 'System.Reflection'],
    hookspath=[],
    hooksconfig={},
    runtime_hooks=runtime_hooks,  # Agregamos el runtime hook
    excludes=[],
    win_no_prefer_redirects=False,
    win_private_assemblies=False,
    cipher=block_cipher,
    noarchive=False,
)

pyz = PYZ(a.pure, a.zipped_data, cipher=block_cipher)

exe = EXE(
    pyz,
    a.scripts,
    [],
    exclude_binaries=True,
    name='TestTFHKA',
    debug=False,
    bootloader_ignore_signals=False,
    strip=False,
    upx=True,
    console=True,
    disable_windowed_traceback=False,
    argv_emulation=False,
    target_arch=None,
    codesign_identity=None,
    entitlements_file=None,
)

coll = COLLECT(
    exe,
    a.binaries,
    a.zipfiles,
    a.datas,
    strip=False,
    upx=True,
    upx_exclude=[],
    name='TestTFHKA',
)
