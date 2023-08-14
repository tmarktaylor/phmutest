# File with label directives. Some labels are on more than one block.


## A block and its fences indented 4 spaces.  Phmutest does not see it.
    ```python
    assert False
    ```

## First of 2 blocks with the same label
<!--phmutest-label one-label-many-blocks-->
```
first of many
```


```python
assert False
```
Note- the 2 blank lines above the above FCB prevent the
phmutest-skip directive from associating with the FCB.

## there is some text between the comment and the fenced code block.
<!--phmutest-skip-->
some text prevents directive from associating with the FCB
<!--phmutest-label one-label-many-blocks-->
```python
assert False
```

## skip directive on output block
```python
b = 10
print(b.as_integer_ratio())
```
<!--phmutest-label my-label-->
```
(10, 1)
```

## Third of 2 blocks with the same label
<!--phmutest-label one-label-many-blocks-->
```
third of many
```
<!-- HTML comment-->
<!--phmutest-label FIRST-->
<!--phmutest-label SECOND-->
```bash
ls -l
```

<!--phmutest-label SECOND-->
<!--phmutest-label THIRD-->
```bash
ls -r
```

