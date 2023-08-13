"""Generate and run docstests for Python interactive session FCBs."""
import argparse
import contextlib
import doctest
import importlib
import itertools
import sys
from dataclasses import dataclass
from pathlib import Path
from typing import Any, Dict, List, Optional, Tuple, cast

import phmutest.cases
import phmutest.globs
import phmutest.select
import phmutest.subtest
import phmutest.summary
from phmutest.direct import Marker
from phmutest.fenced import FencedBlock


class ExampleOutcomeRunner(doctest.DocTestRunner):
    """Doctest Runner to record Example line number, pass/failed/error status."""

    def __init__(self, **kwargs):  # type: ignore
        super().__init__(**kwargs)
        self.outcomes = {}
        self.number_of_failures = 0
        self.number_of_errors = 0

    def report_success(self, out, test, example, got):  # type: ignore
        self.outcomes[example.lineno + 1] = "pass"
        super().report_success(out, test, example, got)

    def report_failure(self, out, test, example, got):  # type: ignore
        self.outcomes[example.lineno + 1] = "failed"
        self.number_of_failures += 1
        super().report_failure(out, test, example, got)

    def report_unexpected_exception(self, out, test, example, exc_info):  # type: ignore
        self.outcomes[example.lineno + 1] = "error"
        self.number_of_errors += 1
        super().report_unexpected_exception(out, test, example, exc_info)


def skip_block(block: FencedBlock, built_from: str) -> Optional[Tuple[int, List[str]]]:
    """If block should be skipped return details for log enty, otherwise None."""
    details = None
    if block.skip_patterns:
        doc_location = phmutest.subtest.make_location_string(block, built_from)
        reason = "--skip " + ", ".join(block.skip_patterns)
        details = (block.line, [doc_location, "skip", reason])
    else:
        if directive := block.get_directive(Marker.SKIP, Marker.SKIPIF_PYVERSION):
            doc_location = phmutest.subtest.make_location_string(block, built_from)
            if directive.type == Marker.SKIP:
                reason = directive.literal[4:-3]  # lose the directive <!-- and -->.
                details = (block.line, [doc_location, "skip", reason])
            else:
                assert directive.type == Marker.SKIPIF_PYVERSION, "sanity check"
                minor_version = int(directive.value)
                if sys.version_info < (3, minor_version):
                    reason = f"requires >=py3.{minor_version}"
                    details = (block.line, [doc_location, "skip", reason])
    return details


def get_result(block_outcomes: List[str]) -> str:
    """Determine pass/failed/error result from the block Example outcomes."""
    assert block_outcomes, "Should not be empty since SESSION starts with >>>."
    if len(block_outcomes) == block_outcomes.count("pass"):
        result = "pass"
    elif "error" in block_outcomes:
        result = "error"
    else:
        assert "failed" in block_outcomes, "Should only be 'pass', 'failed', 'error'"
        result = "failed"
    return result


@dataclass
class SessionResult:
    """Results from testing REPL examples in one Markdown file."""

    log: List[List[str]]
    number_of_failures: int = 0
    number_of_errors: int = 0
    docstring: str = ""


# This is a designated patch point. Developers: Please treat this as if it were an API.
# Use this to access the internally generated docstring in --replmode.
# To patch:
# - Create a new function to replace modify_docstring().
# - with mock.patch("phmutest.session.modify_docstring", <the new instance>):
# - See example in tests/test_patching.py.
def modify_docstring(text: str) -> str:
    """Use mock.patch to access/modify the file docstring."""
    return text


def run_one_file(
    args: argparse.Namespace,
    fileblocks: phmutest.select.FileBlocks,
    optionflags: int = 0,
    globs: Optional[Dict[str, Any]] = None,
    extractor: Optional[phmutest.globs.AssignmentExtractor] = None,
) -> SessionResult:
    """Run doctests on a single file."""
    if not fileblocks.selected:
        return SessionResult([[fileblocks.built_from, "noblocks", ""]], 0, 0, "")
    lineno_log = []
    tested_blocks = []
    # Log blocks that are skipped.
    # The lineno_log is a list [line number, log entry].
    # The log entry is a list of 3 strings.
    for block in fileblocks.selected:
        if details := skip_block(block, fileblocks.built_from):
            lineno_log.append(details)
        else:
            tested_blocks.append(block)

    # Generate docstring from the remaining blocks.
    # The fences of the FCB are not included in the range.
    text = fileblocks.path.read_text(encoding="utf-8")
    line_ranges = [range(b.line + 1, b.end_line) for b in tested_blocks]
    keeplines = set(itertools.chain(*line_ranges))
    docstring_lines = []
    for num, line in enumerate(text.splitlines(), start=1):
        if num in keeplines:
            docstring_lines.append(line)
        else:
            docstring_lines.append("")

    # The extractor instruments the docstring to discover the assignments.
    # It implements the --share-across-files feature.
    if extractor is not None:
        assert docstring_lines[0] == ""
        assert docstring_lines[-1] == ""
        docstring_lines[0] = ">>> _phm_extract.start(locals().keys())"
        docstring_lines[-1] = ">>> _phm_extract.finish(locals())"
        extra_globs = {"_phm_extract": extractor}
    else:
        extra_globs = None
    docstring = "\n".join(docstring_lines)
    docstring = modify_docstring(docstring)
    if args.generate:
        return SessionResult([[]], 0, 0, docstring)

    # Run doctests.
    finder = doctest.DocTestFinder()
    tests = finder.find(
        docstring, name=fileblocks.built_from, globs=globs, extraglobs=extra_globs
    )
    assert len(tests) == 1, f"expect only one test, got {len(tests)}."
    runner = ExampleOutcomeRunner(verbose=False, optionflags=optionflags)  # type:ignore
    runner.run(tests[0])

    # Determine each overall block result for the log from the file's Example outcomes.
    runner_lineno = set(runner.outcomes)
    for block, line_range in zip(tested_blocks, line_ranges):
        block_lineno = set(line_range) & runner_lineno
        if block_outcomes := [runner.outcomes[line] for line in block_lineno]:
            # Note- If there is a fail-fast there will be no outcomes for a
            #       later block.
            result = get_result(block_outcomes)
            doc_location = phmutest.subtest.make_location_string(
                block, fileblocks.built_from
            )
            details = (block.line, [doc_location, result, ""])
            lineno_log.append(details)

    lineno_log.sort()
    log = [entry for lineno, entry in lineno_log]
    return SessionResult(
        log, runner.number_of_failures, runner.number_of_errors, docstring
    )


