from langchain_core.documents import Document
import ast
import os

def extract_functions(code):

    tree = ast.parse(code)

    lines = code.split("\n")

    functions = []

    for node in ast.walk(tree):

        if isinstance(node, ast.FunctionDef):

            function_code = "\n".join(
                lines[node.lineno-1 : node.end_lineno] #means:"Give me only the lines where this function exists." lineno is the index where the line starts and end_lineno is the index of the last line of code
            )

            functions.append(function_code)

    return functions

def parse_python_file(file_path):

    with open(file_path, encoding="utf-8", errors="ignore") as file:
        code = file.read()

    tree = ast.parse(code)

    documents = []

    lines = code.split("\n")

    file_doc = Document(
        page_content=code,
        metadata={
            "name": file_path.split("\\")[-1],
            "type": "File",
            "file": file_path
        }
    )

    documents.append(file_doc)

    for node in ast.walk(tree):

        if isinstance(node, ast.FunctionDef) or isinstance(node, ast.ClassDef):
            code_block = "\n".join(
            lines[node.lineno-1 : node.end_lineno]
            )

            doc = Document(
                page_content=code_block,    
                 metadata={
                    "name": node.name,
                    "type": type(node).__name__,
                    "file": file_path
                }
            )

            documents.append(doc)


    return documents