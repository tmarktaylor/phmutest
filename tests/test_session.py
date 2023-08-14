"""Test cases for session.py."""
import phmutest.main
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
    """Use case where --replmode fixture returns Fixture with replmode=None."""
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
    expected = """location|label            result  skip reason
        ------------------------  ------  -------------------
        tests/md/replerror.md:3.  pass
        tests/md/replerror.md:7.  pass
        tests/md/replerror.md:11  pass
        tests/md/replerror.md:18  pass
        tests/md/replerror.md:24  skip    phmutest-skip
        tests/md/replerror.md:32  error
        tests/md/replerror.md:39  error
        tests/md/replerror.md:47  skip    requires >=py3.9999
        tests/md/replerror.md:55  pass
        ------------------------  ------  -------------------
        location|label          result
        ----------------------  ------
        tests/md/example1.md:5  pass
        ----------------------  ------
        """
    output = capsys.readouterr().out.rstrip()
    endswith_checker(expected, output)
