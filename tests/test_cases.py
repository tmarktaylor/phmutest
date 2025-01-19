"""Tests for cases.py and other source files to provide code coverage."""

import contextlib
import io
import textwrap
import unittest

import phmutest.cases
import phmutest.fillin
import phmutest.main
import phmutest.subtest
import phmutest.summary

# indexes to log file entry
DOC_LOCATION = phmutest.printer.DOC_LOCATION
RESULT = phmutest.printer.RESULT
REASON = phmutest.printer.REASON


def test_chop_final_newline():
    """Call with text that does not end with newline."""
    text = textwrap.dedent(
        """\
        Deselected blocks:
        tests/md/code_groups.md:4
        tests/md/code_groups.md:9
        tests/md/code_groups.md:15"""
    )
    chopped_text = phmutest.fillin.chop_final_newline(text)
    assert chopped_text == text

    text2 = text + "\n"
    chopped_text2 = phmutest.fillin.chop_final_newline(text2)
    assert chopped_text2 == text


def test_no_files():
    """Run with no files specified on the command line."""
    # This covers the cases.py line near the end: test_classes += "\n"
    line = "--log"
    phmresult = phmutest.main.command(line)
    want = phmutest.summary.Metrics(
        number_blocks_run=0,
        passed=0,
        failed=0,
        skipped=0,
        suite_errors=0,
        number_of_files=0,
        files_with_no_blocks=0,
        number_of_deselected_blocks=0,
    )
    assert want == phmresult.metrics
    assert phmresult.is_success is True


def test_skipif_no_output():
    """Source Code block with no output and skipif directive. Empty Python block."""
    line = "tests/md/cases.md --log"
    phmresult = phmutest.main.command(line)
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
    assert phmresult.is_success is True
    assert isinstance(phmresult.test_program, unittest.TestProgram)


def test_duplicate_filename():
    """Duplicate filename specified on command line and .toml tested once."""
    command = "tests/md/unexpected_output.md --config tests/toml/project.toml --log"
    args = command.split()
    phmresult = phmutest.main.main(args)
    want = phmutest.summary.Metrics(
        number_blocks_run=6,
        passed=4,
        failed=2,
        skipped=1,
        suite_errors=0,
        number_of_files=3,
        files_with_no_blocks=0,
        number_of_deselected_blocks=0,
    )
    assert want == phmresult.metrics
    assert phmresult.is_success is False
    assert isinstance(phmresult.test_program, unittest.TestProgram)


def test_deselected_blocks_report(capsys, endswith_checker):
    """See list of deselected blocks at the end of the report."""
    line = "tests/md/code_groups.md --deselect group-1 group-2 --report"
    phmresult = phmutest.main.command(line)
    assert phmresult is None
    output = capsys.readouterr().out
    expected = """Deselected blocks:
        tests/md/code_groups.md:4
        tests/md/code_groups.md:9
        tests/md/code_groups.md:15
        """
    endswith_checker(expected, output.rstrip())


def test_print_captured_output(startswith_checker):
    """Show captured stdout and stderr when printed by --progress."""
    # Note- While unittest is running Printer prints to stderr.
    # --quiet is passed through to unittest to prevent the progress dot printing.
    # Printing after unittest completes is to stdout.
    line = "tests/md/printer.md --log --progress --quiet"
    with contextlib.redirect_stderr(io.StringIO()) as ferr:
        phmresult = phmutest.main.command(line)
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
    assert phmresult.is_success is False
    assert isinstance(phmresult.test_program, unittest.TestProgram)

    output = ferr.getvalue()
    expected = """tests/md/printer.md:7 ... failed
        === tests/md/printer.md:7 stdout ===
        asserting False...
        === end ===
        === tests/md/printer.md:7 stderr ===
        asserting False...
        === end ===
        tests/md/printer.md:18 ... pass
        tests/md/printer.md:31 ... failed
        === tests/md/printer.md:31 stdout ===
        (10, 1)
        === end ===
        tests/md/printer.md:46 ... skip   phmutest-skip
        """
    startswith_checker(expected, output)
    ferr.close()


def test_skip_progress():
    """Test --progress printing with skips has no UnboundLocalError for sys."""
    # This test exposed an issue with UnboundLocalError for sys when using
    # sys.stderr for verbose printing of a skipped block.
    # See src/phmutest/skip.py::make_replacements().
    line = "tests/md/directive1.md --log --progress"
    phmresult = phmutest.main.command(line)
    want = phmutest.summary.Metrics(
        number_blocks_run=3,
        passed=2,
        failed=1,
        skipped=1,
        suite_errors=0,
        number_of_files=1,
        files_with_no_blocks=0,
        number_of_deselected_blocks=0,
    )
    assert want == phmresult.metrics
    assert phmresult.is_success is False


def test_setup_module_progress():
    """Test --progress printing in setUpModule has no UnboundLocalError for sys."""
    line = (
        "docs/setup/across1.md docs/setup/across2.md"
        " --setup-across-files docs/setup/across1.md --log --progress"
    )
    phmresult = phmutest.main.command(line)
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
    assert phmresult.is_success is True


