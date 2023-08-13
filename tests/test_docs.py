"""pytest tests for README.md and other Markdown doc files."""
import contextlib
import re
import textwrap
from io import StringIO
from pathlib import Path
from typing import List

import phmutest.main
import phmutest.summary
import phmutest.tool
from docs.quicklinks import make_quick_links

# Note- unittest appears to be printing to stderr when it is running
#       the generated test file when called from Python.
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
    """Get the first FCB that starts with 'phmutest' and same for 'summary'."""
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
    """Get the first FCB that starts with 'phmutest' and same for 'log'."""
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


def test_readme_metrics():
    """Test the blocks status when running on README.md."""
    command, output = get_command_and_log("README.md")
    args = arg_list(command)
    phmresult = phmutest.main.main(args)
    want = phmutest.summary.Metrics(
        number_blocks_run=3,
        passed=3,
        failed=0,
        skipped=0,
        suite_errors=0,
        number_of_files=1,
        files_with_no_blocks=0,
        number_of_deselected_blocks=0,
    )
    assert want == phmresult.metrics


def test_readme_output(capsys):
    """Test the expected output block when running on README.md."""
    command, output = get_command_and_log("README.md")
    args = arg_list(command)
    _ = phmutest.main.main(args)
    assert output == capsys.readouterr().out.lstrip()


def test_call_from_python():
    """Show call from Python statements in Markdown FCB is the same as in the code."""
    chooser = phmutest.tool.FCBChooser("docs/callfrompython.md")
    example = chooser.contents("call-from-python")
    assert example
    indented_example = textwrap.indent(example, "    ")
    text = Path("tests/test_examples.py").read_text(encoding="utf-8")
    assert indented_example in text, "changed in the python file?"


def test_phmresult():
    """Show PhmResult dataclass in Markdown FCB is the same as in the code."""
    chooser = phmutest.tool.FCBChooser("docs/callfrompython.md")
    example = chooser.contents("phmresult")
    assert example
    text = Path("src/phmutest/summary.py").read_text(encoding="utf-8")
    assert example in text, "changed in the python file?"


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


def test_fixture_chdir_example():
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


def test_fixture_drink_example():
    """Test --fixture example that acquires/releases resource in --replmode."""
    command, output = get_command_and_log("docs/fix/repl/drink.md")
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


def test_replmode_example(capsys):
    """Test sample showing how to run doctests in Markdown files."""
    command, output = get_command_and_log("docs/replmode.md")
    args = arg_list(command)
    phmresult = phmutest.main.main(args)
    want = phmutest.summary.Metrics(
        number_blocks_run=3,
        passed=3,
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
    # args = ["docs/advanced/skip.md"]
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
    expected_std_err = """\
.
----------------------------------------------------------------------
Ran 1 test in 0.000s

OK
"""
    assert expected_std_err == ferr.getvalue()
    assert output == fout.getvalue().lstrip()


def extract_usage_options(text):
    """From --help output get a set of the usage option names."""
    finder = re.finditer(
        pattern=r"[-][-][a-z][\-A-Z_a-z]*", string=text, flags=re.MULTILINE | re.DOTALL
    )
    option_mentions = [m.group() for m in finder]
    return set(option_mentions)


def test_usage_options():
    """Expose added/removed/renamed options that didn't get documented in README.md."""
    # Check usage options in the README FCB against argparser's help text.
    # Tolerate minor formatting changes in argparse help output between
    # Python major and minor versions.
    readme_fcbs = phmutest.tool.FCBChooser("README.md")
    # This string must be present verbatim in at most one FCB in README.md.
    identify_usage_fcb = (
        "Detect broken Python examples in Markdown. "
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


def test_quick_links():
    """Make sure the README.md quick links are up to date."""
    filename = "README.md"
    readme = Path("README.md").read_text(encoding="utf-8")
    github_links = make_quick_links(filename)
    # There must be at least one blank line after the last link.
    assert github_links + "\n\n" in readme
