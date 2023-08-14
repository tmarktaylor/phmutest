# Share same imports as the top level of the generated testfile.


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


