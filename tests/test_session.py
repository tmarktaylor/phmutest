"""Test cases for session.py."""

import sys
import traceback
from unittest import mock

import pytest

import phmutest.main
import phmutest.summary
from phmutest.fixture import Fixture


def test_replmode_skip():
    """Show --skip, skip directive and skipifpy< directive in doctest Example."""
    command = "tests/md/replerror.md --skip MYSKIPPATTERN --replmode --log"
    args = command.split()
    phmresult = phmutest.main.main(args)
    want = phmutest.summary.Metrics(
        number_blocks_run=6,
        passed=5,
        failed=0,
        skipped=3,
        suite_errors=1,
        number_of_files=1,
        files_with_no_blocks=0,
        number_of_deselected_blocks=0,
    )
    assert want == phmresult.metrics
    assert phmresult.test_program is None
    assert phmresult.is_success is False


def nonefixture(**kwargs):
    """phmutest fixture function returns None."""
    print("nonefixture-")
    return None


def test_fixture_returns_none(capsys):
    """Use case where --replmode fixture returns None to cover code that checks that."""
    command = (
        "tests/md/replerror.md "
        "--fixture tests.test_session.nonefixture --replmode --log"
    )
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
    assert phmresult.test_program is None
    assert phmresult.is_success is False
    assert capsys.readouterr().out.startswith("nonefixture-")


def nonecleanupfixture(**kwargs):
    """phmutest fixture function returns None."""
    print("nonecleanupfixture-")
    return Fixture(globs=None, repl_cleanup=None)


def test_none_cleanup(capsys):
    """Use case where --replmode fixture returns Fixture with repl_cleanup=None."""
    command = (
        "tests/md/replerror.md "
        "--fixture tests.test_session.nonecleanupfixture --replmode --log"
    )
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
    assert capsys.readouterr().out.startswith("nonecleanupfixture-")


def test_progress(capsys, endswith_checker):
    """--progress option that prints the per file log after each file."""
    command = "tests/md/replerror.md tests/md/example1.md --replmode --progress"
    args = command.split()
    phmresult = phmutest.main.main(args)
    want = phmutest.summary.Metrics(
        number_blocks_run=8,
        passed=6,
        failed=0,
        skipped=2,
        suite_errors=2,
        number_of_files=2,
        files_with_no_blocks=0,
        number_of_deselected_blocks=0,
    )
    assert want == phmresult.metrics
    assert phmresult.test_program is None
    assert phmresult.is_success is False

    # The FCB tests/md/replerror.md:33 raises a TypeError.
    # The exception description can change between Python minor versions
    # and Python implementations.
    # Cause the same TypeError here and use its description as the expected output.
    description = ""
    try:
        "" + int(3)
    except TypeError:
        exc_info = sys.exc_info()
        lines = traceback.format_exception_only(exc_info[0], exc_info[1])
        description = lines[-1]
        description = description.replace("\n", "")
    column_3_width = max(
        len(description), len("AssertionError: --skip identified block")
    )
    dashes = "-" * column_3_width

    expected = f"""location|label            result  reason
        ------------------------  ------  {dashes}
        tests/md/replerror.md:3.  pass
        tests/md/replerror.md:7.  pass
        tests/md/replerror.md:11  pass
        tests/md/replerror.md:18  pass
        tests/md/replerror.md:26  skip    phmutest-skip
        tests/md/replerror.md:33  error   {description}
        tests/md/replerror.md:40  error   AssertionError: --skip identified block
        tests/md/replerror.md:49  skip    requires >=py3.9999
        tests/md/replerror.md:57  pass
        ------------------------  ------  {dashes}
        location|label          result
        ----------------------  ------
        tests/md/example1.md:5  pass
        ----------------------  ------
        """  # noqa: E501
    output = capsys.readouterr().out.rstrip()
    endswith_checker(expected, output)


def verbose_cleanup():
    """fixture cleanup function that prints."""
    print("Most definitely cleaning up here!")


def printing_cleanup_fixture(**kwargs):
    """phmutest fixture function with a cleanup function that prints."""
    return Fixture(globs=None, repl_cleanup=verbose_cleanup)


def cause_exception(args, globs, fileblocks, extractor):
    """Replacement function that raises an exception."""
    raise ValueError("Bad phmutest REPL logic.")


def test_repl_still_cleans_up(capsys):
    """Show repl fixture cleanup is called for an internal error during session.py."""
    # Get coverage for code that handles an unexpected exception in phmutest code that
    # runs in --replmode. The code assures that a fixture cleanup function
    # gets called before propagating the exception.
    # Use patching to inject the exception.
    with mock.patch("phmutest.session.update_globs_show_sharing", cause_exception):
        with pytest.raises(ValueError) as exc_info:
            command = (
                "tests/md/example1.md tests/md/example2.md "
                "--fixture tests.test_session.printing_cleanup_fixture --replmode --log"
            )
            args = command.split()
            _ = phmutest.main.main(args)
        assert "Most definitely cleaning up here!" in capsys.readouterr().out
        assert "Bad phmutest REPL logic." in str(exc_info.value)
