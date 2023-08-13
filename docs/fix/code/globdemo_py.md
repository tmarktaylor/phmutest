# docs/fix/code/globdemo.py
```python
"""User fixture to return mapping of values."""
from phmutest.fixture import Fixture


def my_function(x):
    return x + 1


def init_globals(**kwargs):
    """Initialize objects and return mapping of the object name, value.

    Logging is optional. The log is passed as the log keyword argument.
    To log, append a list of 3 strings to the "log". The middle string is used
    to calculate metrics in the phmutest return result.
    Avoid passing the keys used with the mapping counts in
    phmutest.summary.compute_metrics().
    """
    import math

    log = kwargs["log"]
    log.append(["init_globals", "", ""])
    myglobs_list = [1, 2, 3, 4, "A"]
    globs = dict(math=math, myglobs_list=myglobs_list, my_function=my_function)
    return Fixture(globs=globs)
```
