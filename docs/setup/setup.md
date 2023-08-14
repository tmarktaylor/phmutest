# Setup and teardown directive example.

Setup and teardown directives.
Directives are HTML comments
and are not rendered.
Look for the `<!--phmutest-setup-->` and `<!--phmutest-teardown-->` directives
in the Markdown file.

## The next 2 blocks are marked as the setup blocks.
The main reason to use setup blocks is so that the teardown blocks
will run in the event a post setup block fails.
Note that teardown will only run if all the setup blocks succeed.
We use ExitStack to create a single function call to cleanup the
temporary directory and change back to the original working directory.
We use with ExitStack to assure cleanup when a statement in the with
suite raises an exception.

<!--phmutest-setup-->
```python
import os
import tempfile
from contextlib import ExitStack
from pathlib import Path

FILENAME = "floaters.txt"
CONTENTS = "apples, cider, cherries, very small rocks."
workdir = Path.cwd()
```

Each setup block must have the `<!--phmutest-setup-->` directive.
<!--phmutest-setup-->
```python
# note callbacks are done in reverse order
with ExitStack() as stack:
    td = stack.enter_context(tempfile.TemporaryDirectory())
    stack.callback(os.chdir, workdir)  # restore
    os.chdir(td)
    cleanup = stack.pop_all().close

Path(FILENAME).write_text(CONTENTS, encoding="utf-8")
```

## This block shows the temporary file exists.
```python
print(Path(FILENAME).read_text(encoding="utf-8"))
assert Path.cwd() != workdir, "In a different cwd, presumably tempdir."
```
expected output:
```
apples, cider, cherries, very small rocks.
```

## The next 2 blocks are marked as the teardown blocks.
Setup and teardown blocks can have an output block as well.
<!--phmutest-teardown-->
```python
print("Restoring current working directory...")
cleanup()
```

expected output:
```
Restoring current working directory...
```

## This block will be designated as teardown code too.
More than one setup or teardown block is allowed.  Each
block must have the `<!--phmutest-teardown-->` directive.
The block shows that cleanup() restored the initial cwd.
<!--phmutest-teardown-->
```python
assert Path.cwd() == workdir, "The original cwd."
```

## phmutest command line.

Note that this fenced code block has `txt` as the info string.
The txt tells phmutest that this is not an output block
for the python block immediately above.
```txt
phmutest docs/setup/setup.md --log
```

## phmutest output.

Terminal output after the `OK` line.
```
log:
args.files: 'docs/setup/setup.md'
args.log: 'True'

location|label                   result
-------------------------------  ------
docs/setup/setup.md:19 setup...  pass
docs/setup/setup.md:32 setup...  pass
docs/setup/setup.md:44.........  pass
docs/setup/setup.md:56 teardown  pass
docs/setup/setup.md:71 teardown  pass
-------------------------------  ------
```
[1]: https://github.com/tmarktaylor/phmutest/docs/setup