def test_setup_no_teardown(capsys):
    """Run setup without teardown and check the log."""
    line = "tests/md/setupnoteardown.md --log -f"
    phmresult = phmutest.main.command(line)
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
    assert phmresult.is_success is True
    assert isinstance(phmresult.test_program, unittest.TestProgram)
    assert "tests/md/setupnoteardown.md:11 setup" in phmresult.log[0][DOC_LOCATION]
    assert "tests/md/setupnoteardown.md:17 setup" in phmresult.log[1][DOC_LOCATION]
    assert "tests/md/setupnoteardown.md:29" in phmresult.log[2][DOC_LOCATION]
    assert "tests/md/setupnoteardown.md:48" in phmresult.log[3][DOC_LOCATION]
    assert "tests/md/setupnoteardown.md:52" in phmresult.log[4][DOC_LOCATION]


def test_setup_across_no_teardown(capsys):
    """Run the setup across files."""
    line = (
        "tests/md/setupnoteardown.md tests/md/setupto.md --log "
        "--setup-across-files tests/md/setupnoteardown.md"
    )
    phmresult = phmutest.main.command(line)
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
    assert phmresult.is_success is True
    assert isinstance(phmresult.test_program, unittest.TestProgram)
    assert "setUpModule" in phmresult.log[0][DOC_LOCATION]
    assert "tests/md/setupnoteardown.md:11" in phmresult.log[1][DOC_LOCATION]
    assert "tests/md/setupnoteardown.md:17" in phmresult.log[2][DOC_LOCATION]
    assert "tests/md/setupnoteardown.md:29" in phmresult.log[3][DOC_LOCATION]
    assert "tests/md/setupnoteardown.md:48" in phmresult.log[4][DOC_LOCATION]
    assert "tests/md/setupnoteardown.md:52" in phmresult.log[5][DOC_LOCATION]
    assert "tests/md/setupto.md:7" in phmresult.log[6][DOC_LOCATION]
    assert "tearDownModule" in phmresult.log[7][DOC_LOCATION]


def test_setup_across_share_across(capsys):
    """Run the setup+share across files."""
    line = "--log --config tests/toml/acrossfiles.toml"
    phmresult = phmutest.main.command(line)
    want = phmutest.summary.Metrics(
        number_blocks_run=7,
        passed=7,
        failed=0,
        skipped=0,
        suite_errors=0,
        number_of_files=2,
        files_with_no_blocks=0,
        number_of_deselected_blocks=0,
    )
    assert want == phmresult.metrics
    assert phmresult.is_success is True
    assert isinstance(phmresult.test_program, unittest.TestProgram)
    assert "setUpModule" in phmresult.log[0][DOC_LOCATION]
    assert "tests/md/setupnoteardown.md:11 setup" in phmresult.log[1][DOC_LOCATION]
    assert "tests/md/setupnoteardown.md:17 setup" in phmresult.log[2][DOC_LOCATION]
    assert "tests/md/setupnoteardown.md:29" in phmresult.log[3][DOC_LOCATION]
    assert "tests/md/setupnoteardown.md:48" in phmresult.log[4][DOC_LOCATION]
    assert "tests/md/setupnoteardown.md:52" in phmresult.log[5][DOC_LOCATION]
    assert "tests/md/sharedto.md:7" in phmresult.log[6][DOC_LOCATION]
    assert "tests/md/sharedto.md:26" in phmresult.log[7][DOC_LOCATION]
    assert "tearDownModule" in phmresult.log[8][DOC_LOCATION]


def test_share_across_with_setup(capsys):
    """Share across files a .md file that has (un-shared) setup blocks."""
    line = "--log --config tests/toml/acrossfiles2.toml"
    phmresult = phmutest.main.command(line)
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
    assert phmresult.is_success is True
    assert isinstance(phmresult.test_program, unittest.TestProgram)
    assert "setUpModule" in phmresult.log[0][DOC_LOCATION]
    assert "tests/md/setupnoteardown.md:11 setup" in phmresult.log[1][DOC_LOCATION]
    assert "tests/md/setupnoteardown.md:17 setup" in phmresult.log[2][DOC_LOCATION]
    assert "tests/md/setupnoteardown.md:29" in phmresult.log[3][DOC_LOCATION]
    assert "tests/md/setupnoteardown.md:48" in phmresult.log[4][DOC_LOCATION]
    assert "tests/md/setupnoteardown.md:52" in phmresult.log[5][DOC_LOCATION]
    assert "tests/md/sharedto2.md:13" in phmresult.log[6][DOC_LOCATION]
    assert "tearDownModule" in phmresult.log[7][DOC_LOCATION]


def test_progress_option():
    """Check stderr printing by the --progress command line option."""
    # Note- Printing by unittest while a test is running goes to stderr.
    # Note- Printing by the phmutest generated testfile should go to stderr.
    # Using homemade stderr capture since not seeing it from pytest's
    # capsys.readouterr().err.
    with contextlib.redirect_stderr(io.StringIO()) as err:
        line = (
            "docs/fix/code/chdir.md --fixture docs.fix.code.chdir.change_dir --progress"
        )
        phmresult = phmutest.main.command(line)
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
        assert phmresult.is_success is True
        assert isinstance(phmresult.test_program, unittest.TestProgram)

        lines = err.getvalue().splitlines()
        assert "setUpModule()..." in lines[0]
        assert "leaving setUpModule." in lines[1]
        assert "docs/fix/code/chdir.md:24 ... pass" in lines[2]
        assert "docs/fix/code/chdir.md:28 ... pass" in lines[3]
        assert "tearDownModule()..." in lines[4]
        assert "leaving tearDownModule." in lines[5]
    err.close()
