"""Context manager to print and log entry and exit status of a code block run."""

import contextlib
import io
import sys
import traceback
from typing import Callable, List, Optional

LogEntry = List[str]
Log = List[LogEntry]


# Indexes to LogEntry
DOC_LOCATION = 0
RESULT = 1
REASON = 2
TESTFILE_BLOCK_START_LINE = 3
EXCEPTION_LINE = 4
STDOUT = 5


# Flags
SHOW_PROGRESS = 0x1  # Enable verbose per subtest case printing.
SHOW_STDOUT = 0x2  # Save stdout printed by FCBs.


# Additional log status values
FRAME = "phmframe"
TRACE = "phmtrace"
DIFFS = "phmdiffs"


def get_exception_description(exc_type, exc_value) -> str:  # type: ignore
    """Return formatted exception class name and the instance value."""
    lines = traceback.format_exception_only(exc_type, exc_value)
    return lines[-1].rstrip()


class Printer:
    """Context manager to print and log test status of a code block.

    Prints messages on entry and exit when verbose flag is set.
    Appends entries to the log.  The log is a list.
    A log entry is a list of 6 strings.
    The first 3 strings are:
    - Markdown file and FCB line number.
    - Test result for FCB.
    - Reason for result where applicable.
    The next two strings are line numbers.
    - The line number of the with _phm_printer statement in the testfile.
    - The line number of the exception.
    The last entry is the captured stdout for the --stdout option.
    Captures stdout and stderr streams
    Prints captured stdout and stderr if __exit__() is called with an exception.
    When stdout is expected and checked, call cancel_print_capture_on_error()
    to prevent captured stdout printing.
    """

    testfile_name: Optional[str] = None
    """Full filename of the generated testfile ."""

    def __init__(
        self,
        log: Log,
        location: str,
        flags: int = 0,
        testfile_lineno: int = 0,
    ):
        """Handle the log, stdio redirection, and pass/failed/error printing.

        Set the destination for log entries. A log entry is a list of 3 to 5 strings.
        The location string is placed in log entries.
        The verbose flag enables __enter__() and __exit__() printing.
        with_statement is the line that has with _phmPrinter statement.
        The example Python starts on the next line after the FCB opening fence.
        The example Python is rendered on the next line after the with _phmPrinter
        statement in the testfile.
        """
        self.log = log
        self.location = location
        self.flags = flags
        self.with_statement = testfile_lineno
        self.capture_stdout = io.StringIO()
        self.capture_stderr = io.StringIO()
        self.cleanup_redirect: Optional[Callable[..., None]] = None
        self.is_print_capture_on_error = True

    def __enter__(self):  # type: ignore
        """Optionally print location to stderr. Capture stdout/stderr for later."""
        if self.flags & SHOW_PROGRESS:
            print(self.location, end="", file=sys.stderr)
        with contextlib.ExitStack() as stack:
            stack.enter_context(contextlib.redirect_stdout(self.capture_stdout))
            stack.enter_context(contextlib.redirect_stderr(self.capture_stderr))
            self.cleanup_redirect = stack.pop_all().close  # method to call later
        return self

    def __exit__(self, exc_type, exc_value, exc_traceback):  # type: ignore
        """Restore redirected stdio, log+print status. All printing goes to stderr."""
        self.cleanup_redirect()  # type: ignore
        with_lineno_str = str(self.with_statement)
        if exc_type is None:
            self._log_and_print(
                status="pass",
                reason="",
                with_lineno_str=with_lineno_str,
                exc_lineno_str="0",
            )
        else:
            # Show FCB line where exception propagates out of the FCB.
            # Show exception class name and value.
            reason = get_exception_description(exc_type, exc_value)
            exc_lineno_str = str(exc_traceback.tb_lineno)
            if exc_type == AssertionError:
                # The AssertionError is raised by either:
                #   - An assert statement in the FCB or code called by the FCB.
                #   - A TestCase.assertEqual() call in the generated testfile for
                #     expected output.
                # We expect the generated testfile to call
                # cancel_print_capture_on_error()
                # before checking expected output. And we expect checking expected
                # output to be at the end of the with Printer(...) context manager
                # statement suite.
                # This places it after any code from the user's FCB.
                # The cancel_print_capture_on_error() clears is_print_capture_on_error.
                # In all other situations we expect is_print_capture_on_error to be
                # True.
                # So when it is False this means we are checking expected output.
                # We don't log a reason because the assertEqual may be testing a
                # multiline string which would mess up the output. The lower case "o"
                # in the location column indicates expected output was checked.
                if not self.is_print_capture_on_error:
                    self._log_and_print(
                        status="failed",
                        reason="",  # no reason here since might be multiline
                        with_lineno_str=with_lineno_str,
                        exc_lineno_str=exc_lineno_str,
                    )
                    # Send the reason here
                    self.log.append(
                        [self.location, DIFFS, reason, with_lineno_str, "0"]
                    )
                else:
                    self._log_and_print(
                        status="failed",
                        reason=reason,
                        with_lineno_str=with_lineno_str,
                        exc_lineno_str=exc_lineno_str,
                    )
            else:
                self._log_and_print(
                    status="error",
                    reason=reason,
                    with_lineno_str=with_lineno_str,
                    exc_lineno_str=exc_lineno_str,
                )

            # This detects deeper frames in the traceback
            # that are sourced from the testfile.
            # The Printer class variable testfile_name provides the
            # full filename of the imported testfile.
            if self.testfile_name:
                tb = exc_traceback
                while tb.tb_next:
                    tb = tb.tb_next
                    if tb.tb_frame.f_code.co_filename == self.testfile_name:
                        self.log.append(
                            [self.location, FRAME, "", "0", str(tb.tb_lineno)]
                        )

            # No printing here.
            self.log_traceback(exc_type, exc_value, exc_traceback)  # type: ignore

            if self.is_print_capture_on_error:
                self._print(self.capture_stdout, title="stdout")
                self._print(self.capture_stderr, title="stderr")

        self.capture_stdout.close()
        self.capture_stderr.close()
        return False

    def log_traceback(self, exc_type, exc_value, exc_traceback):  # type: ignore
        """Add a stackprinter traceback of the exception to the log."""
        try:
            import stackprinter  # type: ignore

            formatted_traceback = "\n" + stackprinter.format(
                (exc_type, exc_value, exc_traceback),
                style="plaintext",
                suppressed_vars=[
                    r"_phm_*",
                    r"self.subTest*",
                    "sys.stderr",
                    "sys.stdout",
                ],
            )
            # Don't need traceback for expected output miss-compare
            # implemented by unittest.TestCase.assertEqual().
            if "assertMultiLineEqual" not in formatted_traceback:
                self.log.append(
                    [
                        self.location,
                        TRACE,
                        formatted_traceback,
                        "0",
                        "0",
                    ]
                )
        except ModuleNotFoundError:
            pass

    def _log_and_print(
        self,
        status: str,
        reason: str = "",
        with_lineno_str: str = "0",
        exc_lineno_str: str = "0",
    ) -> None:
        """Add log entry and optionally print status. Status is pass|failed|error."""
        log_entry = [
            self.location,
            status,
            reason,
            with_lineno_str,
            exc_lineno_str,
        ]
        if self.flags & SHOW_STDOUT:
            log_entry.append(self.capture_stdout.getvalue())
        self.log.append(log_entry)
        if self.flags & SHOW_PROGRESS:
            print(f" ... {status}", file=sys.stderr)

    def cancel_print_capture_on_error(self) -> None:
        """Call this before calling assertEqual() for expected output.

        If assertEqual fails unittest will print the exception message
        sometime after __exit__() runs. We passed the captured stdout
        to assertEqual. It is in the exception message.
        Thus there is no need to print captured stdout here.
        Note that any captured stderr is discarded.

        Append the suffix " o" to the Markdown file location to indicate that
        captured standard output was compared to an expected output block.
        The call here implies that the statements in the code block
        ran without raising an exception or assertion.
        """
        self.is_print_capture_on_error = False
        self.location += " o"

    def stdout(self) -> str:
        """Return captured stdout."""

        return self.capture_stdout.getvalue()

    def _print(self, stringio: io.StringIO, title: str) -> None:
        """Print stringio value to stderr. Print headers."""
        text = stringio.getvalue()
        if text:
            print(f"=== {self.location} {title} ===", file=sys.stderr)
            print(text, end="", file=sys.stderr)
            print("=== end ===", file=sys.stderr)
