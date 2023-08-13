# Fixture example: change working directory

Use the --fixture command line option to change the working directory.

The command line below calls the fixture function **change_dir()**
from [chdir.py](chdir_py.md)
in the **setUpModule()** of the generated unittest test file.

The function is specified as the value for the --fixture command line
option. See the command line below. Instead of slashes in the value
note that dots separate the folders and the function.

The function **change_dir()** changes the
working directory to `docs/fix/code`.  This allows the example to use a
pathname relative to `docs/init/fix/code` for the file.

**change_dir()** also calls **unittest.addModuleCleanup()** to have unittest
restore the working directory when unittest terminates.


## Python fenced code block and expected output under test.

This is the Python example we want to check.

```python
from pathlib import Path
```

```python
# Note-
# The file's location is "docs/fix/code/textfile.txt".
# The --fixture function changed the working directory to "docs/fix/code".
# We open it using just "textfile.txt".
contents = Path("textfile.txt").read_text(encoding="utf-8")
print(contents, end="")
```

Expected output:
```
Demonstrate changed working directory.
```

## phmutest command line.

```
phmutest docs/fix/code/chdir.md --fixture docs.fix.code.chdir.change_dir --log
```

## phmutest output.

Terminal output after the `OK` line.
```
log:
args.files: 'docs/fix/code/chdir.md'
args.fixture: 'docs.fix.code.chdir.change_dir'
args.log: 'True'

location|label             result
-------------------------  ------
setUpModule..............
change cwd...............
docs/fix/code/chdir.md:25  pass
docs/fix/code/chdir.md:29  pass
tearDownModule...........
restore cwd..............
-------------------------  ------
```

