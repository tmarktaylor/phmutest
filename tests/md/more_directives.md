# Test input file for direct.py for phmutest directives.

## directive and FCB indented 3 spaces.
   <!-- OK if there is more than one HTML comment here -->
   <!--phmutest-skip-->
   <!-- OK if there is a HTML comment here -->
   ```python
   assert False
   ```

## directive indented 4 spaces (one too many) and FCB indented 3 spaces.
    <!--phmutest-skip-->
   ```python
   assert False
   ```

## directive is not allowed below the FCB.
```python
assert False
```
<!--phmutest-skip-->


```python
assert False
```
Note- the 2 blank lines above the above FCB prevent the
phmutest-skip directive from associating with the FCB.

## there is some text between the comment and the fenced code block.
<!--phmutest-skip-->
some text prevents directive from associating with the FCB
```python
assert False
```

## skip directive on output block
```python
b = 10
print(b.as_integer_ratio())
```
<!--phmutest-skip-->
<!--phmutest-label my-label-->
```
(10, 1)
```

## skip directive with extra spacing
<!--phmutest-label   EXTRA_SPACES  -->
```python
assert False
```

