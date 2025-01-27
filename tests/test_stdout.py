"""Tests --stdout feature."""

import phmutest.main
import phmutest.summary


def test_example2_stdout(capsys):
    """Run with --stdout."""
    line = "tests/md/example2.md --stdout"
    phmresult = phmutest.main.command(line)
    expected_stdout = """
stdout:
[1, 4, 9, 16, 25]
He said his name is Fred.
There is no output block so this is not checked.
cat 3
window 6
defenestrate 12
2002-03-11
"""
    want = phmutest.summary.Metrics(
        number_blocks_run=5,
        passed=5,
        failed=0,
        skipped=0,
        suite_errors=0,
        number_of_files=1,
        files_with_no_blocks=0,
        number_of_deselected_blocks=0,
    )
    assert want == phmresult.metrics
    output = capsys.readouterr().out
    assert expected_stdout == output


def test_setup_stdout(capsys):
    """Run with --stdout in setup block."""
    line = "docs/setup/setup.md --stdout"
    phmresult = phmutest.main.command(line)
    expected_stdout = """
stdout:
apples, cider, cherries, very small rocks.
Restoring current working directory...
"""
    want = phmutest.summary.Metrics(
        number_blocks_run=5,
        passed=5,
        failed=0,
        skipped=0,
        suite_errors=0,
        number_of_files=1,
        files_with_no_blocks=0,
        number_of_deselected_blocks=0,
    )
    assert want == phmresult.metrics
    output = capsys.readouterr().out
    assert expected_stdout == output


def test_no_stderr_stdout(capsys):
    """Run with --stdout with failing FCBs and mixed stdout/stderr."""
    line = "tests/md/printer.md --stdout"
    phmresult = phmutest.main.command(line)
    expected_stdout = """
stdout:
asserting False...
printing to stdout
(10, 1)
"""
    want = phmutest.summary.Metrics(
        number_blocks_run=3,
        passed=1,
        failed=2,
        skipped=1,
        suite_errors=0,
        number_of_files=1,
        files_with_no_blocks=0,
        number_of_deselected_blocks=0,
    )
    assert want == phmresult.metrics
    output = capsys.readouterr().out
    assert expected_stdout == output
