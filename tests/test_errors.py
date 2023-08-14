"""Check handling of user code raising an exception.  Python code, REPLs, --fixture."""
import contextlib
import io

import pytest

import phmutest.main


def test_code_raises():
    """Python code block raises an exception."""
    command = "tests/fail/raiser.md --log"
    args = command.split()
    phmresult = phmutest.main.main(args)
    want = phmutest.summary.Metrics(
        number_blocks_run=6,
        passed=4,
        failed=1,
        skipped=0,
        suite_errors=1,
        number_of_files=1,
        files_with_no_blocks=0,
        number_of_deselected_blocks=0,
    )
    assert want == phmresult.metrics
    assert phmresult.is_success is False
    assert "error" in phmresult.log[4][1]
    assert "failed" in phmresult.log[5][1]


def test_unittest_fail_fast():
    """Pass through callers -f option to unittest. (fail fast)."""
    command = "tests/fail/raiser.md --log -f"
    phmresult = phmutest.main.main(command.split())
    want = phmutest.summary.Metrics(
        number_blocks_run=5,
        passed=4,
        failed=0,
        skipped=0,
        suite_errors=1,
        number_of_files=1,
        files_with_no_blocks=0,
        number_of_deselected_blocks=0,
    )
    assert want == phmresult.metrics
    assert phmresult.is_success is False


def test_replmode_failfast():
    """Test skipping examples after first fail. Need doctest optionflags to pass."""
    command = "tests/md/optionflags.md tests/md/project.md --log --replmode -f"
    args = command.split()
    phmresult = phmutest.main.main(args)
    want = phmutest.summary.Metrics(
        number_blocks_run=2,
        passed=1,
        failed=1,  # with -f should never be > 1
        skipped=0,
        suite_errors=0,
        number_of_files=2,  # Includes files that didn't get to run due to -f
        files_with_no_blocks=0,
        number_of_deselected_blocks=0,
    )
    assert want == phmresult.metrics
    assert phmresult.is_success is False


def test_replmode_errors():
    """Show exception handling in a doctest Example."""
    command = "tests/md/replerror.md --replmode --log"
    args = command.split()
    phmresult = phmutest.main.main(args)
    want = phmutest.summary.Metrics(
        number_blocks_run=7,
        passed=5,
        failed=0,
        skipped=2,
        suite_errors=2,
        number_of_files=1,
        files_with_no_blocks=0,
        number_of_deselected_blocks=0,
    )
    assert want == phmresult.metrics
    assert phmresult.is_success is False


def badfixture(**kwargs):
    """phmutest fixture raises an exception."""
    raise (ValueError("badfixture- having a bad day"))
    return None


def test_repl_fixture_raises(capsys):
    """In --replmode a fixture raises an exception.  It just kills phmutest."""
    command = "tests/md/replerror.md --fixture tests.test_errors.badfixture --replmode"
    args = command.split()
    with pytest.raises(ValueError) as exc_info:
        _ = phmutest.main.main(args)
    assert "badfixture- having a bad day" in str(exc_info.value)


def test_summary_option(capsys, checker):
    """Check --summary output."""
    command = "--config tests/toml/project.toml --summary"
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

    output = capsys.readouterr().out.strip()
    expected = """summary:
        metric
        --------------------  -
        blocks run            6
        blocks passed         4
        blocks failed         2
        blocks skipped        1
        suite errors          0
        Markdown files        3
        files with no blocks  0
        deselected blocks     0
        --------------------  -

        skipped blocks             reason
        -------------------------  -------------
        tests/md/directive1.md:14  phmutest-skip
        -------------------------  -------------
        """
    checker(expected, output)


def test_setup_raises(capsys, endswith_checker):
    """Check handling of an exception in a <~--phmutest-setup--> block.

    Cover 'setup and teardown errors' statements.
    The setup block generates into the unittest setUpClass() function.
    """
    command = "tests/md/badsetup.md --summary"
    args = command.split()
    with contextlib.redirect_stderr(io.StringIO()) as err:
        phmresult = phmutest.main.main(args)
    want = phmutest.summary.Metrics(
        number_blocks_run=1,
        passed=0,
        failed=0,
        skipped=0,
        suite_errors=1,
        number_of_files=1,
        files_with_no_blocks=0,
        number_of_deselected_blocks=0,
    )
    assert want == phmresult.metrics
    assert phmresult.is_success is False

    output = capsys.readouterr().out.strip()
    expected = """summary:

        setup and teardown errors
        -------------------------
        tests/md/badsetup.md:6 setup

        metric
        --------------------  -
        blocks run            1
        blocks passed         0
        blocks failed         0
        blocks skipped        0
        suite errors          1
        Markdown files        1
        files with no blocks  0
        deselected blocks     0
        --------------------  -
        """
    endswith_checker(expected, output)
    error = err.getvalue()
    err.close()
    assert "ERROR: setUpClass" in error
    assert "TypeError: badsetup.md in setup block" in error


