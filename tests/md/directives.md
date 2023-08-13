# Test input file for direct.py for phmutest directives.

## skip directive
<!--phmutest-skip-->
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
<!--phmutest-skip-->

```
datetime.date(2021, 4, 18)
```

## skip directive on Python session.


<!--phmutest-skip-->

```py
>>> print("Hello World!")
incorrect expected output should fail
if test case is generated
```

## skipif directive.

<!--phmutest-label skipif-pyversion-->
<!--phmutest-skipif<3.8-->
```python
b = 10
print(b.as_integer_ratio())
```
```
(10, 1)
```


## test group directive.

<!--phmutest-group my-group-->
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
<!--phmutest-label session-->
```py
>>> print("coffee")
coffee
```

## This will be marked as the setup code.

<!--phmutest-setup-->
```python
import math

mylist = [1, 2, 3]
a, b = 10, 11

def doubler(x):
    return x * 2
```

## This will be marked as the teardown code.
Teardown code does not have an output block.
Note `<!--phmutest-teardown-->` directive in the Markdown file.
<!--phmutest-teardown-->
```python
mylist.clear()
assert not mylist, "mylist was not emptied"
```

## Does not qualify as a directive due to 2 blank lines before FCB.
<!-- Directive is not found if more than 2 blank lines between FCB and HTML comments-->
<!--phmutest-teardown-->


```python
mylist.clear()
assert not mylist, "mylist was not emptied"
```


<!--phmutest-skip-->
<!-- A multiline
    comment folowed by a
blank line -->

<!-- Another multiline
    comment folowed by a  -->

<!-- and another blank line -->

```python
assert False, "fail if we get here"
```
