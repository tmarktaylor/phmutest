# Test input file for direct.py for phmdoctest directives.

## skip directive
<!--phmdoctest-skip-->
<!-- OK if there is more than one HTML comment here -->
<!-- OK if there is a HTML comment here -->
```python
assert False
```

## skip directive on an expected output block.
Generates a test case that runs the code block but does
not check the expected output.
```python
from datetime import date

date.today()
```
<!-- OK if one blank line between FCB and HTML comments -->
<!--phmdoctest-skip-->

```
datetime.date(2021, 4, 18)
```

## skip directive on Python session.

No test case gets generated.
<!--phmdoctest-skip-->

```py
>>> print("Hello World!")
incorrect expected output should fail
if test case is generated
```

## mark.skip directive with label directive.
- Use `mark.skip` on Python code blocks.

<!--phmdoctest-mark.skip-->
```python
print("testing testing bogus output.")
```
```
incorrect expected output
```

## mark.skipif directive.

Use mark.skipif on Python code blocks.
This test case will only run when Python
is version 3.8 or higher. int.as_integer_ratio() is new in
Python 3.8.
<!--phmdoctest-label skipif-pyversion-->
<!--phmdoctest-mark.skipif<3.8-->
```python
b = 10
print(b.as_integer_ratio())
```
```
(10, 1)
```


## mark.skip group name directive.

<!--phmdoctest-mark.my-group-->
```python
b = 10
print(b.as_integer_ratio())
```
```
(10, 1)
```
## label directive on a session.
This will generate a test case called **doctest_print_coffee()**.
It does not start with test_ to avoid collection as a test item.
<!--phmdoctest-label session-->
```py
>>> print("coffee")
coffee
```

## This will be marked as the setup code.

<!--phmdoctest-setup-->
```python
import math

mylist = [1, 2, 3]
a, b = 10, 11

def doubler(x):
    return x * 2
```

## This will be marked as the teardown code.
Note `<!--phmdoctest-teardown-->` directive in the Markdown file.
<!--phmdoctest-teardown-->
```python
mylist.clear()
assert not mylist, "mylist was not emptied"
```

## Does not qualify as a directive due to 2 blank lines before FCB.
<!-- Directive is not found if more than 2 blank lines between FCB and HTML comments-->
<!--phmdoctest-teardown-->


```python
mylist.clear()
assert not mylist, "mylist was not emptied"
```

