# phmutest 1.0.1

## Detect and troubleshoot broken Python examples in Markdown

- Hybrid Python library / console program checks Python syntax highlighted examples.
- Python tools to get fenced code block contents from Markdown. | [Here](docs/api.md)

Treats each Markdown file as a single long example, which continues
across multiple Markdown [fenced code blocks][3] (FCBs or blocks).

[Skip example and jump down to Features](#features)

## A broken Example

When FCBs break we show what caused the error to help you quickly find the root cause.
Let's start with FCBs that show how to use the library answerlib.
| [answerlib.py](docs/answerlib_py.md).  The ask method returns the answer
to the question. | [phmutest output](#phmutest-console-output)

```python
from docs.answerlib import RightAnswer, WrongAnswer, RaiserBot
```

Create a RightAnswer instance and ask a question.
phmutest
assigns a pass/failed/error/skip status to each Python FCB.
This FCB and the FCB above are given 'pass' status.
Note how the example continues across multiple FCBs.
It continues for the entire Markdown file.

```python
pass_bot = RightAnswer()
pass_bot.ask(question="What floats?")
```

Now we are going to cause the answerlib to raise an
exception by calling the method inquire() which does not exist.
This raises an AttributeError in the library which propagates
up and out of the first line of the FCB below.
This FCB is given 'error' status.

```python
pass_bot.inquire(query="What floats?")
```

The test runner keeps going even after an exception. To stop
on first failure use the "-f" option.
Cause another exception within answerlib to see the FCB line
where the exception propagates out of the FCB in the log.
This FCB is also given 'error' status. See the results in the
log below.

```python
raiser_bot = RaiserBot()
_ = raiser_bot.ask(question="What floats?")
```

Add an FCB that immediately follows a Python code block that has no info string
or the info string `expected-output`. Captured stdout is compared to the block.
In the log a "o" after the filename indicates expected output was checked.

```python
print("Incorrect expected output.")
```

```expected-output
Hello World!
```

To test a value add an assert statement to the FCB. This FCB fails.

```python
fail_bot = WrongAnswer()
answer = fail_bot.ask(question="What floats?")
assert answer == "apples", f"got= {repr(answer)}"
```

### phmutest command line

```shell
phmutest README.md --log --quiet
```

### phmutest console output

There are two parts:

- unittest printing to sys.stderr
- phmutest printing to sys.stdout

#### phmutest stdout

This shows the --log output.
Below the log table are the broken FCB Markdown source file lines.

- The location is the file and line number of the opening fence of the FCB.
- The ">" indicates the line that raised the exception.

```txt
log:
args.files: 'README.md'
args.log: 'True'

location|label  result  reason
--------------  ------  ---------------------------------------------------------------
README.md:20..  pass
README.md:31..  pass
README.md:42..  error   AttributeError: 'RightAnswer' object has no attribute 'inquire'
README.md:53..  error   ValueError: What was the question?
README.md:62 o  failed
README.md:72..  failed  AssertionError: got= 'very small rocks'
--------------  ------  ---------------------------------------------------------------

README.md:42
>   43  pass_bot.inquire(query="What floats?")
        AttributeError: 'RightAnswer' object has no attribute 'inquire'

README.md:53
    54  raiser_bot = RaiserBot()
>   55  _ = raiser_bot.ask(question="What floats?")
        ValueError: What was the question?

README.md:62
    63  print("Incorrect expected output.")
AssertionError: 'Hello World!\n' != 'Incorrect expected output.\n'
- Hello World!
+ Incorrect expected output.

README.md:72
    73  fail_bot = WrongAnswer()
    74  answer = fail_bot.ask(question="What floats?")
>   75  assert answer == "apples", f"got= {repr(answer)}"
        AssertionError: got= 'very small rocks'
```

On GitHub, to see Markdown line numbers, view this file and choose
Code button. (Code is between Preview and Blame).

##### traceback

When phmutest is installed with the `[traceback]` extra,
a [stackprinter][21] formatted
traceback prints after each broken FCB. [Here](docs/traceback.md)
is an example traceback.

#### unittest stderr

Here is the unittest output printed to sys.stderr.
It starts with captured stdout/stderr from the 'error' FCBs.
Markdown Python FCBs are copied to a temporary 'testfile' that is
run by the unittest test runner. The test runner prints to stderr before
the phmutest stdout printing. The test runner output provides tracebacks
for the assertions and exceptions.
The testfile line numbers will mostly be different than the Markdown
line numbers. Look for the Markdown line numbers in the log. (Python 3.11)

```txt
=== README.md:53 stdout ===
This is RaiserBot.ask() on stdout answering 'What floats?'.
=== end ===
=== README.md:53 stderr ===
This is RaiserBot.ask() on stderr: Uh oh!
=== end ===
======================================================================
ERROR: tests (_phm1.Test001.tests) [README.md:42]
----------------------------------------------------------------------
Traceback (most recent call last):
  File "C:\Users\XXX\AppData\Local\Temp\YYY\_phm1.py", line 34, in tests
    pass_bot.inquire(query="What floats?")
    ^^^^^^^^^^^^^^^^
AttributeError: 'RightAnswer' object has no attribute 'inquire'

======================================================================
ERROR: tests (_phm1.Test001.tests) [README.md:53]
----------------------------------------------------------------------
Traceback (most recent call last):
  File "C:\Users\XXX\AppData\Local\Temp\YYY\_phm1.py", line 40, in tests
    _ = raiser_bot.ask(question="What floats?")
        ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
  File "C:\Users\XXX\Documents\u0\docs\answerlib.py", line 32, in ask
    raise ValueError("What was the question?")
ValueError: What was the question?

======================================================================
FAIL: tests (_phm1.Test001.tests) [README.md:62]
----------------------------------------------------------------------
Traceback (most recent call last):
  File "C:\Users\XXX\AppData\Local\Temp\YYY\_phm1.py", line 51, in tests
    _phm_testcase.assertEqual(_phm_expected_str, _phm_printer.stdout())
AssertionError: 'Hello World!\n' != 'Incorrect expected output.\n'
- Hello World!
+ Incorrect expected output.


======================================================================
FAIL: tests (_phm1.Test001.tests) [README.md:72]
----------------------------------------------------------------------
Traceback (most recent call last):
  File "C:\Users\XXX\AppData\Local\Temp\YYY\_phm1.py", line 58, in tests
    assert answer == "apples", f"got= {repr(answer)}"
           ^^^^^^^^^^^^^^^^^^
AssertionError: got= 'very small rocks'

----------------------------------------------------------------------
Ran 1 test in 0.027s

FAILED (failures=2, errors=2)
```

## Features

- Checks either Python code examples **or** ">>>" REPL examples
  | [doctest][5].
- Reports pass/failed/error/skip status and Markdown file line number for each block.
- Shows block source indicating the line where the exception propagated.
- Support for setup and cleanup. Acquire and release resources, change context,
  Pass objects as global variables to the examples. Cleans up even when fail-fast.
  [Suite initialization and cleanup](#suite-initialization-and-cleanup)
- Call from Python, call from pytest.
- Write a pytest testfile into an existing pytest or unittest test suite.
- Runs files in user specified order.
- TOML configuration available.
- An example can continue **across** files.
- Show stdout printed by examples. --stdout
- Colors pass/failed/error/skip status. --color
- Syntax highlights broken FCBs in the log. --style
- Check expected output of code examples. Markdown edits are required.
- Designated and stable **patch points** for Python standard library
  **unittest.mock.patch()** patches. | [Here](#patch-points)

## Advanced features

These features require adding tool specific HTML comment **directives**
to the Markdown. Because directives are HTML comments they are not visible in
rendered Markdown. View directives on GitHub
by pressing the `Code` button in the banner at the top of the file.
| [Advanced feature details](docs/advanced.md).

- Assign test group names to blocks. Command line options select or
  deselect test groups by name.
- Skip blocks or skip checking printed output.
- Label any fenced code block for later retrieval.
- Accepts [phmdoctest][17] directives except share-names and clear-names.
- Specify blocks as setup and teardown code for the file or setup across files.

## main branch status

[![license](https://img.shields.io/pypi/l/phmutest.svg)](https://github.com/tmarktaylor/phmutest/blob/main/LICENSE)
[![pypi](https://img.shields.io/pypi/v/phmutest.svg)](https://pypi.python.org/pypi/phmutest)
[![python](https://img.shields.io/pypi/pyversions/phmutest.svg)](https://pypi.python.org/pypi/phmutest)

[![CI](https://github.com/tmarktaylor/phmutest/actions/workflows/ci.yml/badge.svg?branch=main)](https://github.com/tmarktaylor/phmutest/actions/workflows/ci.yml)
[![Build status](https://ci.appveyor.com/api/projects/status/nbu1xlraoii8x377?svg=true)](https://ci.appveyor.com/project/tmarktaylor/phmutest)
[![readthedocs](https://readthedocs.org/projects/phmutest/badge/?version=latest)](https://phmutest.readthedocs.io/en/latest/?badge=latest)
[![codecov](https://codecov.io/gh/tmarktaylor/phmutest/coverage.svg?branch=main)](https://codecov.io/gh/tmarktaylor/phmutest?branch=main)

[Docs RTD](https://phmutest.readthedocs.io/en/latest/) |
[Docs auto-theme](https://tmarktaylor.github.io/phmutest) |
[Repos](https://github.com/tmarktaylor/phmutest) |
[pytest][13] |
[Codecov](https://codecov.io/gh/tmarktaylor/phmutest?branch=main) |
[License](https://github.com/tmarktaylor/phmutest/blob/main/LICENSE)

[Features](#features) |
[Advanced features](#advanced-features) |
[main branch status](#main-branch-status) |
[Installation](#installation) |
[Usage](#usage) |
[FILE](#file) |
[REPL mode](#repl-mode) |
[Suite initialization and cleanup](#suite-initialization-and-cleanup) |
[--color](#color-option) |
[--style](#style-option) |
[Extend an example across files](#extend-an-example-across-files) |
[Skip blocks from the command line](#skip-blocks-from-the-command-line) |
[--summary](#summary-option) |
[TOML configuration](#toml-configuration) |
[Run as a Python module](#run-as-a-python-module) |
[Call from Python](#call-from-python) |
[Call from pytest](#call-from-pytest) |
[Patch points](#patch-points) |
[Hints](#hints) |
[Related projects](#related-projects) |
[Differences between phmutest and phmdoctest](#differences-between-phmutest-and-phmdoctest)

[Sections](docs/demos.md#sections) |
[Demos](docs/demos.md#demos) |
[Changelog](CHANGELOG.md) |
[Contributions](CONTRIBUTING.md)

See [list of demos](docs/demos.md)
See [How it works](docs/howitworks.md)

## Installation

```shell
python -m pip install phmutest
```

- No required dependencies since Python 3.11. Depends on tomli before Python 3.11.
- Pure Python.
- It is advisable to install in a virtual environment.

### install extras

The extra 'color' enables the --color and
--style options.

```shell
python -m pip install "phmutest[color]"  # Windows
python -m pip install 'phmutest[color]'  # Unix/macOS
```

The extra 'pytest' installs pytest and the plugin
pytest-subtests.
pytest-subtests continues running subtests after
the first subtest failure. [pytest][20] prints a very
helpful traceback when FCBs break.

```shell
python -m pip install "phmutest[pytest]"  # Windows
python -m pip install 'phmutest[pytest]'  # Unix/macOS
```

The extra 'traceback' enables [stackprinter][21] traceback
printing for each broken FCB. The traceback is
slightly different than pytest's.

```shell
python -m pip install "phmutest[traceback]"  # Windows
python -m pip install 'phmutest[traceback]'  # Unix/macOS
```

Install with the extra 'dev' to install locally the same tools used by
the continuous integration scripts.

```shell
python -m pip install "phmutest[dev]"  # Windows
python -m pip install 'phmutest[dev]'  # Unix/macOS
```

Install with all the extras.

```shell
python -m pip install "phmutest[color, traceback, dev]"  # Windows
python -m pip install 'phmutest[color, traceback, dev]'  # Unix/macOS
```

## Usage

`phmutest --help`

```txt
usage: phmutest [-h] [--version] [--skip [TEXT ...]] [--fixture DOTTED_PATH.FUNCTION]
                [--share-across-files [FILE ...]]
                [--setup-across-files [FILE ...]] [--select [GROUP ...] | --deselect
                [GROUP ...]] [--config TOMLFILE] [--replmode] [--color]
                [--style STYLE] [-g OUTFILE]
                [--progress] [--sharing [FILE ...]] [--log] [--summary] [--stdout] [--report]
                [FILE ...]

Detect and troubleshoot broken Python examples in Markdown. Accepts relevant unittest options.

positional arguments:
  FILE                  Markdown input file.

options:
  -h, --help            show this help message and exit
  --version             show program's version number and exit
  --skip [TEXT ...]     Any block that contains the substring TEXT is not tested.
  --fixture DOTTED_PATH.FUNCTION
                        Function run before testing.
  --share-across-files [FILE ...]
                        Shares names from Markdown file to later positional files.
  --setup-across-files [FILE ...]
                        Apply Markdown file setup blocks to files.
  --select [GROUP ...]  Select all blocks with phmutest-group GROUP directive for testing.
  --deselect [GROUP ...]
                        Exclude all blocks with phmutest-group GROUP directive from testing.
  --config TOMLFILE     .toml configuration file.
  --replmode            Test Python interactive sessions.
  --color, -c           Enable --log pass/failed/error/skip result colors.
  --style STYLE         Specify a Pygments style name as STYLE to enable syntax highlighting.
  -g OUTFILE, --generate OUTFILE
                        Write generated Python or docstring to output file or stdout.
  --progress            Print block by block test progress. File by file in --replmode.
  --sharing [FILE ...]  For these files print name sharing. . means all files.
  --log                 Print log items when done.
  --summary             Print test count and skipped tests.
  --stdout              Print output printed by blocks.
  --report              Print fenced code block configuration, deselected blocks.
```

- The **-f** option indicates fail fast.

## FILE

The Markdown files are processed in the same order they are present as positional
arguments on the command line.
Shell wildcards can be used. Be aware that the shell expansion and operating system
will determine the order.

## REPL mode

When --replmode is specified Python interactive sessions are tested and
Python code and expected output blocks are not tested. REPL mode tests are
implemented using [doctest][5].
The option --setup-across-files and the setup and teardown directives
have no effect in REPL mode.
--progress has file by file granularity.
See the [Broken REPL example](docs/repl/REPLexample.md).

## Suite initialization and cleanup

For background refer to definitions at the top of [unittest][18].
Use --fixture to specify a Python initialization function that runs before the tests.
It works with or without --replmode, but there are differences.
In both modes, the fixture function may create objects (globs) that are visible
as globals to the FCBs under test.

In the event of test errors orderly cleanup/release of resources is assured.
For Python code blocks the fixture may register cleanup functions by
calling **unittest.addModuleCleanup()**.
In REPL mode the fixture function optionally returns a cleanup function.

- The fixture can acquire and release resources or change context.
- The fixture can make entries to the log displayed by --log.
- The fixture can install patches to the code under test.

Specify the --fixture function as
a relative **dotted path** where `/` is replaced with `.`.
For example, the function **my_init()** in the file **tests/myfixture.py**
would be specified:

--fixture **tests.myfixture.my_init**

The function is passed keyword only arguments and **optionally**
returns a Fixture instance.
The keyword arguments and return type are described by
[src/phmutest/fixture.py](docs/fixture_py.md).
The fixture file should be in the project directory tree. Fixture demos:

- [fixture change workdir](docs/fix/code/chdir.md)
- [fixture set globals](docs/fix/code/globdemo.md)
- [fixture cleanup REPL Mode](docs/fix/repl/drink.md)

The test case test_doctest_optionflags_patch() shows an
example with a fixture that applies a patch to
doctest optionflags in --replmode.

### Dotted path details

The fixture function must be at the top level of a .py file.

- The dotted_path has components separated by ".".
- The last component is the function name.
- The next to last component is the python file name without the .py suffix.
- The preceding components identify parent folders. Folders should be
  relative to the current working directory which is typically the
  project root.

## color option

The --color -c option colors the --log pass/failed/error/skip status.

## style option

The --style option enables the PYPI project [Pygments][19] syntax
highlighting style used in the --log output.
The style option requires the `[color]` installation extra.

```txt
--style <pygments-style-name>
```

## Extend an example across files

Names assigned by all the blocks in a file can be shared, as global variables,
to files specified later in the command line.
Add a markdown file path to the --share-across-files command line option.
The 'shared' file(s) must also be specified as a FILE positional command line argument.

- [share demo](docs/share/share_demo.md) |
  [how it works](docs/codemode.md#share-across-files)
- [--replmode share demo](docs/repl/replshare_demo.md) |
  [how it works](docs/sessionmode.md#share-across-files)

## Skip blocks from the command line

The skip `--skip TEXT` command line option
prevents testing of any Python code or REPL block that contains the substring TEXT.
The block is logged as skip with `--skip TEXT` as the reason.

## summary option

The example  [here](docs/share/share_demo.md) shows --summary output.

## TOML configuration

Command line options can be augmented with values from a `[tool.phmutest]` section in
a .toml configuration file. It can be in a new file or added to an existing
.toml file like pyproject.toml.
The configuration file is specified by the `--config FILE` command line option.

Zero or more of these TOML keys may be present in the `[tool.phmutest]` section.

| TOML key           | Usage option        | TOML value - double quoted strings
| :------------------| :-----------------: | :---------:
| include-globs      | positional arg FILE | list of filename glob to select files
| exclude-globs      | positional arg FILE | list of filename glob to deselect files
| share-across-files | --share-across-files  | list of path
| setup-across-files | --setup-across-files  | list of path
| fixture            | --fixture           | dotted path
| select             | --select            | list of group directive name
| deselect           | --deselect          | list of group directive name
| color              | --color             | Use unquoted true to set
| style              | --style             | set Pygments syntax highlighting style

Only one of select and deselect can have strings.

- globs are described by Python standard library **pathlib.Path.glob()**.
- Any FILEs on the command line extend the files selected by include-globs and
  exclude-globs.
- Command line options supersede the keys in the config file.
- See the example **tests/toml/project.toml**.

## Run as a Python module

To run phmutest as a Python module:

```bash
python -m phmutest README.md --log
```

## Call from Python

Call **phmutest.main.command()** with a string that looks like a
command line less the phmutest, like this:
`"tests/md/project.md --replmode"`

- A `phmutest.summary.PhmResult` instance is returned.
- When calling from Python there is no shell wildcard expansion.
- **phmutest.main.main()** takes a list of strings like this:
  `["tests/md/project.md", "--replmode"]` and returns `phmutest.summary.PhmResult`.

[Example](docs/callfrompython.md) | [Limitation](docs/callfrompython.md#limitation)

## Call from pytest

In some of the tests the --fixture function is in the same pytest file as the
phmutest library call.  This is not recommended because the Python file is
imported again by fixture_function_importer() to a new module object.
The Python file's module level code will
be run a second time. If there are side-effects they will be repeated, likely
with un-desirable and hard to troubleshoot behavior.

## Patch points

Feel free to **unittest.mock.patch()** at these places in the code and not worry about
breakage in future versions. Look for examples in tests/test_patching.py.

### List of patch points

|       patched function              | purpose
| :--------------------------------:  | :----------:
| phmutest.direct.directive_finders() | Add directive aliases
| phmutest.fenced.python_matcher()    | Add detect Python from FCB info string
| phmutest.select.OUTPUT_INFO_STRINGS | Change detect expected output FCB info string
| phmutest.session.modify_docstring() | Inspect/modify REPL text before testing
| phmutest.reader.post()              | Inspect/modify DocNode detected in Markdown

## Hints

- Since phmutest generates code, the input files should be from a trusted
  source.
- The phmutest Markdown parser finds fenced code blocks enclosed by
  html `<details>` and `</details>` tags.
  The tags may require a preceding and trailing blank line
  to render correctly. See example at the bottom tests/md/readerfcb.md.
- Markdown indented code blocks ([Spec][4] section 4.4) are ignored.
- A malformed HTML comment ending is bad. Make sure
  it ends with both dashes like `-->`.
- A misspelled directive will be missing from the --report output.
- If the generated testfile has a compile error phmutest might raise an
  ImportError when importing it.
- Blocks skipped with --skip and the phmutest-skip directive
  are not rendered. This is useful to avoid above import error.
- In repl mode **no** skipped blocks are rendered.
- "--quiet" is passed to the unittest test runner.
- The unittest "--locals" provides more information in traces.
- Try redirecting `--generate -` standard output into PYPI Pygments to
  colorize the generated test file.
- In code mode patches made by a fixture function are placed
  when the testfile is run.
- In code mode printing a class (not an instance) and then checking it in an
  expected-output FCB is not feasible because Python prints the
  `__qualname__`. See the file tests/md/qualname.md for an explanation.
- phmutest is implemented with non-thread-safe context managers.

## Related projects

- phmdoctest
- rundoc
- byexample
- sphinx.ext.doctest
- sybil
- doxec
- egtest
- pytest-phmdoctest
- pytest-codeblocks

## Differences between phmutest and phmdoctest

- phmutest treats each Markdown file as a single long example. phmdoctest
  tests each FCB in isolation. Adding a share-names directive is necessary to
  extend an example across FCBs within a file.
- Only phmutest can extend an example across files.
- phmutest uses Python standard library unittest and doctest as test runners.
  phmdoctest writes a pytest testfile for each Markdown file
  which requires a separate step to run. The testfiles then need to be discarded.
- phmdoctest offers two pytest fixtures that can be used in a pytest test case
  to generate and run a testfile in one step.
- phmutest generates tests for multiple Markdown files in one step
  and runs them internally so there are no leftover test files.
- The --fixture test suite initialization and cleanup is only available on phmutest.
  phmdoctest offers some initialization behavior using an FCB with a setup
  directive and its --setup-doctest option and it only works with sessions.
  See phmdoctest documentation "Execution Context"
  section for an explanation.
- phmutest does not support inline annotations.

[3]: https://github.github.com/gfm/#fenced-code-blocks
[4]: https://spec.commonmark.org
[5]: https://docs.python.org/3/library/doctest.html
[13]: https://ci.appveyor.com/project/tmarktaylor/phmutest
[17]: https://pypi.python.org/pypi/phmdoctest
[18]: https://docs.python.org/3/library/unittest.html
[19]: https://pypi.python.org/pypi/pygments
[20]: https://docs.pytest.org
[21]: https://github.com/cknd/stackprinter/blob/master/README.md
