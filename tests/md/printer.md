# Test input file for printer.py:_print().

## Python FCB that has no output block.

The block prints to both stdout and stderr and then raises an AssertionError.
```python
import sys
print("asserting False...")
print("asserting False...", file=sys.stderr)
assert False, "fail here to show captured stdout and stderr."
```

## Output blocks can only check stdout.

This block passes.

```python
print("printing to stdout")
print("printing to stderr", file=sys.stderr)
```

```
printing to stdout
```

## Should capture stdout here since there is a skip directive on the output block.

This block fails too.

```python
b = 10
print(b.as_integer_ratio())
assert False, "fail here to show captured stdout and stderr."
```
<!--phmutest-skip-->
<!--phmutest-label skipped-output-block-->
```
(10, 1)
```

<!--phmutest-skip-->
```python
h = "hello"
w = "world"
print(h, w)
```

```
hello world
```

