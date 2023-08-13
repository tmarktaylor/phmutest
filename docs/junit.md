# A way to get as JUnit XML the phmutest result.

The generated testfile is run with unittest which prints
the exception traces to stderr.  phmutest prints to stdout.
When testing session blocks with --replmode all output prints to stdout.
The captured stdout and stderr are combined in the assertion message.

For Python code plus expected output blocks the exception trace will show the
line number in the generated Python testfile (_phm1.py) which is a temporary file.
To find the offending Markdown FCB look at the
--log output. It will show the file and line number of the Markdown
FCB with an "error" status.

- This example was developed using pytest 6.2.5 on Linux. Newer pytest
  may handle capturing stdout and stderr differently.

```python
import contextlib
import io
import sys

import phmutest.main

# Run this test case with pytest using a command like this...
# python -m pytest <this-file> --junit-xml=my_junit.xml -o junit_family=xunit2

def test_broken_python_examples(capsys):
    """Capture unittest's stderr and other info from any bad examples to junit XML."""
    with contextlib.redirect_stderr(io.StringIO()) as f:
        command = "tests/md/badsetup.md --log"
        args = command.split()
        phmresult = phmutest.main.main(args)
        assert phmresult.is_success, capsys.readouterr().out + "\n" + f.getvalue()
```

