"""Test Globals class from globs.py."""
import copy
import doctest
import sys
from unittest.mock import patch

import pytest

import phmutest.main
from phmutest.globs import AssignmentExtractor, Globals

MYGLOBAL = 1


def test_noshareid():
    """Cover paths when there is no verbose printing.

    1. globs.copy().
    2. globs.update() with already imported modules.
    """
    globs = Globals(__name__)
    items = dict(one="1", two="2", aftertwo="3")
    globs.update(additions=items)
    assert globs.copy() == {"one": "1", "two": "2", "aftertwo": "3"}
    globs.clear()
    assert globs.global_names == set()
    assert globs.copy() == {}

    # 2.
    assert "copy" in globs.original_attributes
    assert "sys" in globs.original_attributes
    items = {
        "copy": copy,
        "sys": sys,
    }
    globs.update(additions=items)
    assert globs.get_names() == set()
    assert globs.copy() == dict()

    globs.clear()
    assert globs.global_names == set()
    assert globs.copy() == {}
    del globs


class TestGlobals:
    def setup_method(self):
        self.globs = Globals(__name__, shareid="TestGlobs")

    def teardown_method(self):
        self.globs.clear()
        assert self.globs.global_names == set()
        assert self.globs.copy() == {}
        del self.globs

    def test_initialize_globals(self):
        """Create a Globals instance to manage globals on the current module."""
        assert "MYGLOBAL" in self.globs.original_attributes
        assert self.globs.shareidmsg == "sharing-TestGlobs"
        self.globs.global_names == set()
        assert "MYGLOBAL" not in self.globs.get_names()

    def test_already_exists_error(self):
        """Try to update a name that existed in the orignal module."""
        with pytest.raises(AttributeError) as exc_info:
            self.globs.update(additions={"MYGLOBAL": None}, existing_names=set())
        print("\n" + str(exc_info.value))
        assert "Not allowed to replace global name MYGLOBAL" in str(exc_info.value)

    def test_update_bad_args(self):
        with pytest.raises(ValueError):
            self.globs.update(additions=None)
        with pytest.raises(TypeError):
            self.globs.update(additions=2)

    def test_update_name_pops(self):
        """Try an update with names that get popped before the update."""
        # Exercises the _ = additions.pop('XXX', None) lines
        items = {
            "self": None,
            "cls": None,
            "_phm_expected_str": None,
            "_phm_printer": None,
            "_phm_expected_str": None,
            "_phm_fixture": None,
        }
        self.globs.update(additions=items)
        assert self.globs.get_names() == set()
        assert self.globs.copy() == dict()

    def test_update_name_ifpops(self):
        """Try an update with names that get conditionally popped before the update."""
        # Exercises the if XXX in additions.pop('XXX', None) lines
        items = {
            "contextlib": None,
            "io": None,
            "sys": None,
            "example_variable": 1111,  # does not get popped
        }
        self.globs.update(additions=items)
        # Note get_names() does not include sys since sys is a global of this file.
        assert self.globs.get_names() == {"example_variable", "contextlib", "io"}
        assert self.globs.copy() == {
            "example_variable": 1111,
            "contextlib": None,
            "io": None,
        }

    def test_more_additions(self):
        """Add more items to the namespace.."""
        items = {
            "example_variable": 1111,
        }
        self.globs.update(additions=items)
        more_items = {"A": None, "B": None, "C": None}
        self.globs.update(additions=more_items)
        namespace = self.globs.copy()
        assert len(namespace) == 4
        assert namespace["example_variable"] == 1111
        for name in more_items.keys():
            assert name in namespace

    def test_no_extras_error(self):
        """Simulate a original global integrity check failure.

        This should fail the integrity check: current == original + managed.
        """
        items1 = {"new_name1": 1111}
        self.globs.update(additions=items1)
        items2 = {"new_name2": 2222}
        # Remove new_name1 from global_names.
        newobj = copy.copy(self.globs.global_names)
        newobj.remove("new_name1")
        with patch.object(self.globs, "global_names", newobj):
            with pytest.raises(AttributeError) as exc_info:
                self.globs.update(additions=items2)
        assert "phmutest- current attributes == original +" in str(exc_info.value)

    def test_check_integrity_error(self):
        """Test a different path through check_integrity().

        Add a name to the module that is not an original and is not managed.
        This should fail the integrity check: current == original + managed.
        The module contains the 'extra' bogus1.
        """
        m = sys.modules.copy()[__name__]
        with patch.object(m, "bogus1", None, create=True):
            with pytest.raises(AttributeError) as exc_info:
                self.globs.check_integrity(existing_names=set())
            assert "extras= bogus1" in str(exc_info.value)
            assert "current attributes == original + global" in str(exc_info.value)
            # No error expected
            self.globs.check_integrity(existing_names={"bogus1"})

    def test_no_originals_error(self):
        """Simulate no pre-existing globals/module attributes can be managed error."""
        # Note that check_integrity() is believed to redundant.
        # It is called near the end of update().
        # This test case simulates a failure by calling check_integrity() directly.
        assert self.globs.get_names() == set()
        items1 = {"new_name1": 1111}
        self.globs.update(additions=items1)
        assert "MYGLOBAL" in self.globs.original_attributes
        # Add the original module name MYGLOBALS to global_names.
        newobj = copy.copy(self.globs.global_names)
        newobj.add("MYGLOBAL")
        with patch.object(self.globs, "global_names", newobj):
            with pytest.raises(AttributeError) as exc_info:
                self.globs.check_integrity(existing_names=set(items1.keys()))
        assert "phmutest- no pre-existing globals/module" in str(exc_info.value)

    def test_omit_already_imported(self):
        """Updates contain already imported modules, pre-existing, or duplicates."""
        assert "copy" in self.globs.original_attributes
        assert "sys" in self.globs.original_attributes
        items = {
            "copy": copy,
            "sys": sys,
        }
        self.globs.update(additions=items)
        assert self.globs.get_names() == set()
        assert self.globs.copy() == dict()


