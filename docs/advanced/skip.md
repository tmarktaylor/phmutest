# skip directive

The skip directive identifies Python FCBs to exclude from testing.
They will be noted in --log with result "skip" and reason "phmutest-skip".
This example does not have a skip directive.

```python
print("Hello World!")
```

```expected-output
Hello World!
```

This example has `<!--phmutest-skip-->` before the FCB.

<!--phmutest-skip-->

```python
print("Hello World!")

```

```expected-output
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

```expected-output
Bad expected output.
```

## phmutest command line

```shell
phmutest docs/advanced/skip.md --log
```

## phmutest output

```txt
log:
args.files: 'docs/advanced/skip.md'
args.log: 'True'

location|label             result  reason
-------------------------  ------  -------------
docs/advanced/skip.md:7 o  pass
docs/advanced/skip.md:19.  skip    phmutest-skip
docs/advanced/skip.md:33.  pass
-------------------------  ------  -------------
```
