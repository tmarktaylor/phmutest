"""pytest tests for README.md and other Markdown doc files. Suggest pytest -vv."""

import contextlib
import re
import string
import sys
import textwrap
from io import StringIO
from pathlib import Path
from typing import List
from unittest import mock

import pytest

import phmutest.config
import phmutest.fcb
import phmutest.main
import phmutest.summary
import phmutest.tool
from docs.navlinks import make_nav_links
from docs.quicklinks import make_quick_links
from phmutest.printer import EXCEPTION_LINE, RESULT

# Note- unittest appears to be printing to stderr when it is running
#       the generated testfile when called from Python.
#       For example typing this command line in a bash shell
#           phmutest docs/group/select.md --select slow --log
#       produces:
#
#       .
#       ----------------------------------------------------------------------
#       Ran 1 test in 0.000s
#
#       OK
#       ...
#
#       phmutest does the printing after the OK to stdout.
#       The test cases here check only the stdout.


def get_command_and_output(markdown_filename: str) -> List[str]:
    """Get the last FCB that starts with 'phmutest' and same for 'summary'."""
    command = ""
    output = ""
    content_strings = phmutest.tool.fenced_code_blocks(markdown_filename)
    content_strings.reverse()
    for s in content_strings:
        if s.startswith("phmutest"):
            command = s
        if s.startswith("summary:"):
            output = s
    return command, output


def get_command_and_log(markdown_filename: str) -> List[str]:
    """Get the last FCB that starts with 'phmutest' and same for 'log'."""
    command = ""
    output = ""
    content_strings = phmutest.tool.fenced_code_blocks(markdown_filename)
    content_strings.reverse()
    for s in content_strings:
        if s.startswith("phmutest"):
            command = s
        if s.startswith("log:"):
            output = s
    return command, output


def arg_list(command_line: str) -> List[str]:
    """Convert a phmutest command line to list of strings to pass to main()."""
    args = command_line.split()
    args.remove("phmutest")
    return args


def test_setup_example(capsys):
    """Test setup and teardown directives."""
    command, output = get_command_and_log("docs/setup/setup.md")
    args = arg_list(command)
    phmresult = phmutest.main.main(args)
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
    assert output == capsys.readouterr().out.lstrip()


readme_chooser = phmutest.tool.FCBChooser("README.md")
"""Helper to select lists of FCB contents from the Markdown file."""


NUM_README_ERROR = 2
"""Number of Python code FCBs in README.md broken example that raise an exception."""


NUM_README_FAILED = 2
"""Number of Python code FCBs in README.md broken example that log as 'failed'."""


def test_readme_code_metrics():
    """Test the metrics when running on README.md."""
    command = readme_chooser.select(info_string="shell")[0]  # 1st of selected FCBs
    args = arg_list(command)
    phmresult = phmutest.main.main(args)
    want = phmutest.summary.Metrics(
        number_blocks_run=6,
        passed=2,
        failed=NUM_README_FAILED,
        skipped=0,
        suite_errors=NUM_README_ERROR,
        number_of_files=1,
        files_with_no_blocks=0,
        number_of_deselected_blocks=0,
    )
    assert want == phmresult.metrics


@pytest.mark.skipif(sys.version_info > (3, 12), reason="Skip py 3.12+")
def test_readme_code_output(capsys):
    """Test the 'phmutest stdout' FCB in README.md.

    Run without showing the extra [traceback] tracebacks for broken FCBs.
    Test the exception line numbers in the 'unittest stderr' FCB in README.md.
    """
    with mock.patch("phmutest.fcb.SHOW_TRACEBACK", False):
        # first of selected FCBs
        command = readme_chooser.select(info_string="shell")[0]
        assert len(command)
        output = readme_chooser.select(contains="args.files: 'README.md'")[0]
        assert len(output)
        args = arg_list(command)
        results = phmutest.main.main(args)
        captured_output = capsys.readouterr().out.lstrip()
    assert output == captured_output

    # Check the example unittest tracebacks.
    # Check that the exception line numbers in the log for the
    # "failed" and "error" entries are present in the README.md
    # FCB showing the tracebacks unittest printed to stderr.
    # If this test fails the example unittest traceback may be stale.
    log = results.log
    elines = [e[EXCEPTION_LINE] for e in log if e[RESULT] in ["failed", "error"]]
    assert len(elines)
    txt_fcbs = readme_chooser.select(info_string="txt")
    stderr_fcb = txt_fcbs[1]  # This is the FCB with the unittest tracebacks
    assert len(stderr_fcb)
    for line in elines:
        assert f", line {line}, in" in stderr_fcb, f"README is missing line {line}"


