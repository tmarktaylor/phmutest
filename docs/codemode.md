# Code mode

## Testfile generation

Code and expected output blocks are tested internally with Python
standard library [unittest][1].

A temporary unittest Python source file is generated and run.
Added logic records the pass/failed/error/skip status and
Markdown file line number of each block.
The blocks are copied from the Markdown and pasted into the
generated testfile. This is called rendering in the documentation.
The generated test file is imported and then run by calling unittest.main().

- Example: [project.md](../tests/md/project.md) |
  [Generated testfile](generated_project_py.md)
- Example: [share_demo.md](../docs/share/share_demo.md) |
  [Generated testfile](generated_share_demo_py.md)

Code blocks within a Markdown file render to member function `def tests()`
in a unittest.TestCase derived class.
There is one test class for each Markdown file.
In the example see `class Test001(unittest.TestCase):`. A Python example
in Markdown can spread across several fenced code blocks.

- The blocks are not isolated.
- Names assigned at the top level of a block are visible to other blocks.

## --generate

The --generate option outputs the generated testfile to stdout or the named
file. Keep in mind the testfile is a snapshot in time of the Markdown blocks.
This file may be run later with unittest **or run with pytest**. Run with pytest
is ok provided a --fixture does not call **addModuleCleanup()**.
Working with generated testfile separately is an effective way to
troubleshoot test failures and to understand the execution context.

## Fixture globs

A --fixture function generates a **setUpModule()** in the test file
that calls the fixture function.

The fixture function can inject global variables into the top level
of the testfile module by returning a dict. See [fixture.py](fixture_py.md).
The keys become global variable names in the gernerated module.
This is done at runtime by an instance of phmutest.globs.Globals.
It calls Python built in function setattr(moduleobject, key, value).

Please keep in mind that the module globals are shallow copies or
references to the objects created in the fixture function. The Markdown
Python examples are free to mutate the objects.
Examples should avoid assignments to the fixture glob names. To see what
happens see tests/test_rebind.py.

## --sharing

The --sharing option turns on verbose printing showing the names of globals
added to the module. `.` means show sharing for all files.
The features below add globals to the module:

- fixture globs
- share across files
- setup directives with or without setup-across-files

Since fixture globs are not associated with a Markdown file, use --sharing
for any FILE or `.` to turn them on. The FILE must exist, but
need not be specified by --share-across-files or --setup-across-files.
Look for messages that start with `sharing-mod adding=`.
The file tests/test_rebind.py has a capture of phmutest output
in its docstring.

These imports will not be shown by --sharing because they are already
imported at the top of the testfile.

- import contextlib
- import io
- import sys
- import unittest

## Share across files

Share across files generates code at the bottom of the **def tests()**
that copies to module globals the names assigned by the entire
**tests()** function.
The names become visible as global variables for the rest of
the unittest run.
Refer to the implementation in src/phmutest/globs.py class Globals.

## Setup and teardown
Setup and teardown applies to examples in a single Markdown file.

- Blocks with the phmutest-setup directive render into **setUpClass(cls)**
- Blocks with the phmutest-teardown directive render into **tearDownClass(cls)**

Code is generated at the bottom of **setUpClass(cls)**
to copy the names assigned by the entire function to module level globals.
Code is generated at the bottom of **tearDownClass(cls)**
to **clear** the setUpClass shared names from the module level globals.
The names are only present while the test class for that file is running.
The lines printed by --sharing for setup and teardown
directives start with `sharing-class`.
See test_share_across_with_setup_sharing() in tests/test_sharing.py.

## Setup across files

Setup and teardown blocks in a single Markdown file are applied to all FILEs
by --setup-across-files.

- Blocks with the phmutest-setup directive render into **setUpModule()**
- Blocks with the phmutest-teardown directive render into **tearDownModule()**

Code is generated at the bottom of **setUpModule()**
to copy the names assigned by the entire function to module level globals.

## --progress

This option turns on per block verbose printing. The printing is directed
to the standard error stream shared with unittest's verbose printing.


[1]: https://docs.python.org/3/library/unittest.html

