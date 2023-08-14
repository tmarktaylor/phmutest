"""Check handling of --generate command line options"""
import os
import unittest
import unittest.main
from contextlib import ExitStack
from pathlib import Path
from tempfile import TemporaryDirectory
from typing import List

import phmutest.main
import tests.py.generated_project


def generate_from_files(*mdfiles: List[str], command=""):
    """Generate testfile from mdfiles, return generated testfile."""
    mdpaths = [Path(f) for f in mdfiles]
    contents = [p.read_text(encoding="utf-8") for p in mdpaths]

    with ExitStack() as stack:
        # Create temporary directory, copy input Markdown file to it.
        tmpdir = stack.enter_context(TemporaryDirectory())
        stack.callback(os.chdir, Path.cwd())  # restore
        os.chdir(tmpdir)
        args = []
        print(mdpaths)
        for path, text in zip(mdpaths, contents):
            path.parent.mkdir(mode=0o700, parents=True, exist_ok=True)
            dest = tmpdir / path
            dest.write_text(text, encoding="utf-8")
            args.append(str(path))

        # Call phmutest with args to generate a testfile gencode.py. Read the testfile.
        args = list(mdfiles)
        if command:
            args.extend(command.split())
        args.extend(["--generate", "gencode.py"])
        print(args)
        phmresult = phmutest.main.main(args)
        assert phmresult is None
        genfile = Path("gencode.py").read_text(encoding="utf-8")
        return genfile


def test_code():
    """Generate a unittest .py file from Markdown, and compare to expected file."""
    genfile = generate_from_files("tests/md/project.md", command="")
    want = Path("tests/py/generated_project.py").read_text(encoding="utf-8")
    assert want == genfile


def test_share_demo():
    """Generate a unittest .py file from Markdown, and compare to expected file."""
    command = "--share-across-files docs/share/file1.md docs/share/file2.md"
    genfile = generate_from_files(
        "docs/share/file1.md",
        "docs/share/file2.md",
        "docs/share/file3.md",
        command=command,
    )
    want = Path("tests/py/generated_sharedemo.py").read_text(encoding="utf-8")
    assert want == genfile


def test_repl():
    """Generate docstrings from Markdown, and compare to expected file."""
    genfile = generate_from_files(
        "tests/md/example1.md", "tests/md/example2.md", command="--replmode"
    )
    want = Path("tests/doctest/generated_replmode.txt").read_text(encoding="utf-8")
    assert want == genfile
    testcase = unittest.TestCase()
    testcase.maxDiff = 20000
    testcase.assertEqual(want, genfile)
    assert want == genfile


def test_unittest_args(capsys):
    """unittest passes on the (want) file used in above test case."""
    unittest_args = ["unittest.main", "--quiet"]
    testprog: unittest.TestProgram = unittest.main(
        module=tests.py.generated_project, argv=unittest_args, exit=False
    )
    assert testprog.result.wasSuccessful() is True
