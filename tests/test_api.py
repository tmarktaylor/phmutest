"""Check the hand copying from tool.py into api.md."""
from pathlib import Path

import phmutest.tool


def test_api(checker):
    """Check the API documentaion docs/api.md reflects the actual tool.py."""
    # Check for changes in the parts of the source code file that were
    # manually copied into the Markdown file.
    apifile = Path("docs/api.md")
    fcbs = phmutest.tool.fenced_code_blocks(str(apifile))
    codefile = Path("src/phmutest/tool.py")
    codetext = codefile.read_text(encoding="utf-8")
    for num, f in enumerate(fcbs, start=1):
        # if f not in codetext:
        #    checker(f, codetext)
        assert f in codetext, f"{apifile} FCB number {num} is not in {codefile}."

    # Check that tool.py was not modified since the last
    # time its text sections were manually copied to api/docs/md.
    # If this test fails, check that api.md reflects any additions
    # or subtractions to tool.py.
    # Run black, isort, flake8 etc on tool.py.
    # Then update the actual code_length literal below.
    # Note that this test will detect any change to tool.py.
    # wc src/phmutest/tool.py
    exp_code_length = len(codetext)
    msg = f"tool.py length has changed to {exp_code_length}, is api.md up to date?"
    assert exp_code_length == 5339, msg
