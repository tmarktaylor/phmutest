```python
with contextlib.redirect_stdout(io.StringIO()) as fout:
    print("Greetings Planet!")
    assert fout.getvalue() == "Greetings Planet!\n"
```


```python
import unittest.mock
```

