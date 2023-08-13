"""Tests for cases.py and other source files to provide code coverage."""
import contextlib
import io
import textwrap
import unittest

import phmutest.cases
import phmutest.main
import phmutest.subtest


def test_chop_final_newline():
    """Call with text that does not end with newline."""
    text = textwrap.dedent(
        """\
        Deselected blocks:
        tests/md/code_groups.md:4
        tests/md/code_groups.md:9
        tests/md/code_groups.md:15"""
    )
    chopped_text = phmutest.subtest.chop_final_newline(text)
    assert chopped_text == text

    text2 = text + "\n"
    chopped_text2 = phmutest.subtest.chop_final_newline(text2)
    assert chopped_text2 == text


def test_deindent():
    """Show leading 4 spaces removed only if present."""
    lines1 = ["    4 indent", "no indent", "        8 indent"]
    text1 = "\n".join(lines1)
    dedented1 = "4 indent\nno indent\n    8 indent"
    assert dedented1 == phmutest.cases.deindent(text1)

    lines2 = ["no indent", "no indent", "   3 indent"]
    text2 = "\n".join(lines2)
    dedented2 = "no indent\nno indent\n   3 indent"
    assert dedented2 == phmutest.cases.deindent(text2)


def test_no_files():
    """Run with no files specified on the command line."""
    # This covers the cases.py line near the end: test_classes += "\n"
    command = "--log"
    phmresult = phmutest.main.main(command.split())
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
    """Source Code block with no ouput and skipif directive. Empty Python block."""
    # This covers the cases.py line near the end: test_classes += "\n"
    command = "tests/md/cases.md --log"
    phmresult = phmutest.main.main(command.split())
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
    command = "tests/md/code_groups.md --deselect group-1 group-2 --report"
    phmresult = phmutest.main.main(command.split())
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
    command = "tests/md/printer.md --log --progress --quiet"
    with contextlib.redirect_stderr(io.StringIO()) as ferr:
        phmresult = phmutest.main.main(command.split())
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
    expected = """tests/md/printer.md:6 ... failed
        === phmutest: captured stdout ===
        asserting False...
        === end ===
        === phmutest: captured stderr ===
        asserting False...
        === end ===
        tests/md/printer.md:17 ... pass
        tests/md/printer.md:30 ... failed
        === phmutest: captured stdout ===
        (10, 1)
        === end ===
        tests/md/printer.md:42 ... skip   phmutest-skip
        """
    startswith_checker(expected, output)
    ferr.close()


def test_skip_progress():
    """Test --progress printing with skips has no UnboundLocalError for sys."""
    # This test exposed an issue with UnboundLocalError for sys when using
    # sys.stderr for verbose printing of a skipped block.
    # See src/phmutest/skip.py::make_replacements().
    command = "tests/md/directive1.md --log --progress"
    phmresult = phmutest.main.main(command.split())
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
    command = (
        "docs/setup/across1.md docs/setup/across2.md"
        " --setup-across-files docs/setup/across1.md --log --progress"
    )
    phmresult = phmutest.main.main(command.split())
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
    command = "tests/md/setupnoteardown.md --log -f"
    phmresult = phmutest.main.main(command.split())
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
    assert "tests/md/setupnoteardown.md:10 setup" in phmresult.log[0][0]
    assert "tests/md/setupnoteardown.md:14 setup" in phmresult.log[1][0]
    assert "tests/md/setupnoteardown.md:26" in phmresult.log[2][0]
    assert "tests/md/setupnoteardown.md:42" in phmresult.log[3][0]
    assert "tests/md/setupnoteardown.md:46" in phmresult.log[4][0]


def test_setup_across_no_teardown(capsys):
    """Run the setup across files example and check the log."""
    command = (
        "tests/md/setupnoteardown.md tests/md/setupto.md --log "
        "--setup-across-files tests/md/setupnoteardown.md"
    )
    phmresult = phmutest.main.main(command.split())
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
    assert "setUpModule" in phmresult.log[0][0]
    assert "tests/md/setupnoteardown.md:10" in phmresult.log[1][0]
    assert "tests/md/setupnoteardown.md:14" in phmresult.log[2][0]
    assert "tests/md/setupnoteardown.md:26" in phmresult.log[3][0]
    assert "tests/md/setupnoteardown.md:42" in phmresult.log[4][0]
    assert "tests/md/setupnoteardown.md:46" in phmresult.log[5][0]
    assert "tests/md/setupto.md:7" in phmresult.log[6][0]
    assert "tearDownModule" in phmresult.log[7][0]


def test_setup_across_share_across(capsys):
    """Run the setup across files example and check the log."""
    command = "--log --config tests/toml/acrossfiles.toml"
    phmresult = phmutest.main.main(command.split())
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
    assert "setUpModule" in phmresult.log[0][0]
    assert "tests/md/setupnoteardown.md:10 setup" in phmresult.log[1][0]
    assert "tests/md/setupnoteardown.md:14 setup" in phmresult.log[2][0]
    assert "tests/md/setupnoteardown.md:26" in phmresult.log[3][0]
    assert "tests/md/setupnoteardown.md:42" in phmresult.log[4][0]
    assert "tests/md/setupnoteardown.md:46" in phmresult.log[5][0]
    assert "tests/md/sharedto.md:7" in phmresult.log[6][0]
    assert "tests/md/sharedto.md:24" in phmresult.log[7][0]
    assert "tearDownModule" in phmresult.log[8][0]


def test_share_across_with_setup(capsys):
    """Share across files a .md file that has (un-shared) setup blocks."""
    command = "--log --config tests/toml/acrossfiles2.toml"
    phmresult = phmutest.main.main(command.split())
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
    assert "setUpModule" in phmresult.log[0][0]
    assert "tests/md/setupnoteardown.md:10 setup" in phmresult.log[1][0]
    assert "tests/md/setupnoteardown.md:14 setup" in phmresult.log[2][0]
    assert "tests/md/setupnoteardown.md:26" in phmresult.log[3][0]
    assert "tests/md/setupnoteardown.md:42" in phmresult.log[4][0]
    assert "tests/md/setupnoteardown.md:46" in phmresult.log[5][0]
    assert "tests/md/sharedto2.md:13" in phmresult.log[6][0]
    assert "tearDownModule" in phmresult.log[7][0]


def test_progress_option():
    """Check stderr printing by the --progress command line option."""
    # Note- Printing by unittest while a test is running goes to stderr.
    # Note- Printing by the phmutest generated testfile should go to stderr.
    # Using homemade stderr capture since not seeing it from pytest's
    # capsys.readouterr().err.
    with contextlib.redirect_stderr(io.StringIO()) as err:
        command = (
            "docs/fix/code/chdir.md --fixture docs.fix.code.chdir.change_dir --progress"
        )
        phmresult = phmutest.main.main(command.split())
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
        assert "docs/fix/code/chdir.md:25 ... pass" in lines[2]
        assert "docs/fix/code/chdir.md:29 ... pass" in lines[3]
        assert "tearDownModule()..." in lines[4]
        assert "leaving tearDownModule." in lines[5]
    err.close()