@pytest.mark.skipif(sys.version_info > (3, 12), reason="Skip py 3.12+")
def test_readme_stderr():
    """Test the 'phmutest stderr' FCB in README.md.

    Check the unittest output stderr FCB is consistent with the log FCB.
    Check that user name and tmpdir name are sanitized.
    """
    txt_fcbs = readme_chooser.select(info_string="txt")
    log_fcb = txt_fcbs[0]
    stderr_fcb = txt_fcbs[1]
    # Check that username and the tempdir name are replaced.
    lines = stderr_fcb.splitlines()
    for line in lines:
        if r"C:\Users" in line:
            assert r"C:\Users\XXX" + "\\" in line, "username should be XXX"

        if r"AppData\Local" in line:
            assert r"AppData\Local\Temp\YYY" + "\\" in line, "tmpdir should be YYY"

    # Check the log testfile ERROR: line numbers in the log FCB in parenthesis
    # are all present in the stderr FCB as ",line NN, in tests".
    num_errors = log_fcb.count("error   ")
    assert num_errors == NUM_README_ERROR


replexample_chooser = phmutest.tool.FCBChooser("docs/repl/REPLexample.md")
"""Helper to select lists of FCB contents from the Markdown file."""


def test_replexample_metrics():
    """Test the metrics when running on docs/repl/REPLexample.md."""
    command = replexample_chooser.select(info_string="shell")[0]
    args = arg_list(command)
    phmresult = phmutest.main.main(args)
    want = phmutest.summary.Metrics(
        number_blocks_run=6,
        passed=3,
        failed=1,
        skipped=0,
        suite_errors=2,  # counts all lines that raise exceptions
        number_of_files=1,
        files_with_no_blocks=0,
        number_of_deselected_blocks=0,
    )
    assert want == phmresult.metrics


NUM_REPL_ERROR = 2
"""Number of Python REPL FCBs in REPLexample.md that raise an exception."""


@pytest.mark.skipif(sys.version_info > (3, 12), reason="Skip py 3.12+")
def test_replexample(capsys, endswith_checker):
    """Check expected output block in the example docs/repl/REPLexample.md."""
    command = replexample_chooser.select(info_string="shell")[0]
    expected_output = replexample_chooser.select(info_string="txt")[0]
    start = expected_output.index("summary:\nmetric")
    doctests = expected_output[:start]
    summary_log = expected_output[start:]
    args = arg_list(command)
    _ = phmutest.main.main(args)

    # Check that username is replaced.
    lines = doctests.splitlines()
    for line in lines:
        if r"C:\Users" in line:
            assert r"C:\Users\XXX" + "\\" in line, "username should be XXX"

    # Check the result "error" reason line numbers in the --log part
    # are all present in the doctest printing.
    num_errors = summary_log.count("error   ")
    assert num_errors == NUM_REPL_ERROR

    # check line NN in ask is the raise ValueError... in answerlib.py
    all_answerlib_lineno = re.findall(
        r'answerlib.py", line (\d+)[,]', doctests, flags=re.DOTALL | re.MULTILINE
    )
    assert len(all_answerlib_lineno) == 1
    answerlib_lineno = int(all_answerlib_lineno[0])
    text = Path("docs/answerlib.py").read_text(encoding="utf-8")
    lines = list(text.splitlines())
    assert "raise ValueError" in lines[answerlib_lineno - 1]

    # Check the summary and log at the end of the example
    got = capsys.readouterr().out.strip()
    endswith_checker(summary_log, got)


def test_main_call_api():
    """Show main.main in Markdown FCB is the same as in the code."""
    chooser = phmutest.tool.FCBChooser("docs/callfrompython.md")
    fcb = chooser.contents("api-main")
    assert fcb
    text = Path("src/phmutest/main.py").read_text(encoding="utf-8")
    assert "\n\n" + fcb in text, "changed in the python file?"


