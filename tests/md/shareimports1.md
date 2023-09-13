# Share unittest import at the top level of the generated testfile

## Note contextlib, io, and sys are only imported by FCBs under test

```python
import contextlib
import io
import sys
import unittest
```

```python
with contextlib.redirect_stdout(io.StringIO()) as fout:
    print("Hello World!")
    assert fout.getvalue() == "Hello World!\n"
```
