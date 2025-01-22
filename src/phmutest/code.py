"""Run the generated unittest source file with unittest.main."""

import copy
import importlib
import itertools
import sys
import unittest
from pathlib import Path
from tempfile import TemporaryDirectory

import phmutest.config
import phmutest.fcb
import phmutest.summary

gen_file_counter = itertools.count(1)


def run_code(
    settings: phmutest.config.Settings,
    testfile: str,
) -> phmutest.summary.PhmResult:
    """Run the generated testfile with unittest."""
    args = settings.args  # rename
    # When phmutest is imported and called from a user Python script
    # consider the following:
    # The gen_file_counter makes each module name unique.
    # Each time generate_and_run() is called a new module is created
    # and imported. That consumes Python interpreter resources that are not
    # released until the interpreter exits. The resources include:
    #     sys.path
    #     imported modules
    genmodulename = f"_phm{next(gen_file_counter)}"
    genfilename = genmodulename + ".py"

    with TemporaryDirectory() as tmpdir:
        dest = Path(tmpdir) / genfilename
        # Tell the Printer class the generated testfile name.
        testfile = testfile.replace(
            "_phmPrinter.testfile_name = None", f'_phmPrinter.testfile_name = r"{dest}"'
        )
        _ = dest.write_text(testfile, encoding="utf-8")
        # unittest is the default test runner. Run unittest now.
        sys.path.append(tmpdir)
        unittest_args = ["unittest.main"]
        if settings.extra_args:
            unittest_args.extend(settings.extra_args)
        # Run the testfile
        testprog: unittest.TestProgram = unittest.main(
            module=genmodulename, argv=unittest_args, exit=False
        )
        # Note: unittest should have already imported genmodulename.
        phmgen = importlib.import_module(genmodulename)
        log = copy.copy(phmgen._phm_log)
        metrics = phmutest.summary.compute_metrics(
            num_files=len(args.files),
            suite_errors=len(testprog.result.errors),
            num_deselected=-1,  # fill in later in main:generate_and_run
            log=log,
        )
        phmresult = phmutest.summary.PhmResult(
            test_program=testprog,
            is_success=testprog.result.wasSuccessful(),
            metrics=metrics,
            log=log,
        )
    return phmresult
