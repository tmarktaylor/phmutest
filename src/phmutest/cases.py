"""Generate test cases as a unittest test file."""
import argparse
from pathlib import Path
from typing import Tuple

import phmutest.select
import phmutest.subtest

# Uses Python template string substitution to generate custom code from
# templates strings and key mappings.  The forms are filled in by Python
# standard library String.Template which supports $ based string
# substitution.
#
# If the template value can have expected output, its key must start on
# column 1 in the template.  This is because the expected output string value
# (defined by _phm_expected_str in the generated code) must not be
# indented. See $setupblocks, $teardownblocks, $subtests,
# $setupmodule, $teardownmodule, $testclasses below.


def deindent(text: str) -> str:
    """Shift lines indented by 4 or more spaces to the left 4 spaces."""
    lines = []
    for line in text.splitlines():
        if line.startswith("    "):
            lines.append(line[4:])
        else:
            lines.append(line)
    return "\n".join(lines)


def is_verbose_sharing(args: argparse.Namespace, path: Path) -> bool:
    """Check if path is one of --sharing FILE or if --sharing "."."""
    return path in args.sharing or args.sharing == [Path(".")]


# Note- Module level $setupblocks and $teardownblocks implement --setup-across-files.
setup_module_form = """\
def setUpModule():

    global _phm_globals
    _phm_log.append(["setUpModule", "", ""])
    $showprogressenter
    _phm_globals = _phmGlobals(__name__, shareid=$shareid)
    $usersetupupdate
$setupblocks
    $showprogressexit
"""


def render_setup_module(
    args: argparse.Namespace, block_store: phmutest.select.BlockStore
) -> str:
    """Generate code for unittest setUpModule() fixture."""
    setup_blocks = ""
    for path in args.setup_across_files:
        fileblocks = block_store.get_blocks(path)
        setup_blocks += phmutest.subtest.format_setup_blocks(
            args,
            fileblocks,
        )
    deindented_setup_blocks = deindent(setup_blocks)
    if deindented_setup_blocks:  # Share the names in the setup blocks.
        deindented_setup_blocks += "\n    _phm_globals.update(additions=locals())"

    files_with_sharing = list(args.setup_across_files)
    files_with_sharing.extend(args.share_across_files)
    for path in files_with_sharing:
        if is_verbose_sharing(args, path):
            shareid = '"mod"'
            break
    else:
        shareid = '""'

    replacements = {}
    replacements["shareid"] = shareid
    replacements["setupblocks"] = deindented_setup_blocks
    if args.progress:
        replacements["showprogressenter"] = 'print("setUpModule()...", file=sys.stderr)'
        replacements[
            "showprogressexit"
        ] = 'print("leaving setUpModule.", file=sys.stderr)'

    if args.fixture:
        replacements["usersetupupdate"] = phmutest.subtest.justify(
            setup_module_form,
            "$usersetupupdate",
            fixture_globs_update_code,
        )
    return phmutest.subtest.fill_in(
        setup_module_form,
        replacements,
    )


fixture_globs_update_code = """\
_phm_fixture = _phm_user_setup_function(log=_phm_log)
if _phm_fixture is not None:
    if _phm_fixture.globs is not None:
        _phm_globals.update(additions=_phm_fixture.globs)"""


teardown_module_form = """\
def tearDownModule():

    _phm_log.append(["tearDownModule", "", ""])
    $showprogressenter
$teardownblocks
    _phm_globals.clear()
    $showprogressexit
"""


def render_teardown_module(
    args: argparse.Namespace, block_store: phmutest.select.BlockStore
) -> str:
    """Generate code for unittest tearDownModule() fixture."""
    teardown_blocks = ""
    for path in args.setup_across_files:
        fileblocks = block_store.get_blocks(path)
        teardown_blocks += phmutest.subtest.format_teardown_blocks(
            args,
            fileblocks,
        )
    deindented_teardown_blocks = deindent(teardown_blocks)
    replacements = {}
    replacements["teardownblocks"] = deindented_teardown_blocks

    if args.progress:
        replacements[
            "showprogressenter"
        ] = 'print("tearDownModule()...", file=sys.stderr)'
        replacements[
            "showprogressexit"
        ] = 'print("leaving tearDownModule.", file=sys.stderr)'

    return phmutest.subtest.fill_in(
        teardown_module_form,
        replacements,
    )


setup_class_form = """\

    @classmethod
    def setUpClass(cls):

        cls.global_names = _phmGlobals(__name__, shareid=$shareid)
$setupblocks
        cls.global_names.update(additions=locals(), built_from=$built_from)
"""


def render_setup_class(
    args: argparse.Namespace, fileblocks: phmutest.select.FileBlocks, shareid: str
) -> str:
    """Generate code for unittest setUpClass() fixture."""
    setup_blocks = phmutest.subtest.format_setup_blocks(args, fileblocks)
    if setup_blocks:
        replacements = dict(
            shareid=f'"{shareid}"',
            setupblocks=setup_blocks,
            built_from=f'"{fileblocks.built_from}"',
        )
        return phmutest.subtest.fill_in(
            setup_class_form,
            replacements,
        )
    else:
        return ""


teardown_class_form = """\

    @classmethod
    def tearDownClass(cls):

$teardownblocks
        cls.global_names.clear()
"""


