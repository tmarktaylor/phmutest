"""Test runs calling phmutest.main.main() from Python with command line arguments."""

import phmutest.main
import phmutest.summary

# indexes to log file entry
DOC_LOCATION = phmutest.printer.DOC_LOCATION
RESULT = phmutest.printer.RESULT
REASON = phmutest.printer.REASON


def test_sample():
    """Run Python code block with expected output block in project.md."""
    line = "tests/md/project.md"
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


def test_sample_replmode():
    """Run Python interactive sessions (doctests) in project.md."""
    line = "tests/md/project.md --replmode"
    phmresult = phmutest.main.command(line)
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
    assert phmresult.is_success is True


def test_phmdoctest_example1():
    """Run Python code block with expected output block in example1.md."""
    line = "tests/md/example1.md"
    phmresult = phmutest.main.command(line)
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
    assert phmresult.is_success is True


def test_example2():
    """Run Python code block with expected output block in example2.md."""
    line = "tests/md/example2.md"
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


def test_exmple2_replmode():
    """Run Python interactive sessions (doctests) in example2.md."""
    line = "tests/md/example2.md --replmode"
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


def test_directive1():
    """Test label, skip, and skipif directives on code blocks."""
    line = "tests/md/directive1.md"
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
    assert "phmutest-skip" in phmresult.log[0][REASON]
    assert "expected-failed" in phmresult.log[2][DOC_LOCATION]


def test_directive1_replmode():
    """Test label, skip, and skipif directives on session blocks."""
    line = "tests/md/directive1.md --replmode"
    phmresult = phmutest.main.command(line)
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
    assert phmresult.is_success is True
    assert "phmutest-skip" in phmresult.log[0][REASON]
    assert "tests/md/directive1.md:78" in phmresult.log[1][DOC_LOCATION]
    assert "doctest_print_coffee" in phmresult.log[1][DOC_LOCATION]


def test_directive2():
    """Test single setup and teardown directives on code blocks."""
    line = "tests/md/directive2.md"
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
    assert "setup" in phmresult.log[0][DOC_LOCATION]
    assert "teardown" in phmresult.log[4][DOC_LOCATION]


def test_blank_output_lines():
    """Embedded blank lines in Python code expected output block."""
    line = "tests/md/output_has_blank_lines.md"
    phmresult = phmutest.main.command(line)
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
    assert phmresult.is_success is True


def test_no_code_blocks():
    """Test file with no Python FCBs."""
    line = "tests/md/no_code_blocks.md"
    phmresult = phmutest.main.command(line)
    want = phmutest.summary.Metrics(
        number_blocks_run=0,
        passed=0,
        failed=0,
        skipped=0,
        suite_errors=0,
        number_of_files=1,
        files_with_no_blocks=1,
        number_of_deselected_blocks=0,
    )
    assert want == phmresult.metrics
    assert phmresult.is_success is True
    assert "noblocks" in phmresult.log[0][RESULT]


def test_no_sessions():
    """Test file with no sessions in --replmode."""
    line = "tests/md/directive2.md --replmode"
    phmresult = phmutest.main.command(line)
    want = phmutest.summary.Metrics(
        number_blocks_run=0,
        passed=0,
        failed=0,
        skipped=0,
        suite_errors=0,
        number_of_files=1,
        files_with_no_blocks=1,
        number_of_deselected_blocks=0,
    )
    assert want == phmresult.metrics
    assert phmresult.is_success is True
    assert "noblocks" in phmresult.log[0][RESULT]


def test_bad_session_output():
    """A Python interactive session example that has wrong output."""
    line = "tests/md/bad_session_output.md --replmode"
    phmresult = phmutest.main.command(line)
    want = phmutest.summary.Metrics(
        number_blocks_run=1,
        passed=0,
        failed=1,
        skipped=0,
        suite_errors=0,
        number_of_files=1,
        files_with_no_blocks=0,
        number_of_deselected_blocks=0,
    )
    assert want == phmresult.metrics
    assert phmresult.is_success is False


def test_bad_skipif_number():
    """Two different malformed phmutest-skipif directives are ignored."""
    line = "tests/md/bad_skipif_number.md"
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


def test_does_not_print():
    """Expected output expected but not produced."""
    line = "tests/md/does_not_print.md"
    phmresult = phmutest.main.command(line)
    want = phmutest.summary.Metrics(
        number_blocks_run=1,
        passed=0,
        failed=1,
        skipped=0,
        suite_errors=0,
        number_of_files=1,
        files_with_no_blocks=0,
        number_of_deselected_blocks=0,
    )
    assert want == phmresult.metrics
    assert phmresult.is_success is False


def test_excess_printing():
    """Excess expected output printed."""
    line = "tests/md/missing_some_output.md"
    phmresult = phmutest.main.command(line)
    want = phmutest.summary.Metrics(
        number_blocks_run=1,
        passed=0,
        failed=1,
        skipped=0,
        suite_errors=0,
        number_of_files=1,
        files_with_no_blocks=0,
        number_of_deselected_blocks=0,
    )
    assert want == phmresult.metrics
    assert phmresult.is_success is False


def test_extra_expected_output():
    """Expected output has an additional line."""
    line = "tests/md/extra_line_in_output.md"
    phmresult = phmutest.main.command(line)
    want = phmutest.summary.Metrics(
        number_blocks_run=1,
        passed=0,
        failed=1,
        skipped=0,
        suite_errors=0,
        number_of_files=1,
        files_with_no_blocks=0,
        number_of_deselected_blocks=0,
    )
    assert want == phmresult.metrics
    assert phmresult.is_success is False


def test_no_fcbs():
    """Test file with no FCBs."""
    line = "tests/md/no_fenced_code_blocks.md"
    phmresult = phmutest.main.command(line)
    want = phmutest.summary.Metrics(
        number_blocks_run=0,
        passed=0,
        failed=0,
        skipped=0,
        suite_errors=0,
        number_of_files=1,
        files_with_no_blocks=1,
        number_of_deselected_blocks=0,
    )
    assert want == phmresult.metrics
    assert phmresult.is_success is True
    assert "noblocks" in phmresult.log[0][RESULT]


def test_phmdoctest_mark_skip():
    """Test file with a single phmdoctest directive."""
    line = "tests/md/one_mark_skip.md"
    phmresult = phmutest.main.command(line)
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
    assert phmresult.is_success is True
    assert "phmdoctest-mark.skip" in phmresult.log[0][REASON]


def test_unexpected_output():
    """Test code block with incorrect expected output."""
    line = "tests/md/unexpected_output.md"
    phmresult = phmutest.main.command(line)
    want = phmutest.summary.Metrics(
        number_blocks_run=1,
        passed=0,
        failed=1,
        skipped=0,
        suite_errors=0,
        number_of_files=1,
        files_with_no_blocks=0,
        number_of_deselected_blocks=0,
    )
    assert want == phmresult.metrics
    assert phmresult.is_success is False