def generate(args: argparse.Namespace, block_store: phmutest.select.BlockStore) -> None:
    """Write internally generated docstring(s) to --generate target."""
    for path in args.files:
        fileblocks = block_store.get_blocks(path)
        result = run_one_file(args, fileblocks, optionflags=0, globs=None)
        args.generate.write("# built from " + fileblocks.built_from)
        args.generate.write(result.docstring + "\n")
    args.generate.close()


def process_user_fixture(
    args: argparse.Namespace, log: List[List[str]]
) -> Tuple[contextlib.ExitStack, Optional[Dict[str, Any]]]:
    """Check for --fixture. Create a context manager and get globs from the fixture.

    Return a null context manager if there is no fixture.
    Return an empty dict if there are no fixture globs.
    The globs become visible as global variables to code under test.
    """
    # Create nullcontext cm for with statement below for case where no fixture cleanup.
    # Tell mypy nullcontext looks like an ExitStack.
    globs = None
    cm = cast(contextlib.ExitStack, contextlib.nullcontext())
    if args.fixture:
        modulepackage, function_name = phmutest.cases.get_fixture_parts(args.fixture)
        m = importlib.import_module(modulepackage)
        f = getattr(m, function_name)
        if user_fixture := f(log=log, is_replmode=True):
            globs = user_fixture.globs
            if user_fixture.repl_cleanup:
                # Note- DocTestRunner catches exceptions raised by the Example under
                # test. The ExitStack with callback here assures the fixture cleanup
                # code is run in the event any of this package's code
                # wrapped around DocTestRunner raises an exception.
                cm = contextlib.ExitStack()
                cm.callback(user_fixture.repl_cleanup)

    # The user_fixture.globs default value is None.
    # In the event of sharing across files, the calling code needs globs as an
    # empty mapping to store names that are shared across files.
    if globs is None:
        globs = {}
    else:
        # If --sharing ".", show the fixture globs.
        if phmutest.cases.is_verbose_sharing(args, Path("not_a_md_file")):
            glob_names = ", ".join(globs.keys())
            print(f"{args.fixture} is sharing: {glob_names}")

    return cm, globs


def run_repl(
    args: argparse.Namespace,
    extra_args: List[str],
    block_store: phmutest.select.BlockStore,
) -> phmutest.summary.PhmResult:
    """Test the Python interactive sessions in Markdown FCBs."""

    if args.generate:
        generate(args, block_store)
        return phmutest.summary.EMPTY_PHMRESULT

    optionflags = doctest.FAIL_FAST if "-f" in extra_args else 0
    log: List[List[str]] = []
    number_of_errors = 0
    cm, globs = process_user_fixture(args, log)
    with cm:
        for path in args.files:
            fileblocks = block_store.get_blocks(path)

            # Create object to get assignments by the blocks under test.
            if fileblocks.path in args.share_across_files:
                extractor = phmutest.globs.AssignmentExtractor()
            else:
                extractor = None

            result = run_one_file(args, fileblocks, optionflags, globs, extractor)

            if args.progress:
                phmutest.summary.show_log(result.log)

            # If sharing across files names assigned by the file, udate globs
            # with the shared names.
            # Implement command line --sharing for the file.
            if extractor is not None and globs is not None:
                for name in extractor.assignments:
                    globs[name] = extractor.assignments[name]
                if phmutest.cases.is_verbose_sharing(args, fileblocks.path):
                    shared_names = ", ".join(extractor.assignments.keys())
                    print(f"{fileblocks.built_from} is sharing: {shared_names}")

            if extractor is not None:
                extractor.assignments.clear()

            log.extend(result.log)
            number_of_errors += result.number_of_errors
            if (optionflags & doctest.FAIL_FAST) and (
                result.number_of_failures or result.number_of_errors
            ):
                break

    metrics = phmutest.summary.compute_metrics(
        len(args.files),
        number_of_errors,
        len(block_store.deselected_names),
        log,
    )
    success = (metrics.failed == 0) and (number_of_errors == 0)
    phmresult = phmutest.summary.PhmResult(
        test_program=None, is_success=success, metrics=metrics, log=log
    )
    return phmresult
