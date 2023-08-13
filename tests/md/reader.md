# Test reader.py DocNodes FCBs.
two blanks here


## directive inside a multiline comment.
<!-- OK if there is more than one HTML comment here -->
<!--
phmutest-skip
-->
<!-- OK if there is a HTML comment here -->
```python
assert False
```

<!-- fenced code block with html comment
```python
assert False
```
-->
blank lines inside an FCB
```python

assert False

```
tilde start fence enclosing backtick
~~~python

```python

assert False

```

~~~
 <!-- indent 1 blank html comment -->
  <!-- indent 2 blanks html comment -->
   <!-- indent 3 blanks html comment -->
    this is not a NodeType.HTML_COMMENT
    <!-- indent 4 blanks html comment -->

