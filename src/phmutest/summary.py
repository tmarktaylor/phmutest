"""Define main() result type. Print test results."""

import argparse
import unittest
from collections import Counter
from dataclasses import dataclass
from pathlib import Path
from typing import Iterable, List, Optional, Tuple

import phmutest.color
import phmutest.config
import phmutest.fcb
import phmutest.printer
import phmutest.select
import phmutest.subtest
import phmutest.syntax
from phmutest.printer import (
    DIFFS,
    DOC_LOCATION,
    FRAME,
    REASON,
    RESULT,
    STDOUT,
    TRACE,
    Log,
)

Column = List[str]
Columns = List[Column]
Row = List[str]
Rows = List[Row]
Widths = List[int]


def transpose(grid: Iterable[Iterable[str]]) -> List[List[str]]:
    """Swap rows for columns or columns for rows."""
    return [list(tup) for tup in zip(*grid)]


def left_align_columns(rows: Rows) -> Tuple[Columns, Widths]:
    """Left align each cell and justify to maximum item width to visually align."""
    columns = transpose(rows)
    widths = [max([len(item) for item in col]) for col in columns]
    justified_columns = []
    for width, column in zip(widths, columns):
        justified_columns.append([item.ljust(width) for item in column])
    return justified_columns, widths


def dot_fill_column(column: Column, width: int) -> None:
    """Modifies in place a column replacing up to width trailing spaces with '.'."""
    for i, item in enumerate(column):
        column[i] = item.rstrip().ljust(width, ".")


def show_table(rows: Rows) -> None:
    """Align, justify and print table with header."""
    justified_columns, widths = left_align_columns(rows)
    aligned_rows = transpose(justified_columns)
    add_table_headers(aligned_rows, widths)
    for row in aligned_rows:
        print("  ".join(row).rstrip())


def add_table_headers(aligned: Rows, widths: Widths) -> None:
    """Print table with separators after header row and at end."""
    headers = ["-" * width for width in widths]
    aligned.insert(1, headers)
    aligned.append(headers)


def show_setup_errors(log: Log) -> bool:
    """Find errors from setup/teardown in the log and print them. Return true if any."""
    setup_errors = []
    for item in log:
        is_setup = item[DOC_LOCATION].endswith(phmutest.subtest.SETUP_SUFFIX) or item[
            DOC_LOCATION
        ].endswith(phmutest.subtest.TEARDOWN_SUFFIX)
        if is_setup and item[RESULT] == "error":
            setup_errors.append(item)
    if setup_errors:
        print()
        print("setup and teardown errors")
        print("-------------------------")
        for item in setup_errors:
            print(item[DOC_LOCATION])
    return bool(setup_errors)


@dataclass
class Metrics:
    """Counts of block test results and input files."""

    number_blocks_run: int
    passed: int
    failed: int
    skipped: int
    suite_errors: int
    number_of_files: int  # Includes files that didn't get to run due to -f fail fast.
    files_with_no_blocks: int
    number_of_deselected_blocks: int


@dataclass
class PhmResult:
    """phmutest.main.command() return type.  Markdown Python example test results."""

    test_program: Optional[unittest.TestProgram]
    is_success: Optional[bool]
    metrics: Metrics
    log: List[List[str]]


EMPTY_METRICS = Metrics(
    number_blocks_run=0,
    passed=0,
    failed=0,
    skipped=0,
    suite_errors=0,
    number_of_files=0,
    files_with_no_blocks=0,
    number_of_deselected_blocks=0,
)


EMPTY_PHMRESULT = PhmResult(
    test_program=None,
    is_success=None,
    metrics=EMPTY_METRICS,
    log=[[]],
)
"""Used when --generate and --replmode to avoid an Optional return value."""


def compute_metrics(
    num_files: int, suite_errors: int, num_deselected: int, log: Log
) -> Metrics:
    """Calculate the test run metrics from the log entries."""
    # A log entry is a list of 3 strings.
    # The second string is the status of the log entry,
    # Code in printer.py, cases.py and skip.py append log entries
    # using hard coded string constants.
    status = [item[RESULT] for item in log]
    counts = Counter(status)
    metrics = Metrics(
        number_blocks_run=counts["pass"] + counts["failed"] + counts["error"],
        passed=counts["pass"],
        failed=counts["failed"],
        skipped=counts["skip"],
        suite_errors=suite_errors,
        number_of_files=num_files,
        files_with_no_blocks=counts["noblocks"],
        number_of_deselected_blocks=num_deselected,
    )
    return metrics


