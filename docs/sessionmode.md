# Session mode

Session blocks are copied into a temporary docstring and run
with Python standard library [doctest][1].
There is one docstring for each Markdown file.

## --generate

The --generate option outputs the generated docstring to stdout or the named
file.

## Fixture globs

The fixture function can return global variables that are used
when running doctest.
The fixture function returns a dict.
The items become globs as described by [doctest][1].
Examples should avoid assignments to the fixture glob names. To see what
happens see tests/test_rebind.py.

Please keep in mind that the globs are shallow copies or
references to the objects created in the fixture function. The Markdown
Python examples are free to mutate the objects.

[REPL mode fixture example](fix/repl/drink_py.md).

## Share across files

Names assigned by --share-across-files FILEs are copied to a
mapping called globs described by [doctest][1].
The globs mapping is the same one used by fixture globs.
A file to be shared across files modifies the first and last lines of
the generated docstring.
An instance AssignmentExtractor from src/phmutest/globs.py discovers
the names assigned by the docstring.

- The globs mapping is empty or intialized by a fixture that returns globs.
- The globs mapping is updated after running a share-across-files FILE.
- One globs mapping is used for the entire phmutest run.

## --sharing

The --sharing option turns on verbose printing showing the names
shared by --share-across-files. Printing occurs after running
the docstring generated for the Markdown file.
Add the FILE or `.` to the --sharing option to turn on verbose printing.
`.` means show sharing for all files and will show fixture globs too.


## --progress

This option turns on per Markdown file verbose printing. The printing is directed
to the standard output stream shared with doctest's verbose printing.


[1]: https://docs.python.org/3/library/doctest.html

