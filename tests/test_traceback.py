"""Check the traceback for some Markdown with broken examples."""

import sys

import pytest

import phmutest.config
import phmutest.main
import phmutest.summary
import phmutest.tool
from phmutest.printer import EXCEPTION_LINE, REASON, RESULT, TRACE, Log

traceback_extra = False
try:
    import stackprinter  # noqa: F401

    traceback_extra = True
except ModuleNotFoundError:
    pass


def check_exception_line_numbers(log: Log):
    # Check that the exception line numbers in the log for the
    # failed and error entries are present in the traceback log entries.
    # This should fail if a different line number is reported in the
    # traceback than what was reported in the "failed" or "error" log entry.
    elines = [e[EXCEPTION_LINE] for e in log if e[RESULT] in ["failed", "error"]]
    traces = [e[REASON] for e in log if e[RESULT] == TRACE]
    assert elines
    assert traces
    for line, trace in zip(elines, traces):
        assert f", line {line}, in" in trace


@pytest.mark.skipif(not traceback_extra, reason="Requires install extra [traceback].")
@pytest.mark.skipif(sys.version_info > (3, 12), reason="Skip py 3.12+")
def test_readme_traceback(capsys, ordered_checker):
    """Test the stackprinter traceback printed when running on README.md."""
    results = phmutest.main.command("README.md --log --quiet")
    output = capsys.readouterr().out.strip()
    # Notes:
    # - Only stdout is checked.
    # - The unittest traceback is printed to stderr. It is not checked here.
    print(output)  # This is helpful to troubleshoot test case fails.
    assert "FAIL: tests" not in output, "not looking at unittest stdout"
    strings = [
        ", line 37, in tests",
        "--> 37",
        " answer = 'very small rocks'",
        ", line 42, in tests",
        " answer = 'very small rocks'",
        ", line 55, in tests",
        ", line 32, in ask",
        "--> 32",
        " question = 'What floats?'",
    ]
    ordered_checker(output, strings)
    check_exception_line_numbers(results.log)


@pytest.mark.skipif(not traceback_extra, reason="Requires install extra [traceback].")
@pytest.mark.skipif(sys.version_info > (3, 12), reason="Skip py 3.12+")
def test_traceback_md(capsys, ordered_checker):
    """Test the stackprinter traceback printed when running on README.md."""
    results = phmutest.main.command("tests/md/tracer.md --log")
    output = capsys.readouterr().out.strip()
    # Notes:
    # - Only stdout is checked.
    # - The unittest traceback is printed to stderr. It is not checked here.
    print("\n\n----- output:\n")  # This is helpful to troubleshoot test case fails.
    print(output)  # This is helpful to troubleshoot test case fails.
    strings = [
        ">   60",
        ", line 67, in tests",
        "--> 67",
        " answer = 'very small rocks'",
        "fail_bot.ask",
        #
        ">   72",
        ", line 72, in tests",
        "--> 72",
        " answer = 'very small rocks'",
        "pass_bot.inquire",
        #
        ">   92",
        ">   36",
        ", line 85, in tests",
        "--> 85",
        "raiser_bot.ask",
        ", line 53, in ask",
        "--> 53",
        " question = 'What floats?'",
        #
        "tests/md/tracer.md:101",
    ]
    ordered_checker(output, strings)
    check_exception_line_numbers(results.log)

    # Check the example in the docs.
    chooser = phmutest.tool.FCBChooser("docs/traceback.md")
    examples = chooser.select(info_string="txt")
    example = examples[0]
    # This is helpful to troubleshoot test case fails.
    print("\n\n----- docs/traceback.md:\n")
    print(example)  # This is helpful to troubleshoot test case fails.
    # The example should have the same substrings in the same order as
    # phmutest stdout.
    ordered_checker(example, strings)
    lines = example.splitlines()
    for line in lines:
        if r"C:\Users" in line:
            assert r"C:\Users\XXX" + "\\" in line, "username should be XXX"

        if r"AppData\Local" in line:
            assert r"AppData\Local\Temp\YYY" + "\\" in line, "tmpdir should be YYY"

    assert "ZZZ>" in example, "object addresses replaced with ZZZ."
    assert "at 0x" not in example, "object addresses replaced with ZZZ."
