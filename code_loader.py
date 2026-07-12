import os
from code_parser import parse_python_file


def load_codebase(folder_path):

    documents = []

    ignore_dirs = {
        ".git",
        "__pycache__",
        "venv",
        ".venv",
        "node_modules"
    }

    for root, dirs, files in os.walk(folder_path):

        # remove ignored folders
        dirs[:] = [
            d for d in dirs
            if d not in ignore_dirs
        ]

        for file in files:

            if file.endswith(".py") and not file.startswith("."):

                file_path = os.path.join(root, file)

                docs = parse_python_file(file_path)

                documents.extend(docs)

    return documents