# badsetup.md

Setup code block raises an exception.

<!--phmutest-setup-->
```python
import math

mylist = [1, 2, 3]
a, b = 10, 11

def doubler(x):
    return x * 2
```

## This test case shows the setup names are visible.
```python
print("math.pi=", round(math.pi, 3))
print(mylist)
print(a, b)
print("doubler(16)=", doubler(16))
```
expected output:
```
math.pi= 3.142
[1, 2, 3]
10 11
doubler(16)= 32
```

## This test case modifies mylist.
The objects created by the --setup code can be modified
and blocks run afterward will see the changes.
```python
mylist.append(4)
print(mylist)
```
expected output:
```
[1, 2, 3, 4]
```

## This test case sees the modified mylist.
```python
print(mylist == [1, 2, 3, 4])
```
expected output:
```
True
```

## This will be marked as the teardown code.
Note `<!--phmutest-teardown-->` directive in the Markdown file.
<!--phmutest-teardown-->
```python
mylist.clear()
assert not mylist, "mylist was not emptied"
raise(TypeError("badteardown.md in teardown block"))  # <------ bad part here
```
