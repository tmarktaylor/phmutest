#
```python
from tests.fail.bumper import MyBumper
```

```python
bumper = MyBumper(1)
```

```python
print(bumper.bump())
```

```
2
```

Create a MyBumper instance with an str value.

```python
bumper2 = MyBumper("a")
```

The bump() call below raises a TypeError since += 1 is not
allowed on type str.

```python
print(bumper2.bump())
```

This is incorrect expected output, but it is not checked
because its code block raised an exception.
```
aa
```

Show the test continues after catching the exception above.
You can pass the unittest option --failfast to stop instead.
```python
print("Still going.")
```

```
Wrong expected output.
```

