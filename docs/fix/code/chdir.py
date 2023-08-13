"""User fixture to change the current working directory while running tests."""
import os
import unittest
from pathlib import Path


def change_dir(**kwargs):
    """Change current working directory, restore later.

    This is an initialization function passed to the --fixture option.
    Logging is optional. The log is passed as the log keyword argument.
    To log, append a list of 3 strings to the "log". The middle string is used
    to calculate metrics in the phmutest return result.
    Avoid passing the keys used with the mapping counts in
    phmutest.summary.compute_metrics().

    Note there is no return statement. It is OK to skip the return here
    since this function does not return any globs or cleanup function.
    """
    log = kwargs["log"]
    unittest.addModuleCleanup(restore_working_directory, Path.cwd(), log)
    os.chdir("docs/fix/code")
    log.append(["change cwd", "", ""])


def restore_working_directory(workdir, log):
    os.chdir(workdir)
    log.append(["restore cwd", "", ""])