def test_command_call_api():
    """Show main.main in Markdown FCB is the same as in the code."""
    chooser = phmutest.tool.FCBChooser("docs/callfrompython.md")
    fcb = chooser.contents("api-command")
    assert fcb
    text = Path("src/phmutest/main.py").read_text(encoding="utf-8")
    assert "\n\n" + fcb in text, "changed in the python file?"


def test_phmresult():
    """Show PhmResult dataclass in Markdown FCB is the same as in the code."""
    chooser = phmutest.tool.FCBChooser("docs/callfrompython.md")
    example = chooser.contents("phmresult")
    assert example
    text = Path("src/phmutest/summary.py").read_text(encoding="utf-8")
    assert example + "\n\n" in text, "changed in the python file?"


def test_call_from_python():
    """Show call from Python statements in Markdown FCB is the same as in the code."""
    chooser = phmutest.tool.FCBChooser("docs/callfrompython.md")
    example = chooser.contents("call-from-python")
    assert example
    indented_example = textwrap.indent(example, "    ")
    text = Path("tests/test_examples.py").read_text(encoding="utf-8")
    assert indented_example in text, "changed in the python file?"


def test_fixture_globs_example(capsys):
    """Test --fixture example that initializes globals."""
    command, output = get_command_and_log("docs/fix/code/globdemo.md")
    args = arg_list(command)
    phmresult = phmutest.main.main(args)
    want = phmutest.summary.Metrics(
        number_blocks_run=1,
        passed=1,
        failed=0,
        skipped=0,
        suite_errors=0,
        number_of_files=1,
        files_with_no_blocks=0,
        number_of_deselected_blocks=0,
    )
    assert want == phmresult.metrics
    assert output == capsys.readouterr().out.lstrip()


def test_fixture_chdir_example(capsys):
    """Test --fixture example that changes current working directory."""
    command, output = get_command_and_log("docs/fix/code/chdir.md")
    args = arg_list(command)
    phmresult = phmutest.main.main(args)
    want = phmutest.summary.Metrics(
        number_blocks_run=2,
        passed=2,
        failed=0,
        skipped=0,
        suite_errors=0,
        number_of_files=1,
        files_with_no_blocks=0,
        number_of_deselected_blocks=0,
    )
    assert want == phmresult.metrics
    assert output == capsys.readouterr().out.lstrip()


def test_fixture_drink_example(capsys):
    """Test --fixture example that acquires/releases resource in --replmode."""
    command, _ = get_command_and_log("docs/fix/repl/drink.md")
    # The expected output is the last FCB in the file.
    content_strings = phmutest.tool.fenced_code_blocks("docs/fix/repl/drink.md")
    output = content_strings[-1]
    args = arg_list(command)
    phmresult = phmutest.main.main(args)
    want = phmutest.summary.Metrics(
        number_blocks_run=2,
        passed=2,
        failed=0,
        skipped=0,
        suite_errors=0,
        number_of_files=1,
        files_with_no_blocks=0,
        number_of_deselected_blocks=0,
    )
    assert want == phmresult.metrics
    assert output == capsys.readouterr().out.lstrip()


def test_replmode_example(capsys):
    """Test sample showing how to run doctests in Markdown files."""
    command, output = get_command_and_log("docs/replmode.md")
    args = arg_list(command)
    phmresult = phmutest.main.main(args)
    want = phmutest.summary.Metrics(
        number_blocks_run=4,
        passed=4,
        failed=0,
        skipped=0,
        suite_errors=0,
        number_of_files=1,
        files_with_no_blocks=0,
        number_of_deselected_blocks=0,
    )
    assert want == phmresult.metrics
    assert output == capsys.readouterr().out.lstrip()


def test_share_across_files_example(capsys):
    """Run the share across files example and check the output against the FCB."""
    command, output = get_command_and_output("docs/share/share_demo.md")
    args = arg_list(command)
    phmresult = phmutest.main.main(args)
    want = phmutest.summary.Metrics(
        number_blocks_run=8,
        passed=8,
        failed=0,
        skipped=0,
        suite_errors=0,
        number_of_files=3,
        files_with_no_blocks=0,
        number_of_deselected_blocks=0,
    )
    assert want == phmresult.metrics
    assert output == capsys.readouterr().out.lstrip()


