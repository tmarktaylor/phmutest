"""Print breakage in broken FCBs."""

import ast
import re
from dataclasses import dataclass
from typing import Dict, List, Optional

import phmutest.select
import phmutest.syntax
from phmutest.fenced import Role
from phmutest.printer import (
    DIFFS,
    DOC_LOCATION,
    EXCEPTION_LINE,
    FRAME,
    REASON,
    RESULT,
    TESTFILE_BLOCK_START_LINE,
    TRACE,
    Log,
    LogEntry,
)

SHOW_TRACEBACK = True
"""
When the traceback extra is installed
display its traceback following each broken FCB in the --log.
"""


@dataclass
class FcbCodeLine:
    """For a line in an FCB, its Markdown file name, start of FCB, and line number."""

    built_from: str = ""
    """Markdown filename."""
    open_fence: int = 0
    """FCB's open fence Markdown file line number."""
    code_line: int = 0
    """Markdown file line number for a line within the FCB."""


class FcbLineMap:
    """Mapping from testfile line number to Markdown and FCB line number.

    # Look up the exception line number in the map to find the
    # FCB line that was rendered at that testfile line.
    # The map entry for an expected output check will return an FCB
    # code_line = 0.
    """

    def __init__(self, block_store: phmutest.select.BlockStore) -> None:
        self.block_store = block_store
        self.map: Dict[int, FcbCodeLine] = {}

    def get(self, testfile_lineno: int) -> FcbCodeLine:
        """Return Markdown information for testfile line number."""
        return self.map.get(testfile_lineno, FcbCodeLine("", 0, 0))

    def add_fcb(
        self, built_from: str, open_fence: int, testfile_with_statement: int
    ) -> None:
        """Add one line to the map for each line in the FCB.

        open_fence is the Markdown file line number of the FCB opening fence.
        testfile_with_statement is the generated testfile line number of the
            with _phmPrinter(_phm_log, ... statement.
        """
        fcb_line_count = self.block_store.number_of_lines(
            built_from=built_from, line=open_fence
        )
        if fcb_line_count:
            fcb_line = open_fence + 1
            testfile_line = testfile_with_statement + 1
            for lineno in range(fcb_line, fcb_line + fcb_line_count):
                self.map[testfile_line] = FcbCodeLine(
                    built_from=built_from,
                    open_fence=open_fence,
                    code_line=lineno,
                )
                testfile_line += 1

    def add_expected_output_check(
        self, built_from: str, open_fence: int, testfile_lineno: int
    ) -> None:
        """Add one line for exception raised by expected output check."""
        # Note that the expected output check comes after the rendered FCB so
        # there is no code_line.
        self.map[testfile_lineno] = FcbCodeLine(
            built_from=built_from,
            open_fence=open_fence,
            code_line=0,
        )


def show_broken_fcbs(
    log: Log,
    block_store: phmutest.select.BlockStore,
    markdown_map: Optional[FcbLineMap],
    highlighter: phmutest.syntax.Highlighter,
) -> None:
    """Print example FCBs that 'failed' or 'error' status and line causing it."""
    # For Python code blocks (not REPL) that failed the expected output check,
    # the whole block is printed.
    # If these are --replmode FCBs there is no markdown_map and no "error",
    # FRAME, or DIFFS.
    for entry in log:
        if entry[RESULT] in ["failed", "error", FRAME]:
            print()
            fcb_info = get_broken_fcb_details(markdown_map, entry)
            built_from = fcb_info.built_from
            open_fence = fcb_info.open_fence
            broken_code_line = fcb_info.code_line

            # Print the FCB line by line indicating the broken line with ">"
            # and stopping there. Print the Markdown file line numbers.
            if built_from:
                contents, role = block_store.get_contents_and_role(
                    built_from=built_from, line=open_fence
                )
                broken_statement_end = find_end_of_statement(
                    contents, role, open_fence, broken_code_line
                )
                print(f"{built_from}:{open_fence}")
                highlighted_fcb = highlighter.highlight(contents)
                lines = highlighted_fcb.splitlines()
                for line_number, line in enumerate(lines, start=open_fence + 1):
                    if line_number == broken_code_line:
                        print(f"> {line_number:4.0f}  {line}")
                    else:
                        print(f"  {line_number:4.0f}  {line}")
                    # show FCB until the breakage
                    if line_number == broken_statement_end:
                        break

                # Print the exception reason.
                if text := entry[REASON]:
                    print(f"        {text}")

        # Additionally print diffs from miss-compare of an expected output block.
        # REASON will be the assertion message from unittest.assertEqual
        # which includes diffs.
        if entry[RESULT] == DIFFS:
            print(entry[REASON])

        # Additionally print a traceback.
        # Show formatted traceback logged by Printer.
        # The traceback is logged when the project [traceback] extra is installed.
        if (entry[RESULT] == TRACE) and SHOW_TRACEBACK:
            print(entry[REASON])


