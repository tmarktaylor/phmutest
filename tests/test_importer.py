"""Try code that imports the fixture function.

Show that a different module object is created by fixture_function_importer
for the situation when the fixture function is an already imported file.
This file is imported to a module name not in Python's module
cache. We assume that the file's top level module code is run again.

The fixture function should be in a file which can be reloaded.
The fixture function should not be in a file which has side effects
when imported.
"""

import sys

import phmutest.importer

this_module = sys.modules.copy()[__name__]
print("\ntest_importer- module id=", id(this_module))


def imported_funcion(**kwargs):
    """Print the string passed as keyword arg message."""
    return kwargs["message"]


def test_fixture_function_importer():
    assert imported_funcion(message="spam") == "spam"
    func = phmutest.importer.fixture_function_importer(
        "tests.test_importer.imported_funcion"
    )
    assert func(message="very small rocks") == "very small rocks"


def test_loads_a_separate_module():
    """Show evidence that a new object was imported rather than a cached module.

    Run pytest with --capture=tee-sys to see the stdout printing.
    """
    module1 = phmutest.importer.python_file_importer(
        "tests/test_importer.py", "tests_test_importer1"
    )
    module2 = phmutest.importer.python_file_importer(
        "tests/test_importer.py", "tests_test_importer2"
    )
    assert id(module1) != id(module2)
    assert id(this_module) != id(module1)
    assert id(this_module) != id(module2)

    assert module1.imported_funcion(message="larch") == "larch"
    assert module2.imported_funcion(message="shrubbery") == "shrubbery"


if __name__ == "__main__":  # pragma: no cover
    """Invoke this file with python to run the tests without pytest."""
    # prints test_importer three times
    print()
    print("test_imports_function-")
    test_fixture_function_importer()
    print()
    print("test_loads_a_separate_module-")
    test_loads_a_separate_module()