def test_replmode_share_across_files(capsys):
    """Run the share across files example and check the output against the FCB."""
    command, output = get_command_and_output("docs/repl/replshare_demo.md")
    args = arg_list(command)
    phmresult = phmutest.main.main(args)
    want = phmutest.summary.Metrics(
        number_blocks_run=8,
        passed=8,
        failed=0,
        skipped=0,
        suite_errors=0,
        number_of_files=3,
        files_with_no_blocks=0,
        number_of_deselected_blocks=0,
    )
    assert want == phmresult.metrics
    assert output == capsys.readouterr().out.lstrip()


def test_setup_across_files_example(capsys):
    """Run the setup across files example and check the output against the FCB."""
    command, output = get_command_and_log("docs/setup/across1.md")
    args = arg_list(command)
    phmresult = phmutest.main.main(args)
    want = phmutest.summary.Metrics(
        number_blocks_run=6,
        passed=6,
        failed=0,
        skipped=0,
        suite_errors=0,
        number_of_files=2,
        files_with_no_blocks=0,
        number_of_deselected_blocks=0,
    )
    assert want == phmresult.metrics
    assert output == capsys.readouterr().out.lstrip()


def test_select_example(capsys):
    """Test --select example."""
    command, output = get_command_and_output("docs/group/select.md")
    args = arg_list(command)
    phmresult = phmutest.main.main(args)
    want = phmutest.summary.Metrics(
        number_blocks_run=1,
        passed=1,
        failed=0,
        skipped=0,
        suite_errors=0,
        number_of_files=1,
        files_with_no_blocks=0,
        number_of_deselected_blocks=1,
    )
    assert phmresult.is_success
    assert want == phmresult.metrics
    assert output == capsys.readouterr().out.lstrip()


def test_deselect_example(capsys):
    """Test --deselect example."""
    command, output = get_command_and_output("docs/group/deselect.md")
    args = arg_list(command)
    phmresult = phmutest.main.main(args)
    want = phmutest.summary.Metrics(
        number_blocks_run=1,
        passed=1,
        failed=0,
        skipped=0,
        suite_errors=0,
        number_of_files=1,
        files_with_no_blocks=0,
        number_of_deselected_blocks=1,
    )
    assert phmresult.is_success
    assert want == phmresult.metrics
    assert output == capsys.readouterr().out.lstrip()


def test_skip_directive_example(capsys):
    """Test skip directive example."""
    command, output = get_command_and_log("docs/advanced/skip.md")
    args = arg_list(command)
    phmresult = phmutest.main.main(args)
    want = phmutest.summary.Metrics(
        number_blocks_run=2,
        passed=2,
        failed=0,
        skipped=1,
        suite_errors=0,
        number_of_files=1,
        files_with_no_blocks=0,
        number_of_deselected_blocks=0,
    )
    assert want == phmresult.metrics
    assert output == capsys.readouterr().out.lstrip()


def test_skipif_directive_example(capsys):
    """Test skipif directive example."""
    command, output = get_command_and_log("docs/advanced/skipif.md")
    args = arg_list(command)
    phmresult = phmutest.main.main(args)
    want = phmutest.summary.Metrics(
        number_blocks_run=0,
        passed=0,
        failed=0,
        skipped=1,
        suite_errors=0,
        number_of_files=1,
        files_with_no_blocks=0,
        number_of_deselected_blocks=0,
    )
    assert want == phmresult.metrics
    assert output == capsys.readouterr().out.lstrip()


def test_label_directive_example(capsys):
    """Test label directive example."""
    command, output = get_command_and_log("docs/advanced/label.md")
    args = arg_list(command)
    phmresult = phmutest.main.main(args)
    want = phmutest.summary.Metrics(
        number_blocks_run=1,
        passed=1,
        failed=0,
        skipped=1,
        suite_errors=0,
        number_of_files=1,
        files_with_no_blocks=0,
        number_of_deselected_blocks=0,
    )
    assert want == phmresult.metrics
    assert output == capsys.readouterr().out.lstrip()