def show_metrics(metrics: Metrics) -> None:
    """Print metrics in aligned ASCII table format."""
    cells = [
        ["metric", ""],  # headings
        ["blocks run", str(metrics.number_blocks_run)],
        ["blocks passed", str(metrics.passed)],
        ["blocks failed", str(metrics.failed)],
        ["blocks skipped", str(metrics.skipped)],
        ["suite errors", str(metrics.suite_errors)],
        ["Markdown files", str(metrics.number_of_files)],
        ["files with no blocks", str(metrics.files_with_no_blocks)],
        ["deselected blocks", str(metrics.number_of_deselected_blocks)],
    ]
    # right justify the second column
    width = max(len(row[1]) for row in cells)
    for row in cells:
        row[1] = row[1].rjust(width)
    show_table(cells)


def show_skips(log: Log) -> None:
    """Print table of blocks that were skipped with the reason."""
    if skips := [
        [item[DOC_LOCATION], item[REASON]] for item in log if item[RESULT] == "skip"
    ]:
        cells = [["skipped blocks", "reason"]] + skips
        print()
        show_table(cells)


def format_arg(value: object) -> str:
    """Return representation of the value. Show files in posix."""
    if isinstance(value, Path):
        value = value.as_posix()
    return repr(str(value))


def show_args(args: argparse.Namespace) -> None:
    """Print the parsed command line argument values."""
    argmap = vars(args)
    multiple = [
        "files",
        "skip",
        "share_across_files",
        "setup_across_files",
        "sharing",
        "select",
        "deselect",
    ]
    single = [
        "fixture",
        "config",
        "replmode",
        "color",
        "style",
        "generate",  # When True main.generate_and_run() returns without showing args.
        "progress",
        "log",
        "summary",
        "stdout",
        "report",
    ]

    # Developers: If you added or removed or renamed arguments in parser (main.py)
    #             update multiple and single lists above to avoid assertions below.
    #             Don't need to list 'help' and 'version'.
    assert len(set(multiple) | set(single)) == len(argmap), "most args must be printed"
    assert (
        set(multiple) | set(single)
    ) == argmap.keys(), "no missing or duplicates args"
    for k, v in argmap.items():
        if k in multiple:
            if v:
                for value in v:
                    print(f"args.{k}: {format_arg(value)}")
        elif v:
            assert k in single, "unittest check"
            print(f"args.{k}: {format_arg(v)}")
    print()


def show_log(
    log: Log, highighter: phmutest.syntax.Highlighter, use_color: bool = False
) -> None:
    """Print a table of the log entries."""
    if log:
        empty_3rd_col = not any([entry[REASON] for entry in log])
        column_title = "location|label"
        if empty_3rd_col:
            log2 = [[column_title, "result"]]
            log2.extend([[entry[DOC_LOCATION], entry[RESULT]] for entry in log])
            log3 = log2
        else:
            log2 = [[column_title, "result", "reason"]]
            # Remove entries for RESULT values that aren't displayed.
            log2a = [
                entry for entry in log if entry[RESULT] not in [TRACE, FRAME, DIFFS]
            ]
            log2.extend(log2a)
            # Remove the remaining columns, if present.
            log3 = [row[0:3] for row in log2]

        # Align and justify. Return columns and column widths.
        columns, widths = left_align_columns(log3)

        # Disassemble into justified titles and justified columns.
        rows = transpose(columns)
        justified_titles = rows.pop(0)
        justified_columns = transpose(rows)

        # Replace space fill with "." in the first column of cells.
        dot_fill_column(justified_columns[0], widths[0])

        # Colorize the result values in the second column,
        colorize_results(justified_columns[RESULT], use_color)

        # Assemble the table from the title row and the rows.
        justified_rows = transpose(justified_columns)
        table = [justified_titles]
        table.extend(justified_rows)
        add_table_headers(table, widths)
        for row in table:
            print("  ".join(row).rstrip())


def colorize_results(results: List[str], use_color: bool = False) -> None:
    """Insert ANSI terminal color sequences to list of test results. Modify in place."""
    # Replace matching result string with the colorized version of it.
    if hasattr(phmutest.color, "colorize_result"):
        for ix, item in enumerate(results):
            results[ix] = phmutest.color.colorize_result(item, use_color)


def show_results(
    settings: phmutest.config.Settings,
    block_store: phmutest.select.BlockStore,
    markdown_map: Optional[phmutest.fcb.FcbLineMap],
    phmresult: PhmResult,
) -> None:
    """Print requested test results."""
    args = settings.args  # rename
    if args.summary:
        print()
        print("summary:")
        is_errors = show_setup_errors(phmresult.log)
        if is_errors:
            print()
        show_metrics(phmresult.metrics)
        show_skips(phmresult.log)

    if args.log and phmresult.log:
        print()
        print("log:")
        show_args(args)
        show_log(phmresult.log, settings.highlighter, args.color)
        phmutest.fcb.show_broken_fcbs(
            phmresult.log,
            block_store,
            markdown_map,
            settings.highlighter,
        )

    if args.stdout and phmresult.log:
        print("\nstdout:")
        for entry in phmresult.log:
            if len(entry) == (STDOUT + 1) and entry[STDOUT]:
                print(entry[STDOUT], end="")