def get_broken_fcb_details(
    markdown_map: Optional[FcbLineMap], entry: LogEntry
) -> FcbCodeLine:
    """Get broken FCB details for either the map or the log entry."""
    if markdown_map:
        # Determine the Markdown FCB and the line in it that broke.
        # We assume the traceback is revisiting a different block
        # that ran earlier.
        # Now the block is at depth in a traceback and we retrieve the
        # information from the testfile_map.
        # We only use the markdown_map to look up info for FRAMEs.
        fcb_info = markdown_map.get(int(entry[EXCEPTION_LINE]))
        if not fcb_info.built_from:
            print(
                "phmutest.fcb.show_broken_fcbs()- markdown_map is"
                f" missing key = {entry[EXCEPTION_LINE]}."
            )
    else:
        # Determine the Markdown FCB and the line in it that broke.
        # If an expected output check raised the exception, the
        # broken_code_line will be beyond the end of the FCB because the
        # _phm_testcase.assertEqual statement in the testfile is
        # beyond the end of the FCB. So the whole FCB is printed.
        built_from, open_fence = phmutest.subtest.decode_location_string(
            entry[DOC_LOCATION]
        )
        testfile_with_statement = int(entry[TESTFILE_BLOCK_START_LINE])
        exc_line_number = int(entry[EXCEPTION_LINE])
        offset = exc_line_number - testfile_with_statement
        broken_code_line = open_fence + offset
        fcb_info = FcbCodeLine(built_from, open_fence, broken_code_line)
    return fcb_info


def make_markdown_map(
    testfile_lines: List[str], block_store: phmutest.select.BlockStore
) -> FcbLineMap:
    """Map testfile line number(s) to the rendered Markdown FCB."""
    # Create a map to lookup the markdown information for a given testfile line number.
    # The lookup typically happens when a line for the testfile appears in a
    # exception traceback frame.
    location_pattern = r"^\s*with _phmPrinter[(]_phm_log," r' "(?P<location>.*?)",'
    markdown_map = FcbLineMap(block_store)
    location = ""
    built_from = ""
    open_fence = 0
    for testfile_lineno, line in enumerate(testfile_lines, start=1):
        if "with _phmPrinter(" in line:
            # Add lines for an FCB to the markdown map.
            # Get the Markdown FCB location from the "with _phmPrinter(" line.
            m = re.search(
                pattern=location_pattern,
                string=line,
            )
            assert m, "with _phmPrinter is missing valid doc location."
            location = m["location"]  # avoid mypy error
            built_from, open_fence = phmutest.subtest.decode_location_string(location)
            markdown_map.add_fcb(
                built_from=built_from,
                open_fence=open_fence,
                testfile_with_statement=testfile_lineno,
            )
        elif location and "_phm_testcase.assertEqual(" in line:
            # Add a testfile line for the expected output assertEqual statement.
            # Use built_from, open_fence left over from the
            # 'if "with _phmPrinter" in line:' if suite.
            markdown_map.add_expected_output_check(
                built_from=built_from,
                open_fence=open_fence,
                testfile_lineno=testfile_lineno,
            )
            location = ""  # done until next with _phmPrinter line
    return markdown_map


def find_end_of_statement(
    contents: str, role: Role, open_fence: int, broken_code_line: int
) -> int:
    """Guess the end line number of the statement at broken_code_line."""
    if role == Role.SESSION:
        # For REPL try to print one extra line.
        # This can be beyond the end of the FCB.
        return broken_code_line + 1
    at_most_lines = 12
    guess = 0
    relative_lineno = broken_code_line - open_fence
    try:
        tree = ast.parse(contents)
        for node in ast.walk(tree):
            if isinstance(node, ast.stmt):
                if node.lineno == relative_lineno:
                    assert node.end_lineno is not None  # avoid mypy error
                    guess = open_fence + node.end_lineno
                    break
    except Exception:
        # If guess fails, just return the broken line number.
        return broken_code_line
    guess = max(guess, broken_code_line)  # at least the broken line
    guess = min(guess, broken_code_line + at_most_lines - 1)
    return guess
