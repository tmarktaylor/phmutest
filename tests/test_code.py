"""Check --runpytest return code."""

import phmutest.main


def test_runpytest_only():
    """Run pytest, no unittest: phmresult.pytest_returncode indicates pytest failed."""
    line = "README.md --runpytest only"
    phmresult = phmutest.main.command(line)
    assert phmresult.is_success is None
    assert phmresult.pytest_returncode == 1


def test_runpytest_on_error():
    """Run pytest after unittest fails."""
    line = "README.md --runpytest on-error"
    phmresult = phmutest.main.command(line)
    assert phmresult.is_success is False
    assert phmresult.pytest_returncode == 1


def test_runpytest_passes():
    """Check for good pytest_returncode."""
    line = "tests/md/project.md --runpytest only"
    phmresult = phmutest.main.command(line)
    assert phmresult.is_success is None
    assert phmresult.pytest_returncode == 0


def test_pytest_returncode_is_none():
    """When no --runpytest the return code is None."""
    line = "tests/md/project.md"
    phmresult = phmutest.main.command(line)
    assert phmresult.is_success is True
    assert phmresult.pytest_returncode is None
    line = "README.md"
    phmresult = phmutest.main.command(line)
    assert phmresult.pytest_returncode is None


def test_cleanups():
    """Show unittest.doModuleCleanups() gets called."""
    line = (
        "tests/md/cleanups.md --fixture docs.fix.code.chdir.change_dir"
        " --log --runpytest only"
    )
    phmresult = phmutest.main.command(line)
    assert phmresult.pytest_returncode == 1, phmresult.pytest_returncode
