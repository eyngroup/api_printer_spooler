#!/usr/bin/env python
# -*- coding: utf-8 -*-

import sys
import os
from cx_Freeze import setup, Executable

base_path = os.path.dirname(os.path.dirname(os.path.dirname(__file__)))

include_files = [
    (os.path.join(base_path, "library", "TfhkaNet.dll"), "library/TfhkaNet.dll"),
]

build_options = {
    "packages": [
        "clr",
        "logging",
        "pythonnet",
    ],
    "include_files": include_files,
    "include_msvcr": True,
    "excludes": ["tkinter", "unittest", "email", "xml", "pydoc"],
    "optimize": 2,
}

base = None
if sys.platform == "win32":
    base = "Console"

executables = [
    Executable(
        "test_tfhka_runtime.py",
        base=base,
        target_name="TestTFHKA.exe",
    )
]

setup(
    name="TestTFHKA",
    version="1.0.0",
    description="Test de DLL TFHKA con runtime",
    options={"build_exe": build_options},
    executables=executables,
)
