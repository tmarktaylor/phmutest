"""Check the traceback for some Markdown with broken examples."""

import sys

import pytest

import phmutest.config
import phmutest.main
import phmutest.summary
import phmutest.tool
from phmutest.printer import DOC_LOCATION, EXCEPTION_LINE, REASON, RESULT, TRACE, Log

traceback_extra = False
try:
    import stackprinter  # noqa: F401

    traceback_extra = True
except ModuleNotFoundError:  # pragma: no cover
    pass


def check_exception_line_numbers(log: Log):
    # Check that the exception line numbers in the log for the
    # FCBs that propagated an exception or are present in the traceback log entries.
    # FCBs that fail the expected output check will not have a TRACE log entry.
    # This should fail if a different line number is reported in the
    # traceback than what was reported in the log entry.
    elines = []
    for e in log:
        # See printer.cancel_print_capture_on_error().
        if e[DOC_LOCATION].endswith(" o"):  # expected output check?
            continue  # yes-
        elif e[RESULT] in ["failed", "error"]:
            elines.append(e[EXCEPTION_LINE])

    traces = [e[REASON] for e in log if e[RESULT] == TRACE]
    assert elines
    assert traces
    for line, trace in zip(elines, traces):
        assert f", line {line}, in" in trace


def test_ordered_checker_miss(ordered_checker):
    """Show ordered_checker fixture detects a missing line."""
    with pytest.raises(AssertionError):
        ordered_checker(
            got="line1\nline2\nline3", substrings=["line1", "bogus", "line3"]
        )


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
        ">   43",
        ", line 34, in tests",
        "--> 34",
        "pass_bot.inquire",
        ">   55",
        ", line 40, in tests",
        ", line 32, in ask",
        "--> 32",
        "question = 'What floats?'",
        "ValueError: What was the question?",
        "+ Incorrect expected output.",
        ">   75",
        ", line 58, in tests",
        "--> 58",
        "answer = 'very small rocks'",
    ]
    ordered_checker(output, strings)
    check_exception_line_numbers(results.log)


@pytest.mark.skipif(not traceback_extra, reason="Requires install extra [traceback].")
@pytest.mark.skipif(sys.version_info > (3, 12), reason="Skip py 3.12+")
def test_traceback_md(capsys, ordered_checker):
    """Test the stackprinter traceback printed when running on tracer.md."""
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
