# Test Markdown for setup but no teardown directives.

## These are setup code blocks.

Setup code blocks render to SetupClass.
Alternatively, they render to setUpModule when file is
specified in the command line option --setup-across-files.

<!--phmutest-setup-->
```python
    import math
```
<!--phmutest-setup-->
```python
def my_function(x):
    return x + 1


myglobs_list = [1, 2, 3, 4, "A"]
```

## Python fenced code block and expected output under test.

This is the Python example we want to check.

```python
print(math.floor(10.7))
print(myglobs_list)
print(my_function(2))
```

Expected output:
```
10
[1, 2, 3, 4, 'A']
3
```
Note that Python prints the string value with single quotes.

This block assigns a name to be shared across files.
Note that all names including temporary variables are shared.
```python
shared_int = 9999
```

```python
shared_string = "coffee"
print(shared_string)
```

```
coffee
```
## There are no teardown blocks.

