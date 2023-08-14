# This is Markdown file directive1.md

Directives are HTML comments and are not rendered.
To see the directives press Edit on GitHub and then
the Raw button.

## skip directive. No test case gets generated.
It is OK to put a directive above pre-existing HTML comments.
The HTML comments are not visible in the rendered Markdown.

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

## Expected code block failure

<!--phmutest-label expected-failed-->
```python
print("testing bogus output.")
```
```
incorrect expected output
```

## skipif directive.

Use skipif on Python code blocks.
This test case will only run when Python is version 3.8 or higher.

<!--phmutest-skipif<3.8-->
```python
import sys
b = 10
print(b)
assert sys.version_info >= (3, 8)
```
```
10
```

## label directive on a session.
<!--phmutest-label doctest_print_coffee-->
```py
>>> print("coffee")
coffee
```
