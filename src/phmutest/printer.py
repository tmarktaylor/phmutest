"""Context manager to print and log entry and exit status of a code block run."""
import contextlib
import io
import sys
from typing import Callable, List, Optional

Log = List[List[str]]


class Printer:
    """Context manager to print and log test status of a code block.

    Prints messages on entry and exit when verbose is True.
    Appends messages to the log.  The log is a list.
    A message is a list of 3 strings.
    Captures stdout and stderr streams.
    Prints captured stdout and stderr if __exit__() is called with an exception.
    When stdout is expected and checked, call cancel_print_capture_on_error()
    to prevent captured stdout printing.
    """

    def __init__(self, log: Log, location: str, verbose: bool = False):
        """Handle the log, stdio redirection, and pass/failed/error printing.

        Set the destination for log entries. A log entry is a list of 3 strings.
        The location string is placed in log entries.
        The verbose flag enables __enter__() and __exit__() printing.
        """
        self.log = log
        self.location = location
        self.verbose = verbose
        self.capture_stdout = io.StringIO()
        self.capture_stderr = io.StringIO()
        self.cleanup_redirect: Optional[Callable[..., None]] = None
        self.is_print_capture_on_error = True

    def __enter__(self):  # type: ignore
        """Optionally print location to stderr. Capture stdout/stderr for later."""
        if self.verbose:
            print(self.location, end="", file=sys.stderr)
        with contextlib.ExitStack() as stack:
            stack.enter_context(contextlib.redirect_stdout(self.capture_stdout))
            stack.enter_context(contextlib.redirect_stderr(self.capture_stderr))
            self.cleanup_redirect = stack.pop_all().close  # method to call later
        return self

    def __exit__(self, exc_type, exc_value, traceback):  # type: ignore
        """Restore redirected stdio, log+print status. All printing goes to stderr."""
        self.cleanup_redirect()  # type: ignore
        if exc_type is None:
            self._log_and_print("pass")
        else:
            if exc_type == AssertionError:
                self._log_and_print("failed")
            else:
                self._log_and_print("error")
            if self.is_print_capture_on_error:
                self._print(self.capture_stdout, title="stdout")
                self._print(self.capture_stderr, title="stderr")

        self.capture_stdout.close()
        self.capture_stderr.close()
        return False

    def _log_and_print(self, status: str) -> None:
        """Add log entry and optionally print status. Status is pass|failed|error."""
        self.log.append([self.location, status, ""])
        if self.verbose:
            print(f" ... {status}", file=sys.stderr)

    def cancel_print_capture_on_error(self) -> None:
        """Call this before calling assertEqual() for expected output.

        If assertEqual fails unittest will print the exception message
        sometime after __exit__() runs. We passed the captured stdout
        to assertEqual. It is in the exception message.
        Thus there is no need to print captured stdout here.
        Note that any captured stderr is discarded.
        """
        self.is_print_capture_on_error = False

    def stdout(self) -> str:
        """Return captured stdout."""

        return self.capture_stdout.getvalue()

    @staticmethod
    def _print(stringio: io.StringIO, title: str) -> None:
        """Print stringio value to stderr. Print headers."""
        text = stringio.getvalue()
        if text:
            print(f"=== phmutest: captured {title} ===", file=sys.stderr)
            print(text, end="", file=sys.stderr)
            print("=== end ===", file=sys.stderr)
