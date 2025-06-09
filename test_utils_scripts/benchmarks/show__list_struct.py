import os

ignore_folders = {".idea", ".venv", ".vscode", ".git", "__pycache__"}


def list_files(startpath, output_file):
    with open(output_file, "w", encoding="utf-8") as f:
        for root, dirs, files in os.walk(startpath):
            dirs[:] = [d for d in dirs if d not in ignore_folders]

            level = root.replace(startpath, "").count(os.sep)
            indent = " " * 4 * level
            f.write(f"{indent}{os.path.basename(root)}/\n")

            subindent = " " * 4 * (level + 1)
            for file in files:
                f.write(f"{subindent}{file}\n")


if __name__ == "__main__":
    output_file = os.path.join(os.getcwd(), "estructura.txt")
    list_files(os.getcwd(), output_file)
