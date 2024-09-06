"""Test subprocess call."""

import subprocess
import sys


def test_subprocess():
    """Run phmutest in a subprocess."""
    commandline = [
        sys.executable,
        "-m",
        "phmutest",
        "docs/fix/code/globdemo.md",
        "--progress",
        "--quiet",
        "--log",
        "--summary",
        "--fixture",
        "docs.fix.code.globdemo.init_globals",
    ]
    completed = subprocess.run(commandline)
    assert completed.returncode == 0


def test_callfrompython():
    """Run phmutest in a subprocess on the call from python example."""
    # Although it works on the linux dev machine, decided not to run
    # the call from Python example as a phmutest call from Python.
    # So run it in a subprocess as a command line call.
    commandline = [
        sys.executable,
        "-m",
        "phmutest",
        "docs/callfrompython.md",
        "--progress",
        "--quiet",
        "--log",
        "--summary",
    ]
    completed = subprocess.run(commandline)
    assert completed.returncode == 0


def test_fixture_patching():
    """Run phmutest in a subprocess, call a fixture that does mock.patch().

    This shows a --fixture function using contextlib.ExitStack to install
    a patch using unittest.mock.patch() with a shell invocation of
    phmutest. It runs the same example as
    test_patching::test_doctest_optionflags_patch.

    It should be possible to do the same patch when not in --replmode
    by calling unittest.addModuleCleanup(stack.pop_all().close).
    """
    commandline = [
        sys.executable,
        "-m",
        "phmutest",
        "tests/md/optionflags.md",
        "--log",
        "--replmode",
        "--fixture",
        "tests.test_patching.setflags",
    ]
    completed = subprocess.run(commandline)
    assert completed.returncode == 0
