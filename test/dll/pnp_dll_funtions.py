import pefile


def get_exported_functions(dll_path):
    pe = pefile.PE(dll_path)
    exported_functions = []
    for exp in pe.DIRECTORY_ENTRY_EXPORT.symbols:
        if exp.name is not None:
            exported_functions.append(exp.name.decode("utf-8"))
    return exported_functions


dll_path = r"./pnpdll.dll"
functions = get_exported_functions(dll_path)

print(f"Funciones exportadas en {dll_path}:")
for func in functions:
    print(f" - {func}")
