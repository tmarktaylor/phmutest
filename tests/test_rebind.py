"""Check FCB rebinds a name passed as globs by --fixture and shares it across files.

On Linux run:

python -m pytest tests -k test_share_across_rebind --capture=tee-sys

to see the printing. Example output is shown below.

The name 'we' is added as a module global (sharing-mod adding= we, no_conflict)
by the generated test file setUpModule().

tests/test_rebind.py::test_share_across_rebind sharing-mod initialized
sharing-mod adding= we, no_conflict
sharing-mod names= no_conflict, we
sharing-mod-docs/share/file1.md adding= dataclass, BeverageActivity, cc, we
sharing-mod-docs/share/file1.md names= cc, BeverageActivity, we, no_conflict, dataclass
sharing-mod-docs/share/file2.md adding= bp
sharing-mod-docs/share/file2.md names= bp, cc, BeverageActivity, we, no_conflict, dataclass # noqa: E501

sharing-mod clearing= bp, cc, BeverageActivity, we, no_conflict, dataclass
sharing-mod is empty
cleanup-

The name 'we' is assigned in file1.md. The value overwrites the 'we' initialized
by the fixture. file2.md sees the value of 'we' assigned by file1.md.
The fixture cleanup function sees the original value of 'we'.


To see the effect of rebind in REPL mode see test_globs.py::test_extractor().
"""
import unittest

import phmutest.main
from phmutest.fixture import Fixture


def cleanup(globs):
    print("cleanup-")
    assert globs == {"we": 3, "no_conflict": 9999}


def globsfixture(**kwargs):
    """Pass the name 'we' as globs. That name is shared across files by file1.md."""
    myglobs = {"we": 3, "no_conflict": 9999}
    unittest.addModuleCleanup(cleanup, myglobs)
    return Fixture(globs=myglobs)


def test_share_across_rebind():
    """Share across files re-assign of fixture glob name done in file1.md."""
    command = (
        "docs/share/file1.md docs/share/file2.md docs/share/file3.md "
        "--share-across-files docs/share/file1.md docs/share/file2.md --log "
        "--fixture tests.test_rebind.globsfixture "
        "--sharing . --quiet"
    )
    # --quiet is passed through to unittest to prevent the progress dot printing.
    args = command.split()
    phmresult = phmutest.main.main(args)
    want = phmutest.summary.Metrics(
        number_blocks_run=8,
        passed=8,
        failed=0,
        skipped=0,
        suite_errors=0,
        number_of_files=3,
        files_with_no_blocks=0,
        number_of_deselected_blocks=0,
    )
    assert want == phmresult.metrics
