"""Fixtures used in multiple test files. Checkers are helpful with pytest 6.2.5."""

import inspect
import unittest
from typing import List

import pytest

testcase = unittest.TestCase()
testcase.maxDiff = None


@pytest.fixture()
def checker():
    """Return Callable(str, str) that dedents want and compares to got.

    Note that want string's final newline is removed by inspect.cleandoc().
    """

    def want_and_got_same(want: str, got: str) -> None:
        """Prettier ndiff error output."""
        dedented = inspect.cleandoc(want)
        testcase.assertEqual(dedented, got)

    return want_and_got_same


@pytest.fixture()
def startswith_checker():
    """Return Callable(str, str) that dedents want and compares to start of got.

    Note that want string's final newline is removed by inspect.cleandoc().
    """

    def got_startswith_want(want: str, got: str) -> None:
        """Prettier ndiff error output."""
        dedented = inspect.cleandoc(want)
        gotstartswith = got[: len(dedented)]
        testcase.assertEqual(dedented, gotstartswith)

    return got_startswith_want


@pytest.fixture()
def endswith_checker():
    """Return Callable(str, str) that dedents want and compares to end of got.

    Note that want string's final newline is removed by inspect.cleandoc().
    """

    def got_endswith_want(want: str, got: str) -> None:
        """Prettier ndiff error output."""
        dedented = inspect.cleandoc(want)
        gotendswith = got[-len(dedented) :]
        testcase.assertEqual(dedented, gotendswith)

    return got_endswith_want


@pytest.fixture()
def ordered_checker():
    """Return Callable(str, List[str]) looks for each str in turn."""

    def got_ordered_checker(got: str, substrings: List[str]) -> None:
        start = 0
        for want in substrings:
            try:
                start = got.index(want, start)
                print(f"found   {want!r}")
            except ValueError:
                print(f"missing {want!r}")
                assert False, f"missing {want!r} after index {start}"
            start += len(want)
        print("Success")

    return got_ordered_checker
