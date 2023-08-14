# phmutest 0.0.1

## Detect broken Python examples in Markdown

- Command line program checks Python syntax highlighted examples.
- Equivalent Python library for calling from test suite. | [Here](#call-from-python)
- Python tools to get fenced code block contents from Markdown. | [Here](docs/api.md)

Treats each Markdown file as a single long example which continues
across multiple Markdown [fenced code blocks][3] (FCBs or blocks).

- Checks either Python code examples plus output **or** ">>>" REPL examples
  | [doctest][4].
- Reports pass/failed/error/skip status and line number for each block.
- An example can continue **across** files.
- Runs files in user specified order.
- TOML configuration available.

### Your Python setup and cleanup

Specify a Python function which is called first before checking examples.
Change context, acquire resources, create objects, register cleanup functions.
Pass objects as global variables to the examples.
Cleans up even when fail-fast.
| [Suite initialization and cleanup](#suite-initialization-and-cleanup)

### No Markdown edits required for above features

Tests Python examples as is, the same way they were written.

### Extendable

Designated and stable **patch points** for Python standard library
**unittest.mock.patch()** patches. | [Here](#patch-points)

### Advanced features

These features require adding tool specific HTML comment **directives**
to the Markdown. Because directives are HTML comments they are not visible in
rendered Markdown. View directives on [Latest README on GitHub][1]
by pressing the `Code` button in the banner at the top of the file.
| [Here](docs/advanced.md).

- Assign test group names to blocks. Command line options select or
  deselect test groups by name.
- Skip blocks or skip checking printed output.
- Label any fenced code block for later retrieval.
- Accepts [phmdoctest][17] directives except share-names and clear-names.
- Specify blocks as setup and teardown code for the file or setup across files.


## main branch status
[![](https://img.shields.io/pypi/l/phmutest.svg)](https://github.com/tmarktaylor/phmutest/blob/main/LICENSE)
[![](https://img.shields.io/pypi/v/phmutest.svg)](https://pypi.python.org/pypi/phmutest)
[![](https://img.shields.io/pypi/pyversions/phmutest.svg)](https://pypi.python.org/pypi/phmutest)
[![Code style: black](https://img.shields.io/badge/code%20style-black-000000.svg)](https://github.com/psf/black)

[![CI](https://github.com/tmarktaylor/phmutest/actions/workflows/ci.yml/badge.svg?branch=main)](https://github.com/tmarktaylor/phmutest/actions/workflows/ci.yml)
[![Build status](https://ci.appveyor.com/api/projects/status/nbu1xlraoii8x377?svg=true)](https://ci.appveyor.com/project/tmarktaylor/phmutest)
[![readthedocs](https://readthedocs.org/projects/phmutest/badge/?version=latest)](https://phmutest.readthedocs.io/en/latest/?badge=latest)
[![codecov](https://codecov.io/gh/tmarktaylor/phmutest/coverage.svg?branch=main)](https://codecov.io/gh/tmarktaylor/phmutest?branch=main)

[Docs RTD](https://phmutest.readthedocs.io/en/latest/) |
[Docs GitHub](https://github.com/tmarktaylor/phmutest/blob/main/README.md) |
[Repos](https://github.com/tmarktaylor/phmutest) |
[pytest][13] |
[Codecov](https://codecov.io/gh/tmarktaylor/phmutest?branch=main) |
[License](https://github.com/tmarktaylor/phmutest/blob/main/LICENSE)

[Installation](#installation) |
[Usage](#usage) |
[FILE](#file) |
[REPL mode](#repl-mode) |
[Suite initialization and cleanup](#suite-initialization-and-cleanup) |
[Extend an example across files](#extend-an-example-across-files) |
[Skip blocks from the command line](#skip-blocks-from-the-command-line) |
[--summary](#summary-option) |
[TOML configuration](#toml-configuration) |
[Run as a Python module](#run-as-a-python-module) |
[Call from Python](#call-from-python) |
[Patch points](#patch-points) |
[Related projects](#related-projects)

[Changes](docs/recent_changes.md) |
[Contributions](CONTRIBUTING.md)

## Core feature demo

### markdown
The are no phmutest directives in this file.
The example starts by creating the object m.
```python
from hashlib import sha256
m = sha256()
```

The example continues here.
```python
m.update(b"hello World")
print(m.hexdigest()[0:5])
```

Expected output here is checked. This fenced code block does not
have an info string.
```
db406
```

The example continues here. It will continue for the entire file. This is
the last Python fenced code block (FCB) in the file.
```python
m.update(b"more bytes")
print(m.hexdigest()[0:5])
```

Note the expected output is different.
```
4c6ea
```

### phmutest command line
```
phmutest README.md --log
```

### phmutest output

Here is output from the command line.
The output produced by Python standard library unittest module
is not shown here. This is printed after the unittest `OK` line.


```
log:
args.files: 'README.md'
args.log: 'True'

location|label  result
--------------  ------
README.md:92..  pass
README.md:98..  pass
README.md:111.  pass
--------------  ------
```

See [list of demos](docs/demos.md)
See [How it works](docs/howitworks.md)

## Installation

    python -m pip install phmutest

- No dependencies since Python 3.11. Depends on tomli before Python 3.11.
- Pure Python. No binaries.
- It is advisable to install in a virtual environment.

## Usage

`phmutest --help`

```
usage: phmutest [-h] [--version] [--skip [TEXT ...]] [--fixture DOTTED_PATH.FUNCTION]
                [--share-across-files [FILE ...]] [--setup-across-files [FILE ...]]
                [--select [GROUP ...] | --deselect [GROUP ...]]
                [--config TOMLFILE] [--replmode]
                [-g OUTFILE] [--progress]
                [--sharing [FILE ...]] [--log] [--summary]
                [--report]
                [FILE ...]

Detect broken Python examples in Markdown. Accepts relevant unittest options.

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
  -g OUTFILE, --generate OUTFILE
                        Write generated Python or docstring to output file or stdout.
  --progress            Print block by block test progress. File by file in --replmode.
  --sharing [FILE ...]  For these files print name sharing. . means all files.
  --log                 Print log items when done.
  --summary             Print test count and skipped tests.
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
implemented using [doctest][4].
The option --setup-across-files and the setup and teardown directives
have no effect in REPL mode.
--progress has file by file granularity.

## Suite initialization and cleanup

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
| include-globs      | FILE                | list of filename glob to select files
| exclude-globs      | FILE                | list of filename glob to deselect files
| share-across-files | --share-across-files  | list of path
| setup-across-files | --setup-across-files  | list of path
| fixture            | --fixture           | dotted path
| select             | --select            | list of group directive name
| deselect           | --deselect          | list of group directive name

Only one of select and deselect can have strings.

- globs are described by Python standard library **pathlib.Path.glob()**.
- Any FILEs on the command line extend the files selected by include-globs and
  exclude-globs.
- Command line options supercede the keys in the config file.
- See the example **tests/toml/project.toml**.

## Run as a Python module

To run phmutest as a Python module:

```bash
python -m phmutest README.md --log
```

## Call from Python

Call **phmutest.main.main()** with a list of strings for the usage arguments,
options, and option values like this:
`["/md/project.md", "--replmode"]`

- A `phmutest.summary.PhmResult` instance is returned.
- When calling from Python there is no shell wildcard expansion.
- The --fixture function can be in the same Python file.
- Call from pytest to get overall result as Junit XML | [Suggestion](docs/junit.md)

[Example](docs/callfrompython.md) | [Limitation](docs/callfrompython.md#limitation)


## Patch points

Feel free to **unittest.mock.patch()** at these places in the code and not worry about
breakage in future versions. Look for examples in tests/test_patching.py.


|       patched function       | purpose
| :--------------------------------:  | :----------:
| phmutest.direct.directive_finders() | Add directive aliases
| phmutest.fenced.python_matcher()    | Add detect Python from FCB info string
| phmutest.session.modify_docstring() | Inspect/modify REPL text before testing
| phmutest.reader.post()              | Inspect/modify DocNode detected in Markdown

List of patch points

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

[1]: https://github.com/tmarktaylor/phmutest/blob/master/README.md?plain=1
[3]: https://github.github.com/gfm/#fenced-code-blocks
[11]: https://github.github.com/gfm/#info-string
[10]: https://phmutest.readthedocs.io/en/latest/docs/api.html
[4]: https://docs.python.org/3/library/doctest.html
[6]: https://pypi.python.org/project/coverage
[13]: https://ci.appveyor.com/project/tmarktaylor/phmutest
[15]: https://docs.pytest.org/en/stable
[16]: https://tmarktaylor.github.io/pytest-phmdoctest
[17]: https://pypi.python.org/pypi/phmutest


