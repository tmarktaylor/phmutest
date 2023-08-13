"""Fixtures used in multiple test files. Checkers are helpful with pytest 6.2.5."""
import inspect
import unittest

import pytest

testcase = unittest.TestCase()
testcase.maxDiff = 20000


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
    """Return Callable(str, str) that dedents want and compares to start of got.

    Note that want string's final newline is removed by inspect.cleandoc().
    """

    def got_endswith_want(want: str, got: str) -> None:
        """Prettier ndiff error output."""
        dedented = inspect.cleandoc(want)
        gotendswith = got[-len(dedented) :]
        testcase.assertEqual(dedented, gotendswith)

    return got_endswith_want
