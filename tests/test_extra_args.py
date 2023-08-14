"""Check pass through of extra args to unittest."""
import pytest

import phmutest.main


def test_noextras():
    """No extra args."""
    command = "--config tests/toml/project.toml --log"
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


def test_verbose():
    """unittest --verbose."""
    command = "--config tests/toml/project.toml --verbose --log"
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


def test_quiet():
    """unittest --quiet."""
    command = "--config tests/toml/project.toml --quiet --log"
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


def test_locals():
    """unittest --locals."""
    command = "--config tests/toml/project.toml --locals --log"
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


def test_catch():
    """unittest --catch."""
    command = "--config tests/toml/project.toml --catch --log"
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


def test_buffer():
    """unittest --buffer."""
    command = "--config tests/toml/project.toml --buffer --log"
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


@pytest.mark.skip("Causes unrelated tests to fail.")
def test_namepatterns():
    """-k TESTNAMEPATTERNS. Use -k= otherwise it looks like a .md file."""
    command = "--config tests/toml/project.toml -k=NOMATCH --log"
    args = command.split()
    phmresult = phmutest.main.main(args)
    want = phmutest.summary.Metrics(
        number_blocks_run=0,
        passed=0,
        failed=0,
        skipped=0,
        suite_errors=0,
        number_of_files=3,
        files_with_no_blocks=0,
        number_of_deselected_blocks=0,
    )
    assert want == phmresult.metrics
    assert phmresult.is_success is True


def test_replmode():
    """No extra args."""
    command = "--config tests/toml/projectrepl.toml --replmode --log"
    args = command.split()
    phmresult = phmutest.main.main(args)
    want = phmutest.summary.Metrics(
        number_blocks_run=5,
        passed=4,
        failed=1,
        skipped=1,
        suite_errors=0,
        number_of_files=3,
        files_with_no_blocks=0,
        number_of_deselected_blocks=0,
    )
    assert want == phmresult.metrics
    assert phmresult.is_success is False


def test_replmode_failfast():
    """Test --replmode files with -f (fail fast)."""
    # phmutest handles -f when creating its ExampleOutcomeRunner.
    # The .md file on the command line extends the files selected by the .toml.
    command = (
        "tests/md/optionflags.md --config tests/toml/projectrepl.toml "
        "--replmode --log -f"
    )
    args = command.split()
    phmresult = phmutest.main.main(args)
    want = phmutest.summary.Metrics(
        number_blocks_run=4,
        passed=3,
        failed=1,
        skipped=0,  # -f aborted suite before running skipped FCB.
        suite_errors=0,
        number_of_files=4,  # Includes files that didn't get to run due to -f
        files_with_no_blocks=0,
        number_of_deselected_blocks=0,
    )
    assert want == phmresult.metrics
    assert phmresult.is_success is False
