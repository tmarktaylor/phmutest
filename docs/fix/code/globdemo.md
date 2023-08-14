# Fixture example: set globals

Use the --fixture command line option to initialize globals for tests.

The command line at the bottom calls the function **init_globals()**
from [globdemo.py](globdemo_py.md)
in the **setUpModule()** of the generated unittest test file.

The function is specified as the value for the --fixture command line
option. See the command line below. Instead of slashes in the value
note that dots separate the folders and the function.

The function **init_globals()** assigns names and returns
a mapping of them to the caller. The generated testfile
copies them to the test module's module attributes.

## Python fenced code block and expected output under test.

This is the Python example we want to check.

```python
print(math.floor(10.7))
print(myglobs_list)
print(my_function(2))
```

Expected output:
```
10
[1, 2, 3, 4, 'A']
3
```
Note that Python prints the string value with single quotes.


## phmutest command line.

```
phmutest docs/fix/code/globdemo.md --fixture docs.fix.code.globdemo.init_globals --log
```

## phmutest output.

Terminal output after the `OK` line.
```
log:
args.files: 'docs/fix/code/globdemo.md'
args.fixture: 'docs.fix.code.globdemo.init_globals'
args.log: 'True'

location|label                result
----------------------------  ------
setUpModule.................
init_globals................
docs/fix/code/globdemo.md:21  pass
tearDownModule..............
----------------------------  ------
```

