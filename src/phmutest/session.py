"""Generate and run doctests for Python interactive session FCBs."""

import argparse
import doctest
import itertools
import sys
import traceback
import typing
from dataclasses import dataclass
from pathlib import Path
from typing import Any, Callable, Dict, List, Optional, Tuple

import phmutest.cases
import phmutest.globs
import phmutest.importer
import phmutest.printer
import phmutest.select
import phmutest.subtest
import phmutest.summary
import phmutest.syntax
from phmutest.direct import Marker
from phmutest.fenced import FencedBlock

ReasonType = Tuple[str, int]


class ExampleOutcomeRunner(doctest.DocTestRunner):
    """Doctest Runner to record Example line number, pass/failed/error status."""

    def __init__(self, **kwargs):  # type: ignore
        super().__init__(**kwargs)
        self.phm_outcomes = {}
        self.phm_failed_reasons: Dict[int, ReasonType] = {}
        self.phm_error_reasons: Dict[int, ReasonType] = {}
        self.phm_number_of_failures = 0
        self.phm_number_of_errors = 0

    def report_success(self, out, test, example, got):  # type: ignore
        line_number = example.lineno + 1
        self.phm_outcomes[line_number] = "pass"
        super().report_success(out, test, example, got)

    def report_failure(self, out, test, example, got):  # type: ignore
        line_number = example.lineno + 1
        self.phm_outcomes[line_number] = "failed"
        self.phm_number_of_failures += 1
        self.phm_failed_reasons[line_number] = ("", line_number)
        super().report_failure(out, test, example, got)

    def report_unexpected_exception(self, out, test, example, exc_info):  # type: ignore
        line_number = example.lineno + 1
        self.phm_outcomes[line_number] = "error"
        self.phm_number_of_errors += 1
        exception_class = phmutest.printer.get_exception_description(
            exc_info[0], exc_info[1]
        )
        self.phm_error_reasons[line_number] = (
            exception_class,
            line_number,
        )
        super().report_unexpected_exception(out, test, example, exc_info)


def skip_block(block: FencedBlock, built_from: str) -> Optional[Tuple[int, List[str]]]:
    """If block should be skipped return details for log entry, otherwise None."""
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
                assert directive.type == Marker.SKIPIF_PYVERSION, "unittest check"
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
    runner_lineno = set(runner.phm_outcomes)
    for block, line_range in zip(tested_blocks, line_ranges):
        block_lineno = set(line_range) & runner_lineno
        if block_outcomes := [runner.phm_outcomes[line] for line in block_lineno]:
            # Note- If there is a fail-fast there will be no outcomes for a
            #       later block.
            result = get_result(block_outcomes)
            doc_location = phmutest.subtest.make_location_string(
                block, fileblocks.built_from
            )
            description, lineno = get_runner_reason(runner, line_range, result)
            # block.line is the start of the FCB.
            # lineno is the line associated with the result
            details = (
                block.line,
                [doc_location, result, description, str(block.line), str(lineno)],
            )
            lineno_log.append(details)

    lineno_log.sort()
    log = [entry for _, entry in lineno_log]
    return SessionResult(
        log, runner.phm_number_of_failures, runner.phm_number_of_errors, docstring
    )


def get_runner_reason(
    runner: ExampleOutcomeRunner, line_range: range, result: str
) -> ReasonType:
    """From the runner, get first of (description, line number) for the line range."""
    # For failed assert statements and raised exceptions in the block report
    # log the reason saved by the test runner. Reports the first problem
    # in the FCB, there may be more unless fail-fast.
    if result == "failed":
        reason_map = runner.phm_failed_reasons
    elif result == "error":
        reason_map = runner.phm_error_reasons
    else:
        return ("", 0)

    reason_lineno = set(reason_map)
    lineno = set(line_range) & reason_lineno
    reasons: List[ReasonType] = []
    for line in line_range:
        if line in lineno:
            reasons.append(reason_map[line])
    return reasons[0]


def generate(args: argparse.Namespace, block_store: phmutest.select.BlockStore) -> None:
    """Write internally generated docstring(s) to --generate target."""
    for path in args.files:
        fileblocks = block_store.get_blocks(path)
        result = run_one_file(args, fileblocks, optionflags=0, globs=None)
        args.generate.write("# built from " + fileblocks.built_from)
        args.generate.write(result.docstring + "\n")
    args.generate.close()


def null_cleanup() -> None:
    """Do nothing cleanup function for case where no fixture cleanup specified."""
    pass


UserFixtureInfo = Tuple[Optional[Dict[str, Any]], Callable[[], None], bool]
"""Function return type [globs, cleanup function, success]."""