def test_extractor(capsys):
    """Show extractor discovers names assigned in a Python interactive session.

    Also shows that rebinding a name passed in by run_docstring_examples() arg
    globs is not reflected in globs after the doctest.  See AGLOBALVAR below.
    """

    docstring = """\n
>>> g1 = 7
>>> g2 = 999

>>> myextractor.start(locals().keys())
>>> # Only names assigned between start() and finish() should be in extract.globs().
>>> import math

>>> mylist = [1, 2, 3]
>>> a, b = 10, 11

>>> def doubler(x):
...    return x * 2

>>> class MyClass:
...    pass

>>> assert AGLOBALVAR == 1111
>>> AGLOBALVAR = "abcd"          # rebind a name from fixture globs
>>> assert AGLOBALVAR == "abcd"  # succeeds only within this docstring
>>> myextractor.finish(locals())

>>> # These should not be in myextractor.assignments()
>>> g3 = "hello"
>>> pi = math.pi
"""
    import math

    extractor = AssignmentExtractor()
    globs = {"myextractor": extractor, "AGLOBALVAR": 1111}
    doctest.run_docstring_examples(docstring, globs=globs, name="test_myextractor")
    want = set(["math", "mylist", "a", "b", "doubler", "MyClass"])
    assert want == set(extractor.assignments)
    assert extractor.assignments["math"] == math
    assert extractor.assignments["mylist"] == [1, 2, 3]
    assert extractor.assignments["a"] == 10
    assert extractor.assignments["b"] == 11
    assert extractor.assignments["doubler"](2) == 4
    assert "AGLOBALVAR" not in extractor.assignments
    assert "myextractor" not in extractor.assignments
    assert "g3" not in extractor.assignments
    assert "pi" not in extractor.assignments

    # Notice that the passed in globs names are reported by locals().
    assert "AGLOBALVAR" in extractor.start_names
    assert "myextractor" in extractor.start_names

    # Show that AGLOBALVAR does not reflect the assignment in the docstring.
    assert globs["AGLOBALVAR"] == 1111

    # doctest.run_docstring_examples only prints if errors. So the assert
    # will fail and print the captured output.
    assert capsys.readouterr().out == ""


def test_share_testfile_imports():
    """Use same imports in an example that are at the top level of the testfile.

    Logic in globs.py prevents the copy to the module globals. The example works
    because the imports already exist at the top level of the testfile.
    Also note that --sharing will not show these imports.

    Generated testfile top level imports:
      import contextlib
      import io
      import sys
      import unittest
    """
    command = (
        "tests/md/shareimports1.md tests/md/shareimports2.md "
        "--share-across-files tests/md/shareimports1.md"
    )
    args = command.split()
    phmresult = phmutest.main.main(args)
    want = phmutest.summary.Metrics(
        number_blocks_run=4,
        passed=4,
        failed=0,
        skipped=0,
        suite_errors=0,
        number_of_files=2,
        files_with_no_blocks=0,
        number_of_deselected_blocks=0,
    )
    assert want == phmresult.metrics
    assert phmresult.is_success is True
