"""Check the code snippets from tool.py found in api.md."""

import ast
from pathlib import Path

import phmutest.tool

PYTHON_FILE = Path("src/phmutest/tool.py")
MARKDOWN_FILE = "docs/api.md"


def test_api():
    """Check the API documentation docs/api.md reflects the actual tool.py."""
    # Check for changes in the parts of the source code file that were
    # manually copied into the Markdown file.
    # The contents of each FCB should be present verbatim in the Python file.
    fenced_code_blocks = phmutest.tool.fenced_code_blocks(MARKDOWN_FILE)
    source = PYTHON_FILE.read_text(encoding="utf-8")
    for num, fcb in enumerate(fenced_code_blocks, start=1):
        assert (
            fcb in source
        ), f"{MARKDOWN_FILE} FCB number {num} is not in {PYTHON_FILE}."

    # The Python file tool.py should have one class and one function
    # def for each FCB in api.md. If there are more classes and functions in the
    # tool.py, the extras may be missing from the Markdown file.
    tree = ast.parse(source)
    count = 0
    for node in ast.walk(tree):
        if isinstance(node, (ast.FunctionDef, ast.ClassDef)):
            count += 1
    assert count > 0
    assert count == len(fenced_code_blocks)