def process_user_fixture(
    args: argparse.Namespace, log: List[List[str]]
) -> UserFixtureInfo:
    globs: Optional[Dict[str, Any]] = {}
    cleanup_function = null_cleanup
    f = phmutest.importer.fixture_function_importer(args.fixture.name)
    try:
        user_fixture = f(log=log, is_replmode=True)
    except Exception:
        print("-" * 60)
        print(f"Caught an exception in --fixture {args.fixture}...")
        # Print the traceback to stdout
        # since the doctest failure printing is to stdout.
        traceback.print_exc(file=sys.stdout)
        # Expecting caller to ignore the first two items of the returned tuple.
        return {}, null_cleanup, False

    if user_fixture:
        if user_fixture.globs is not None:
            # Make the fixture's MutableMapping type look like a Dict for doctest.
            globs = typing.cast(Optional[Dict[str, Any]], user_fixture.globs)

        if user_fixture.repl_cleanup is not None:
            cleanup_function = user_fixture.repl_cleanup

        # When --sharing is ".", and the fixture returned some globs, show them.
        if globs and phmutest.cases.is_verbose_sharing(args, Path("placeholder")):
            glob_names = ", ".join(globs.keys())
            print(f"{args.fixture} is sharing: {glob_names}")
    return globs, cleanup_function, True


def update_globs_show_sharing(
    args: argparse.Namespace,
    globs: Optional[Dict[str, Any]],
    fileblocks: phmutest.select.FileBlocks,
    extractor: Optional[phmutest.globs.AssignmentExtractor],
) -> None:
    """If sharing across files copy assigned names to globs, Do --sharing."""
    # Modifies globs in place. Clears the extractor.
    if extractor is not None and globs is not None:
        for name in extractor.assignments:
            globs[name] = extractor.assignments[name]
        if phmutest.cases.is_verbose_sharing(args, fileblocks.path):
            shared_names = ", ".join(extractor.assignments.keys())
            print(f"{fileblocks.built_from} is sharing: {shared_names}")

    if extractor is not None:
        extractor.assignments.clear()


DoctestGlobs = Optional[Dict[str, Any]]
"""Type globs compatible with Python standard library doctest globs."""


def run_repl(
    settings: phmutest.config.Settings,
    block_store: phmutest.select.BlockStore,
) -> phmutest.summary.PhmResult:
    """Test the Python interactive sessions in Markdown FCBs."""
    args = settings.args  # rename
    if args.generate:
        generate(args, block_store)
        return phmutest.summary.EMPTY_PHMRESULT

    optionflags = doctest.FAIL_FAST if "-f" in settings.extra_args else 0
    globs: Optional[Dict[str, Any]] = {}
    cleanup_function = null_cleanup
    log: List[List[str]] = []
    number_of_errors = 0
    if args.fixture:
        globs, cleanup_function, success = process_user_fixture(args, log)
        if not success:
            phm_result = phmutest.summary.EMPTY_PHMRESULT
            phm_result.metrics.number_of_files = len(args.files)
            phm_result.is_success = False
            phm_result.metrics.suite_errors = 1
            phm_result.log = [[str(args.fixture), "error", ""]]
            return phm_result

    try:
        for path in args.files:
            fileblocks = block_store.get_blocks(path)

            # Create object to get assignments by the blocks under test.
            if fileblocks.path in args.share_across_files:
                extractor = phmutest.globs.AssignmentExtractor()
            else:
                extractor = None

            result = run_one_file(args, fileblocks, optionflags, globs, extractor)

            if args.progress:
                null_highlighter = phmutest.syntax.Highlighter()
                null_highlighter.disable()
                phmutest.summary.show_log(
                    log=result.log,
                    highighter=null_highlighter,
                    use_color=args.color,
                )

            update_globs_show_sharing(args, globs, fileblocks, extractor)

            log.extend(result.log)
            number_of_errors += result.number_of_errors
            if (optionflags & doctest.FAIL_FAST) and (
                result.number_of_failures or result.number_of_errors
            ):
                break

    except Exception as e:
        cleanup_function()
        raise e

    cleanup_function()

    metrics = phmutest.summary.compute_metrics(
        num_files=len(args.files),
        suite_errors=number_of_errors,
        num_deselected=-1,  # fill in later in main:generate_and_run
        log=log,
    )
    success = (metrics.failed == 0) and (number_of_errors == 0)
    phmresult = phmutest.summary.PhmResult(
        test_program=None,
        is_success=success,
        metrics=metrics,
        log=log,
    )
    return phmresult
