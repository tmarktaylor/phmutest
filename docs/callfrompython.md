# Call from Python

## Api

<!--phmutest-skip-->
<!--phmutest-label api-main-->

```python
def main(argv: Optional[List[str]] = None) -> Optional[phmutest.summary.PhmResult]:
    """Library function that accepts command line args as a list of strings.

    Args:
        argv
            The command line args as a list of strings.

    Returns:
        phmutest.summary.PhmResult
    """
```

phmutest.main.main() returns a value of type PhmResult.

<!--phmutest-skip-->
<!--phmutest-label api-command-->

```python
def command(line: str) -> Optional[phmutest.summary.PhmResult]:
    """Library function that accepts command line args as a single string.

    Args:
        line
            The command line args as a single string.

    Returns:
        phmutest.summary.PhmResult
    """
```

phmutest.main.command() returns a value of type PhmResult.

## PhmResult

<!--phmutest-skip-->
<!--phmutest-label phmresult-->

```python
@dataclass
class PhmResult:
    """phmutest.main.command() return type.  Markdown Python example test results."""

    test_program: Optional[unittest.TestProgram]
    is_success: Optional[bool]
    metrics: Metrics
    log: List[List[str]]
```

## Example

```python
import phmutest.main
```

<!--phmutest-label call-from-python-->
```python
line = "tests/md/project.md --replmode"
phmresult = phmutest.main.command(line)
```

```python
assert phmresult.is_success
assert phmresult.metrics.number_blocks_run == 3
assert phmresult.metrics.passed == 3
assert phmresult.metrics.number_of_files == 1
```

## Another way to call from Python

This example shows how to call from Python
with the arguments as a list of strings.
phmutest.main.main() returns a value of type PhmResult as well.

```python
args = ["tests/md/project.md", "--replmode"]
phmresult = phmutest.main.main(args)
assert phmresult.is_success
assert phmresult.metrics.number_blocks_run == 3
assert phmresult.metrics.passed == 3
assert phmresult.metrics.number_of_files == 1
```

## limitation

The limitation described here applies to call from Python when
testing Python code plus expected output FCBs.
It does not apply when testing Python interactive session FCBs
with --replmode.

When phmutest is imported and called from a user Python script
each call creates and imports a new module.
The import consumes Python interpreter resources that are not released until the
interpreter exits. The resources include:

- sys.path
- imported modules

This makes call from Python unsuitable for looping tests or
long running or server processes.
On the development machine over 200 calls caused a noticeable slowdown.
The test suite has around 72 phmutest.main.main() calls.
On the Linux development machine it runs in 1-3 seconds.
Please also keep in mind that imports by phmutest and user's
Markdown Python examples are cached and top level module code
only runs once per Python interpreter invocation.

## phmutest tests this example

The example was split into several FCBs so that the labeled FCBs were
exact copies of snippets of Python source code in other Python
source files.

Tests checking this example:

- tests/test_subprocess.py:test_callfrompython()
- tests/test_docs.py:test_main_call_api()
- tests/test_docs.py:test_command_call_api()
- tests/test_docs.py:test_call_from_python()
- tests/test_docs.py:test_phmresult()
