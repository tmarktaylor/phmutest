# Show pytest invokes added cleanups at teardown time

For --fixture in code mode extra code is added to the
generated testfile at module setup and teardown time
to explicitly invoke unittest.doModuleCleanups().

This code is redundant when running the testfile with unittest
since the unittest framework does the call.

When running a generated testfile with pytest 6.2.5 and 7 and
maybe later unittest.doModuleCleanups() does not get called.

Show that unittest cleanup functions added by addModuleCleanup() get called
when running with pytest.

Run the command below and look for the print message in the pytest output.

```txt
phmutest tests/md/cleanups.md --fixture docs.fix.code.chdir.change_dir --log --generate t.txt
pytest -vv t.txt
```

```python
import unittest
```

```python
print("This FCB passes")
```

```python
# This is a little bit of a cheat since we are adding the cleanup
# after setUpModule() is run in the generated testfile.
unittest.addModuleCleanup(print, "Module Cleanup at module teardown time")
assert False, "fail this FCB."
```

```python
print("This FCB also passes.")
```

```python
assert False, "fail another FCB."
```

```python
print("A final passing FCB.")
```
