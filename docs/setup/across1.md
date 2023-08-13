# --setup-across-files example

This example shows the use of the `<!--phmutest-setup-->` and
`<!--phmutest-teardown-->` directives.


**All** the names assigned in the setup blocks are made visible to the examples
in all files.

- [docs/setup/across1.md](across1.md) (This file)
- [docs/setup/across2.md](across2.md)


## The next 2 blocks are marked as the setup blocks.
The main reason to use setup blocks is so that the teardown blocks
will run in the event a post setup block fails.
Note that teardown will only run if all the setup blocks succeed.

The example employs ExitStack to combine the cleanup of the temporary
directory and restore the changed working directory.
The function create_tmpdir() serves to hide the names 'stack' and 'td' from sharing.

<!--phmutest-setup-->
```python
import os
import tempfile
from contextlib import ExitStack
from pathlib import Path

FILENAME = "floaters.txt"
CONTENTS = "apples, cider, cherries, very small rocks."
original_cwd = Path.cwd()
```

Each setup block must have the `<!--phmutest-setup-->` directive.
<!--phmutest-setup-->
```python
def create_tmpdir():
    with ExitStack() as stack:
        # callbacks are done in reverse order
        td = stack.enter_context(tempfile.TemporaryDirectory())
        stack.callback(os.chdir, Path.cwd())  # restore
        os.chdir(td)
        return stack.pop_all().close

cleanup_tmpdir = create_tmpdir()
Path(FILENAME).write_text(CONTENTS, encoding="utf-8")
```

## The next 2 blocks are marked as the teardown blocks.
Setup and teardown blocks can have an output block.
<!--phmutest-teardown-->
```python
print("Removing tmpdir, restoring current working directory...")
cleanup_tmpdir()
```

expected output:
```
Removing tmpdir, restoring current working directory...
```

## This block will be marked as the teardown code too.
More than one setup or teardown block is allowed.  Each
block must have the `<!--phmutest-teardown-->` directive.
The block shows that cleanup_tmpdir() restored the initial cwd.
<!--phmutest-teardown-->
```python
assert Path.cwd() == original_cwd
```

## phmutest command line.

Note that this fenced code block has `txt` as the info string.
The txt tells phmutest that this is not an output block
for the python block immediately above.
```txt
phmutest docs/setup/across1.md docs/setup/across2.md --setup-across-files docs/setup/across1.md --log
```

## phmutest output.

Terminal output after the `OK` line.
```
log:
args.files: 'docs/setup/across1.md'
args.files: 'docs/setup/across2.md'
args.setup_across_files: 'docs/setup/across1.md'
args.log: 'True'

location|label                     result
---------------------------------  ------
setUpModule......................
docs/setup/across1.md:24 setup...  pass
docs/setup/across1.md:37 setup...  pass
docs/setup/across2.md:4..........  pass
docs/setup/across2.md:12.........  pass
tearDownModule...................
docs/setup/across1.md:53 teardown  pass
docs/setup/across1.md:68 teardown  pass
---------------------------------  ------
```
[1]: https://github.com/tmarktaylor/phmutest/docs/setup
