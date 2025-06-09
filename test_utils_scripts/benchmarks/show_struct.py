import os

ignore_folders = {".idea", ".ruff_cache", ".venv", ".vs", ".vscode", ".git", "__pycache__"}

descriptions = {
    "config": "Archivos de configuración",
    "controllers": "Controladores para la lógica de impresión",
    "docs": "Documentación del proyecto",
    "logs": "Archivos de log",
    "models": "Modelos de datos",
    "printers": "Lógica específica de las impresoras",
    "resources": "Recursos adicionales",
    "server": "Implementación del servidor API",
    "templates": "Plantillas JSON",
    "tests": "Pruebas unitarias",
    "views": "Archivos HTML y estáticos",
    "static": "",
    "css": "",
    "js": "",
}


def list_files(startpath, output_file):
    with open(output_file, "w", encoding="utf-8") as f:
        f.write("## Estructura del Proyecto\n\n")
        f.write("```bash\n")
        for root, dirs, files in os.walk(startpath):
            dirs[:] = [d for d in dirs if d not in ignore_folders]

            level = root.replace(startpath, "").count(os.sep)
            indent = "    " * level
            base_name = os.path.basename(root)

            if base_name in descriptions:
                folder_desc = f"{base_name}/                  # {descriptions[base_name]}"
            else:
                folder_desc = f"{base_name}/"
            f.write(f"{indent}├── {folder_desc}\n")

            subindent = "    " * (level + 1)
            for i, file in enumerate(files):
                if i == len(files) - 1:
                    f.write(f"{subindent}└── {file}\n")
                else:
                    f.write(f"{subindent}├── {file}\n")
        f.write("```\n")


def update_readme(
    readme_file,
    structure_file,
    start_marker="## Estructura del Proyecto",
    end_marker="## Estructura del Proyecto (fin)",
):
    with open(readme_file, "r", encoding="utf-8") as f:
        content = f.read()

    with open(structure_file, "r", encoding="utf-8") as f:
        new_structure = f.read()

    start_idx = content.find(start_marker)
    end_idx = content.find(end_marker, start_idx) + len(end_marker)

    if start_idx != -1 and end_idx != -1:
        updated_content = content[:start_idx] + new_structure + content[end_idx:]

        with open(readme_file, "w", encoding="utf-8") as f:
            f.write(updated_content)
    else:
        print("Markers not found in README.md")


if __name__ == "__main__":
    output_file = os.path.join(os.getcwd(), "estructura.md")
    list_files(os.getcwd(), output_file)

    # readme_file = os.path.join(os.getcwd(), "README.md")
    # structure_file = os.path.join(os.getcwd(), "estructura.md")
    # update_readme(readme_file, structure_file)