def test_setup_across_raises(capsys, endswith_checker):
    """Check handling of an exception in a <~--phmutest-setup--> block.

    The setup block is rendered in setUpModule().
    The error in setUpModule() cancels the rest of the unittest.
    Try with 2 imput files.
    """
    command = (
        "tests/md/badsetup.md tests/md/badteardown.md --summary "
        "--setup-across-files tests/md/badsetup.md"
    )
    args = command.split()
    with contextlib.redirect_stderr(io.StringIO()) as err:
        phmresult = phmutest.main.main(args)
    phmresult = phmutest.main.main(args)
    want = phmutest.summary.Metrics(
        number_blocks_run=1,
        passed=0,
        failed=0,
        skipped=0,
        suite_errors=1,
        number_of_files=2,
        files_with_no_blocks=0,
        number_of_deselected_blocks=0,
    )
    assert want == phmresult.metrics
    assert phmresult.is_success is False

    output = capsys.readouterr().out.strip()
    expected = """summary:

        setup and teardown errors
        -------------------------
        tests/md/badsetup.md:6 setup

        metric
        --------------------  -
        blocks run            1
        blocks passed         0
        blocks failed         0
        blocks skipped        0
        suite errors          1
        Markdown files        2
        files with no blocks  0
        deselected blocks     0
        --------------------  -
        """
    endswith_checker(expected, output)
    error = err.getvalue()
    err.close()
    assert "ERROR: setUpModule" in error
    assert "TypeError: badsetup.md in setup block" in error


def test_teardown_raises(capsys, endswith_checker):
    """Check handling of an exception in a <~--phmutest-teardown--> block.

    Cover 'setup and teardown errors' statements.
    """
    command = "tests/md/badteardown.md --summary"
    args = command.split()
    with contextlib.redirect_stderr(io.StringIO()) as err:
        phmresult = phmutest.main.main(args)
    want = phmutest.summary.Metrics(
        number_blocks_run=5,
        passed=4,
        failed=0,
        skipped=0,
        suite_errors=1,
        number_of_files=1,
        files_with_no_blocks=0,
        number_of_deselected_blocks=0,
    )
    assert want == phmresult.metrics
    assert phmresult.is_success is False

    output = capsys.readouterr().out.strip()
    expected = """summary:

        setup and teardown errors
        -------------------------
        tests/md/badteardown.md:55 teardown

        metric
        --------------------  -
        blocks run            5
        blocks passed         4
        blocks failed         0
        blocks skipped        0
        suite errors          1
        Markdown files        1
        files with no blocks  0
        deselected blocks     0
        --------------------  -
        """
    endswith_checker(expected, output)
    error = err.getvalue()
    err.close()
    assert "ERROR: tearDownClass" in error
    assert "TypeError: badteardown.md in teardown block" in error


def test_teardown_across_raises(capsys, endswith_checker):
    """Check handling of an exception in a <~--phmutest-teardown--> block.

    Cover 'setup and teardown errors' statements.
    """
    command = (
        "tests/md/badteardown.md --summary "
        "--setup-across-files tests/md/badteardown.md"
    )
    args = command.split()
    with contextlib.redirect_stderr(io.StringIO()) as err:
        phmresult = phmutest.main.main(args)
    want = phmutest.summary.Metrics(
        number_blocks_run=5,
        passed=4,
        failed=0,
        skipped=0,
        suite_errors=1,
        number_of_files=1,
        files_with_no_blocks=0,
        number_of_deselected_blocks=0,
    )
    assert want == phmresult.metrics
    assert phmresult.is_success is False

    output = capsys.readouterr().out.strip()
    expected = """summary:

        setup and teardown errors
        -------------------------
        tests/md/badteardown.md:55 teardown

        metric
        --------------------  -
        blocks run            5
        blocks passed         4
        blocks failed         0
        blocks skipped        0
        suite errors          1
        Markdown files        1
        files with no blocks  0
        deselected blocks     0
        --------------------  -
        """
    endswith_checker(expected, output)
    error = err.getvalue()
    err.close()
    assert "ERROR: tearDownModule" in error
    assert "TypeError: badteardown.md in teardown block" in error
