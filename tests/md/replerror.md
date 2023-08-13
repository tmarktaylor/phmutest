# Test cases for Python interactive sessions (doctest)s

```python
>>> from tests.fail.bumper import MyBumper
```

```python
>>> bumper = MyBumper(1)
```

```python
>>> print(bumper.bump())
2
```

Create a MyBumper instance with an str value.

```python
>>> bumper2 = MyBumper("a")
```

Show that command line --skip skips the test.
<!--phmutest-skip-->
```python
>>> assert False, "--skip identified block"
```


The bump() call below raises a TypeError since += 1 is not
allowed on type str.

```python
>>> print(bumper2.bump())
aa
```


Show that skip directive skips the test.
```python
>>> # MYSKIPPATTERN
>>> assert False, "directive identified block"
```


Show that Python version conditional skip skips the test.
<!--phmutest-skipif<3.9999-->
```python
>>> assert False, "--skip identified block"
```



Show that Python version conditional skip runs the test.
<!--phmutest-skipif<3.3-->
```python
>>> print("run this test if Python version >= 3.3")
run this test if Python version >= 3.3
```

