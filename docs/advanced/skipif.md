# skipif directive

N is a Python minor version number.

The skipif directive identifies Python FCBs to exclude from testing.
They will be noted in --log with result "skip" and
skip reason "requires Python >= 3.N".

This test case will only run when Python is version 3.999 or higher.

<!--phmutest-skipif<3.999-->
```python
import sys
b = 10
print(b)
assert sys.version_info >= (3, 999)
```
```
10
```

## phmutest command line

```
phmutest docs/advanced/skipif.md --log
```

## phmutest expected output

```
log:
args.files: 'docs/advanced/skipif.md'
args.log: 'True'

location|label              result  skip reason
--------------------------  ------  ------------------------
docs/advanced/skipif.md:12  skip    requires Python >= 3.999
--------------------------  ------  ------------------------
```

