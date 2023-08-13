"""v0.0.1 Keyword arguments passed to --fixture function and return type Fixture.

These are passed to the fixture function as keyword arguments:

log
    The fixture can append entries to the log.
    List of log entries. Each entry is a list of 3 strings:
        location
            Hint to identify originator of the log entry.

        status
            The strings pass, failed, error, skip, noblocks count towards metrics.

        skip reason


is_replmode
    Python bool. True when commandline argument --replmode is present.

"""
from dataclasses import dataclass
from typing import Callable, MutableMapping, Optional


@dataclass
class Fixture:
    """Object type returned by user's --fixture function.

    globs
        Python dict().
        1. For Python code blocks the keys become global variable names in the
           the generated test file with the corresponding values.
        2. In --replmode globs is passed to doctest.DocTestFinder.find()
           as keyword argument globs.

    repl_cleanup
        Ignored unless replmode. This is only effective for testing
        Python interactive sessions.
        Function that takes no arguments and returns None.
        Fixture function writer supplies this function to release resources acquired
        by the fixture function. This function is called after the final doctest
        completes or if the code running doctests raises an unhandled exception.
    """

    globs: Optional[MutableMapping[str, object]] = None
    repl_cleanup: Optional[Callable[..., None]] = None


FixtureFunction = Callable[..., Optional[Fixture]]
"""Signature of the user supplied --fixture function. Args should be keyword only."""
