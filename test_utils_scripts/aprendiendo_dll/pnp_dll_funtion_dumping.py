import ctypes
import os

# Cargar la DLL
dll_path = r"./pnpdll.dll"
dll = ctypes.CDLL(dll_path)


def enumerate_functions(dll_path):
    if not os.path.exists(dll_path):
        raise FileNotFoundError(f"El archivo {dll_path} no existe.")

    dumpbin_output = os.popen(f"dumpbin /EXPORTS {dll_path}").read()
    functions = []
    for line in dumpbin_output.splitlines():
        if "ordinal" in line.lower() or "hint" in line.lower():
            continue
        parts = line.split()
        if len(parts) > 2:
            func_name = parts[-1]
            functions.append(func_name)
    return functions


functions = enumerate_functions(dll_path)
print(f"Funciones en {dll_path}:")
for func in functions:
    print(f" - {func}")
