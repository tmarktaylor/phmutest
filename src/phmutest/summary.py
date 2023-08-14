"""Define main() result type. Print test results."""
import argparse
import unittest
from collections import Counter
from dataclasses import dataclass
from pathlib import Path
from typing import List, Optional, Tuple

import phmutest.subtest

Row = List[str]
Rows = List[Row]
Log = List[List[str]]


def left_align_columns(rows: Rows) -> Tuple[Rows, List[int]]:
    """Left align each cell and justify to maximum item width to visually align."""
    columns = list(zip(*rows))
    widths = [max([len(item) for item in col]) for col in columns]
    justified_columns = []
    for width, column in zip(widths, columns):
        justified_columns.append([item.ljust(width) for item in column])
    # Convert zip's tuples to lists to avoid mypy error.
    aligned_rows = [list(tup) for tup in zip(*justified_columns)]
    return list(aligned_rows), widths


def dot_fill_first_column(rows: Rows, minimum_width: int) -> Rows:
    """Rewrite first column using dot instead of space to fill to width."""
    # Convert zip's tuples to lists to avoid mypy error.
    columns = [list(tup) for tup in zip(*rows)]
    column = columns[0]
    width = max([len(item) for item in column])
    width = max(width, minimum_width)
    filled_column = [item.ljust(width, ".") for item in column]
    # Convert zip's tuples to lists to avoid mypy error.
    filled_columns = [filled_column] + columns[1:]
    filled_rows = [list(tup) for tup in zip(*filled_columns)]
    return list(filled_rows)


def show_table(rows: Rows) -> None:
    """Print table with separators after header row and at end."""
    aligned, widths = left_align_columns(rows)
    aligned.insert(1, ["-" * width for width in widths])
    aligned.append(["-" * width for width in widths])
    for row in aligned:
        print("  ".join(row).rstrip())


def show_setup_errors(log: Log) -> bool:
    """Find errors from setup/teardown in the log and print them. Return true if any."""
    setup_errors = []
    for item in log:
        is_setup = item[0].endswith(phmutest.subtest.SETUP_SUFFIX) or item[0].endswith(
            phmutest.subtest.TEARDOWN_SUFFIX
        )
        if is_setup and item[1] == "error":
            setup_errors.append(item)
    if setup_errors:
        print()
        print("setup and teardown errors")
        print("-------------------------")
        for item in setup_errors:
            print(item[0])
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
    """phmutest.main.main() return type.  Markdown Python example test results."""

    test_program: Optional[unittest.TestProgram]
    is_success: bool
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
    is_success=True,
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
    status = [item[1] for item in log]
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
    if skips := [[item[0], item[2]] for item in log if item[1] == "skip"]:
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
        "generate",  # When True main.generate_and_run() returns without showing args.
        "progress",
        "log",
        "summary",
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
            assert k in single, "sanity check"
            print(f"args.{k}: {format_arg(v)}")
    print()


def show_log(log: Log) -> None:
    """Print a table of the log entries."""
    if log:
        empty_3rd_col = not any([entry[2] for entry in log])
        colulmn_title = "location|label"
        if empty_3rd_col:
            titles = [colulmn_title, "result"]
            log2 = [[entry[0], entry[1]] for entry in log]
        else:
            titles = [colulmn_title, "result", "skip reason"]
            log2 = log
        titled_log = [titles]
        filled_log = dot_fill_first_column(log2, len(colulmn_title))
        titled_log.extend(filled_log)
        show_table(titled_log)


def show_results(args: argparse.Namespace, phmresult: PhmResult) -> None:
    """Print requested test results."""
    if args.summary:
        print()
        print("summary:")
        is_errors = show_setup_errors(phmresult.log)
        if is_errors:
            print()
        show_metrics(phmresult.metrics)
        show_skips(phmresult.log)

    if args.log:
        print()
        print("log:")
        show_args(args)
        show_log(phmresult.log)
