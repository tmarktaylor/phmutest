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
