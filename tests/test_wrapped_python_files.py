"""Check example Python file is the same as in Markdown fenced code block."""
from pathlib import Path

import phmutest.tool


def check_first_block(markdown_path, contents_path):
    """Check that first FCB in Markdown is same as the file contents."""
    want = Path(contents_path).read_text(encoding="utf-8")
    blocks = phmutest.tool.fenced_code_blocks(markdown_path)
    got = blocks[0]
    assert want == got


def test_fixture_py_md():
    """The copy of .py file in fenced code block is the same as the file."""
    check_first_block(
        markdown_path="docs/fixture_py.md",
        contents_path="src/phmutest/fixture.py",
    )


def test_globs_py_md():
    """The copy of .py file in fenced code block is the same as the file."""
    check_first_block(
        markdown_path="docs/fix/code/globdemo_py.md",
        contents_path="docs/fix/code/globdemo.py",
    )


def test_chdir_py_md():
    """The copy of .md file in fenced code block is the same as the file."""
    check_first_block(
        markdown_path="docs/fix/code/chdir_py.md",
        contents_path="docs/fix/code/chdir.py",
    )


def test_drink_py_md():
    """The copy of .md file in fenced code block is the same as the file."""
    check_first_block(
        markdown_path="docs/fix/repl/drink_py.md",
        contents_path="docs/fix/repl/drink.py",
    )


def test_generate_project_py_md():
    """The copy of .md file in fenced code block is the same as the file."""
    check_first_block(
        markdown_path="docs/generated_project_py.md",
        contents_path="tests/py/generated_project.py",
    )


def test_generate_share_demo_py_md():
    """The copy of .md file in fenced code block is the same as the file."""
    check_first_block(
        markdown_path="docs/generated_share_demo_py.md",
        contents_path="tests/py/generated_sharedemo.py",
    )


def notest_count_test_modules():
    """Count the number of sys.modules that are generated testfiles. Last in suite."""
    # Change notest to test above to do the count.
    import sys

    count = 0
    for m in sys.modules.copy():
        if m.startswith("_phm"):
            count += 1
    print(f"Tests generated and imported {count} testfile modules")
    assert False
