# Call from Python example

```python
import phmutest.main
```

<!--phmutest-label call-from-python-->
```python
command = "tests/md/project.md --replmode"
args = command.split()
phmresult = phmutest.main.main(args)
```

```python
assert phmresult.is_success
assert phmresult.metrics.number_blocks_run == 3
assert phmresult.metrics.passed == 3
assert phmresult.metrics.number_of_files == 1
```

## PhmResult
phmutest.main.main() returns a value of type PhmResult
defined in src/phmutest/summary.py.

<!--phmutest-skip-->
<!--phmutest-label phmresult-->
```python
@dataclass
class PhmResult:
    """phmutest.main.main() return type.  Markdown Python example test results."""

    test_program: Optional[unittest.TestProgram]
    is_success: bool
    metrics: Metrics
    log: List[List[str]]
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
- tests/test_docs.py:test_call_from_python()
- tests/test_docs.py:test_phmresult()