noblocks_teardown_class = """\

    @classmethod
    def tearDownClass(cls):
        cls.global_names.clear()
"""


def render_teardown_class(
    args: argparse.Namespace,
    fileblocks: phmutest.select.FileBlocks,
    has_setup: bool,
) -> str:
    """Generate code for unittest tearDownClass() fixture."""
    teardown_blocks = phmutest.subtest.format_teardown_blocks(args, fileblocks)
    if teardown_blocks:
        replacements = {"teardownblocks": teardown_blocks}
        return phmutest.subtest.fill_in(
            teardown_class_form,
            replacements,
        )
    # If there is a setUpClass the tearDownClass is required to
    # call cls.global_names.clear().
    elif has_setup:
        return noblocks_teardown_class
    else:
        return ""


# Note- The keys are left justified in the template if they
#       have $output for expected output blocks.
#       Expected output must start in column 1.
class_form = '''\
class Test$filenum(unittest.TestCase):
    """Test cases generated from $mdfile."""
$setupclass
$teardownclass

    def tests(self):

$subtests
        $sharenames

'''

no_blocks_form = """\
        # no python blocks to test
        _phm_log.append(["$builtfrom", "noblocks", ""])
"""

no_log_form = """\
        # no python Role.CODE blocks.
        pass
"""


def markdown_file(
    args: argparse.Namespace,
    block_store: phmutest.select.BlockStore,
    path: Path,
    sequence_number: int,
) -> str:
    """Generate test class from examples in Markdown file given by path."""
    fileblocks = block_store.get_blocks(path)
    replacements = dict(
        mdfile=fileblocks.built_from,
        filenum=str(sequence_number).zfill(3),
        setupclass="",  # for test below
    )
    if is_verbose_sharing(args, path):
        shareid = "class"
    else:
        shareid = ""

    if path not in args.setup_across_files:
        replacements["setupclass"] = render_setup_class(
            args,
            fileblocks,
            shareid=shareid,
        )
        has_setup = bool(replacements["setupclass"])
        replacements["teardownclass"] = render_teardown_class(
            args,
            fileblocks,
            has_setup,
        )

    sub_tests = phmutest.subtest.format_code_blocks(
        args,
        fileblocks,
    )

    if sub_tests:
        replacements["subtests"] = sub_tests
    else:
        # We get here if there were no subtests. This means that all the code blocks
        # have setup or teardown directives OR there were no code blocks at all.
        if not fileblocks.selected:
            replacements["subtests"] = no_blocks_form.replace(
                "$builtfrom", fileblocks.built_from
            )
        else:
            # Assuming all the code blocks have setup or teardown directives.
            replacements["subtests"] = no_log_form

    if path in args.share_across_files:
        # If there is a setUpClass it adds names to the Globals object cls.global_names.
        # Tell the module level Globals object _phm_globals about those
        # names when doing the update at the bottom of the class's def tests(self).
        # When the tearDownClass is run the cls.global_names names are removed
        # from the module.
        if replacements["setupclass"].strip():
            existing_names = "existing_names=self.global_names.get_names()"
        else:
            existing_names = "existing_names=None"
        from_arg = f'built_from="{fileblocks.built_from}"'
        statement = (
            f"_phm_globals.update(additions=locals(), {from_arg}, {existing_names})"
        )
        replacements["sharenames"] = statement
    return phmutest.subtest.fill_in(
        class_form,
        replacements,
    )


testfile_form = '''\
"""Python unittest test file generated by Python Package phmutest."""
import contextlib
import io
import sys
import unittest

from phmutest.globs import Globals as _phmGlobals
from phmutest.printer import Printer as _phmPrinter
from phmutest.skip import sys_tool as _phm_sys
$usersetupfunction

_phm_globals = None
_phm_testcase = unittest.TestCase()
_phm_log = []
$setupmodule
$teardownmodule
$testclasses
'''


def get_fixture_parts(fixture_arg: Path) -> Tuple[str, str]:
    """Return X, Y for the fixture function where X and Y are 'from X import Y'."""
    function = fixture_arg.suffix  # pathlib Rocks!
    assert function.startswith("."), "Expecting .FUNCTION."
    function = function[1:]
    return fixture_arg.stem, function


def testfile(args: argparse.Namespace, block_store: phmutest.select.BlockStore) -> str:
    """Generate the unittest module source as directed by command line args args."""
    test_classes = ""
    replacements = {}
    if args.fixture:
        modulepackage, function_name = get_fixture_parts(args.fixture)
        replacements[
            "usersetupfunction"
        ] = f"from {modulepackage} import {function_name} as _phm_user_setup_function"

    if args.setup_across_files or args.share_across_files or args.fixture:
        setupcode = render_setup_module(args, block_store)
        replacements["setupmodule"] = "\n\n" + setupcode
        teardown_code = render_teardown_module(args, block_store)
        replacements["teardownmodule"] = "\n\n" + teardown_code

    sequence_number = 1
    for sequence_number, path in enumerate(args.files, start=1):
        test_classes += "\n\n" + markdown_file(args, block_store, path, sequence_number)
    if not test_classes.endswith("\n"):
        test_classes += "\n"
    replacements["testclasses"] = test_classes

    return phmutest.subtest.fill_in(
        testfile_form,
        replacements,
    )