def test_label_directive_anyfcb_example():
    """Test label directive on any FCB example."""
    args = "docs/advanced/labelanyfcb.md --log".split()
    phmresult = phmutest.main.main(args)
    want = phmutest.summary.Metrics(
        number_blocks_run=1,
        passed=1,
        failed=0,
        skipped=0,
        suite_errors=0,
        number_of_files=1,
        files_with_no_blocks=0,
        number_of_deselected_blocks=0,
    )
    assert want == phmresult.metrics


def test_unittest_stderr_printing():
    """Shows that unittest prints to stderr (captured as ferr)."""
    command, output = get_command_and_output("docs/group/deselect.md")
    args = arg_list(command)
    with contextlib.redirect_stdout(StringIO()) as fout:
        with contextlib.redirect_stderr(StringIO()) as ferr:
            phmresult = phmutest.main.main(args)
            want = phmutest.summary.Metrics(
                number_blocks_run=1,
                passed=1,
                failed=0,
                skipped=0,
                suite_errors=0,
                number_of_files=1,
                files_with_no_blocks=0,
                number_of_deselected_blocks=1,
            )
    assert want == phmresult.metrics
    expected_std_err = [
        """\
.
----------------------------------------------------------------------
Ran 1 test in""",
        """

OK
""",
    ]
    assert expected_std_err[0] in ferr.getvalue()
    assert expected_std_err[1] in ferr.getvalue()
    assert output == fout.getvalue().lstrip()


def extract_usage_options(text):
    """From --help output get a set of the usage option names."""

    option_name_finder = (
        # 2 dash
        r"[-]{2}"
        # mix of dash | letter | number | underscore
        r"[\-A-Za-z0-9_]*"
    )
    """This won't find options with the other punctuation characters."""
    option_mentions = re.findall(
        pattern=option_name_finder, string=text, flags=re.MULTILINE | re.DOTALL
    )
    return set(option_mentions)


def test_usage_options():
    """Expose added/removed/renamed options that didn't get documented in README.md."""
    # Check usage options in the README FCB against argparser's help text.
    # Tolerate minor formatting changes in argparse help output between
    # Python major and minor versions.
    # Note- Does not check the help descriptions or the nargs indications in the usage
    # part.
    readme_fcbs = phmutest.tool.FCBChooser("README.md")
    # This string must be present verbatim in at most one FCB in README.md.
    identify_usage_fcb = (
        "Detect and troubleshoot broken Python examples in Markdown. "
        "Accepts relevant unittest options."
    )
    usage_fcbs = readme_fcbs.select(contains=identify_usage_fcb)
    assert len(usage_fcbs) == 1, "No substring in an FCB or found in more than one FCB."
    usage = usage_fcbs[0]
    fcb_options = extract_usage_options(usage)
    help = phmutest.main.main_argparser().format_help()
    help_options = extract_usage_options(help)
    assert fcb_options, "non-empty"
    assert help_options, "non-empty"
    assert fcb_options == help_options


@pytest.mark.skip("Minor version specific. Run manually on py 3.11.")
def test_usage_text_exactly():  # pragma: no cover
    """Check exact --help text documented in README.md."""
    readme_fcbs = phmutest.tool.FCBChooser("README.md")
    # This string must be present verbatim in at most one FCB in README.md.
    identify_usage_fcb = (
        "Detect and troubleshoot broken Python examples in Markdown. "
        "Accepts relevant unittest options."
    )
    usage_fcbs = readme_fcbs.select(contains=identify_usage_fcb)
    assert len(usage_fcbs) == 1, "No substring in an FCB or found in more than one FCB."
    usage = usage_fcbs[0]
    # Collapse whitespace.
    for c in string.whitespace:
        usage = usage.replace(c, "")
    help = phmutest.main.main_argparser().format_help()
    for c in string.whitespace:
        help = help.replace(c, "")
    assert usage, "non-empty"
    assert help, "non-empty"
    assert usage == help


def test_quick_links():
    """Make sure the README.md quick links are up to date."""
    filename = "README.md"
    readme = Path(filename).read_text(encoding="utf-8")
    github_links = make_quick_links(filename)
    # There must be at least one blank line after the last link.
    assert github_links + "\n\n" in readme


def test_nav_links():
    """Make sure the docs/demos.md links are up to date."""
    want = make_nav_links()
    got = Path("docs/demos.md").read_text(encoding="utf-8")
    assert want == got
