"""Python unittest test file generated by Python Package phmutest."""
import unittest

from phmutest.globs import Globals as _phmGlobals
from phmutest.printer import Printer as _phmPrinter
from phmutest.systool import sys_tool as _phm_sys

_phm_globals = None
_phm_testcase = unittest.TestCase()
_phm_testcase.maxDiff = None
_phm_log = []


def setUpModule():

    global _phm_globals
    _phm_log.append(["setUpModule", "", ""])
    _phm_globals = _phmGlobals(__name__, shareid="")


def tearDownModule():

    _phm_log.append(["tearDownModule", "", ""])
    _phm_globals.clear()


class Test001(unittest.TestCase):
    """Test cases generated from docs/share/file1.md."""

    def tests(self):

        # ------ docs/share/file1.md:5 ------
        with self.subTest(msg="docs/share/file1.md:5"):
            with _phmPrinter(_phm_log, "docs/share/file1.md:5", False):
                from dataclasses import dataclass

        # ------ docs/share/file1.md:9 ------
        with self.subTest(msg="docs/share/file1.md:9"):
            with _phmPrinter(_phm_log, "docs/share/file1.md:9", False):
                @dataclass
                class BeverageActivity:
                    beverage: str
                    activity: str

                    def combine(self) -> str:
                        if self.beverage == "coffee" and self.activity == "coding":
                            return "enjoyment"
                        else:
                            return self.beverage + "-" + self.activity

        # ------ docs/share/file1.md:24 ------
        with self.subTest(msg="docs/share/file1.md:24"):
            with _phmPrinter(_phm_log, "docs/share/file1.md:24", False) as _phm_printer:
                cc = BeverageActivity("coffee", "coding")
                print(cc.combine())
                # line 29
                _phm_expected_str = """\
enjoyment
"""
                _phm_printer.cancel_print_capture_on_error()
                _phm_testcase.assertEqual(_phm_expected_str, _phm_printer.stdout())

        # ------ docs/share/file1.md:35 ------
        with self.subTest(msg="docs/share/file1.md:35"):
            with _phmPrinter(_phm_log, "docs/share/file1.md:35", False):
                we = BeverageActivity("water", "exercise")

        _phm_globals.update(additions=locals(), built_from="docs/share/file1.md", existing_names=None)


class Test002(unittest.TestCase):
    """Test cases generated from docs/share/file2.md."""

    def tests(self):

        # ------ docs/share/file2.md:8 ------
        with self.subTest(msg="docs/share/file2.md:8"):
            with _phmPrinter(_phm_log, "docs/share/file2.md:8", False) as _phm_printer:
                print(we.combine())
                # line 12
                _phm_expected_str = """\
water-exercise
"""
                _phm_printer.cancel_print_capture_on_error()
                _phm_testcase.assertEqual(_phm_expected_str, _phm_printer.stdout())

        # ------ docs/share/file2.md:18 ------
        with self.subTest(msg="docs/share/file2.md:18"):
            with _phmPrinter(_phm_log, "docs/share/file2.md:18", False) as _phm_printer:
                bp = BeverageActivity("beer", "partying")
                print(bp.combine())
                # line 23
                _phm_expected_str = """\
beer-partying
"""
                _phm_printer.cancel_print_capture_on_error()
                _phm_testcase.assertEqual(_phm_expected_str, _phm_printer.stdout())

        _phm_globals.update(additions=locals(), built_from="docs/share/file2.md", existing_names=None)


class Test003(unittest.TestCase):
    """Test cases generated from docs/share/file3.md."""

    def tests(self):

        # ------ docs/share/file3.md:7 ------
        with self.subTest(msg="docs/share/file3.md:7"):
            with _phmPrinter(_phm_log, "docs/share/file3.md:7", False) as _phm_printer:
                print(bp.combine())
                # line 11
                _phm_expected_str = """\
beer-partying
"""
                _phm_printer.cancel_print_capture_on_error()
                _phm_testcase.assertEqual(_phm_expected_str, _phm_printer.stdout())

        # ------ docs/share/file3.md:17 ------
        with self.subTest(msg="docs/share/file3.md:17"):
            with _phmPrinter(_phm_log, "docs/share/file3.md:17", False) as _phm_printer:
                ss = BeverageActivity("soda", "snacking")
                print(ss.combine())
                # line 22
                _phm_expected_str = """\
soda-snacking
"""
                _phm_printer.cancel_print_capture_on_error()
                _phm_testcase.assertEqual(_phm_expected_str, _phm_printer.stdout())
