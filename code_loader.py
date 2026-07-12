import os
from langchain_core.documents import Document
from code_parser import parse_python_file, parse_generic_file

# .py gets AST-based parsing (function/class-level chunks).
# Everything else here falls back to generic text chunking.
GENERIC_EXTENSIONS = {
    ".js", ".jsx", ".ts", ".tsx",
    ".java", ".go", ".rb", ".php",
    ".c", ".cpp", ".h", ".hpp", ".cs",
    ".rs", ".swift", ".kt",
    ".html", ".css",
    ".md", ".yml", ".yaml", ".json"
}

SUPPORTED_EXTENSIONS = {".py"} | GENERIC_EXTENSIONS

IGNORE_FILES = {
    "package-lock.json",
    "yarn.lock",
    "pnpm-lock.yaml",
    "composer.lock",
    "poetry.lock",
    "Cargo.lock"
}

MAX_FILE_SIZE_BYTES = 300_000  # skip unusually large files (generated/minified/data dumps)

IGNORE_DIRS = {
    ".git",
    "__pycache__",
    "venv",
    ".venv",
    "node_modules",
    "dist",
    "build"
}


def _build_structure_overview(folder_path):
    """
    Creates one synthetic Document describing the repo's file tree
    (and README content, if present) so questions like "explain the
    project structure" have something real to retrieve instead of
    falling back to a random code chunk.
    """
    tree_lines = []

    for root, dirs, files in os.walk(folder_path):
        dirs[:] = [d for d in dirs if d not in IGNORE_DIRS]

        depth = root.replace(folder_path, "").count(os.sep)
        indent = "  " * depth
        rel_root = os.path.relpath(root, folder_path)
        label = "." if rel_root == "." else os.path.basename(root)
        tree_lines.append(f"{indent}{label}/")

        for f in sorted(files):
            if not f.startswith("."):
                tree_lines.append(f"{indent}  {f}")

    tree_text = "\n".join(tree_lines)

    readme_text = ""
    for candidate in ("README.md", "README.rst", "README.txt", "readme.md"):
        readme_path = os.path.join(folder_path, candidate)
        if os.path.isfile(readme_path):
            with open(readme_path, encoding="utf-8", errors="ignore") as f:
                readme_text = f.read()[:3000]  # cap length
            break

    content = f"PROJECT FILE STRUCTURE:\n{tree_text}"
    if readme_text:
        content += f"\n\nREADME CONTENT:\n{readme_text}"

    return Document(
        page_content=content,
        metadata={
            "name": "project_structure_overview",
            "type": "ProjectOverview",
            "file": folder_path
        }
    )


def load_codebase(folder_path):

    documents = [_build_structure_overview(folder_path)]

    for root, dirs, files in os.walk(folder_path):

        dirs[:] = [d for d in dirs if d not in IGNORE_DIRS]

        for file in files:

            if file.startswith(".") or file in IGNORE_FILES:
                continue

            ext = os.path.splitext(file)[1]
            file_path = os.path.join(root, file)

            try:
                if os.path.getsize(file_path) > MAX_FILE_SIZE_BYTES:
                    continue
            except OSError:
                continue

            if ext == ".py":
                try:
                    docs = parse_python_file(file_path)
                except SyntaxError:
                    # invalid/unparseable Python — fall back to generic chunking
                    docs = parse_generic_file(file_path)
                documents.extend(docs)

            elif ext in GENERIC_EXTENSIONS:
                documents.extend(parse_generic_file(file_path))

    if len(documents) == 1:
        # only the structure overview got added — no real source files found
        raise ValueError(
            f"No supported source files found in this repository. "
            f"Supported extensions: {', '.join(sorted(SUPPORTED_EXTENSIONS))}"
        )

    return documents