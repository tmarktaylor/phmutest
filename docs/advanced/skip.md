# skip directive

The skip directive identifies Python FCBs to exclude from testing.
They will be noted in --log with result "skip" and skip reason "phmutest-skip".
This example does not have a skip directive.

```python
print("Hello World!")
```
```
Hello World!
```

This example has `<!--phmutest-skip-->` before the FCB.


<!--phmutest-skip-->
```python
print("Hello World!")
```
```
Bad expected output.
```

The skip directive can also be placed on an expected output block.
There it prevents checking expected against actual output.
This example has `<!--phmutest-skip-->` above the expected output FCB.
It prevents the test from failing the expected output check.

```python
print("Hello World!")
```
<!--phmutest-skip-->
```
Bad expected output.
```

## phmutest command line
```
phmutest docs/advanced/skip.md --log
```

## phmutest output
```
log:
args.files: 'docs/advanced/skip.md'
args.log: 'True'

location|label            result  skip reason
------------------------  ------  -------------
docs/advanced/skip.md:7.  pass
docs/advanced/skip.md:18  skip    phmutest-skip
docs/advanced/skip.md:30  pass
------------------------  ------  -------------
```

