"""Check handling of --skip command line option."""

import phmutest.main


def test_skip_text1():
    """Command line --skip removes 1 test case containing TEXT squares."""
    command = "tests/md/example2.md --log --skip squares"
    args = command.split()
    phmresult = phmutest.main.main(args)
    want = phmutest.summary.Metrics(
        number_blocks_run=4,
        passed=4,
        failed=0,
        skipped=1,
        suite_errors=0,
        number_of_files=1,
        files_with_no_blocks=0,
        number_of_deselected_blocks=0,
    )
    assert want == phmresult.metrics
    assert phmresult.is_success is True
    assert "--skip squares" in phmresult.log[0][2]


def test_skip_text2():
    """Command line --skip removes 1 test case containing TEXT datetime."""
    command = "tests/md/example2.md --log --skip datetime"
    args = command.split()
    phmresult = phmutest.main.main(args)
    want = phmutest.summary.Metrics(
        number_blocks_run=4,
        passed=4,
        failed=0,
        skipped=1,
        suite_errors=0,
        number_of_files=1,
        files_with_no_blocks=0,
        number_of_deselected_blocks=0,
    )
    assert want == phmresult.metrics
    assert phmresult.is_success is True
    assert "--skip datetime" in phmresult.log[4][2]


def test_two_skip_arg():
    """Command line two --skip removes 2 test cases."""
    command = "tests/md/example2.md --log --skip squares --skip datetime"
    args = command.split()
    phmresult = phmutest.main.main(args)
    want = phmutest.summary.Metrics(
        number_blocks_run=3,
        passed=3,
        failed=0,
        skipped=2,
        suite_errors=0,
        number_of_files=1,
        files_with_no_blocks=0,
        number_of_deselected_blocks=0,
    )
    assert want == phmresult.metrics
    assert phmresult.is_success is True
    assert "--skip squares" in phmresult.log[0][2]
    assert "--skip datetime" in phmresult.log[4][2]


def test_two_skip_option():
    """Command line --skip with 2 values removes 2 test cases."""
    command = "tests/md/example2.md --log --skip squares datetime"
    args = command.split()
    phmresult = phmutest.main.main(args)
    want = phmutest.summary.Metrics(
        number_blocks_run=3,
        passed=3,
        failed=0,
        skipped=2,
        suite_errors=0,
        number_of_files=1,
        files_with_no_blocks=0,
        number_of_deselected_blocks=0,
    )
    assert want == phmresult.metrics
    assert phmresult.is_success is True
    assert "--skip squares" in phmresult.log[0][2]
    assert "--skip datetime" in phmresult.log[4][2]
