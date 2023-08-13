# Input file for testing --select and --deselect
## Python code blocks
<!--phmdoctest-mark.group-1-->
```python
print("legacy-group-1")
```

<!--phmutest-group group-1-->
```python
print("code-group-1")
```

<!--phmutest-group group-2-->
<!--phmutest-group group-3-->
```python
print("code-group-2")
print("code-group-3")
```

<!--phmutest-group group-3-->
<!--phmutest-group group-4-->
```python
print("code-group-3")
print("code-group-4")
```

## Python interactive session blocks

<!--phmdoctest-mark.group-1-->
```python
>>> print()  # legacy-1
```

<!--phmutest-group repl-1-->
```python
>>> print()  # repl-1
```

<!--phmdoctest-mark.repl-5-->
```python
>>> print()  # legacy-repl-5
```

<!--phmutest-group repl-5-->
```python
>>> print()  # repl-5
```

<!--phmutest-group repl-6-->
<!--phmutest-group repl-7-->
```python
>>> print()  # repl-6
>>> print()  # repl-7
```

<!--phmutest-group repl-7-->
<!--phmutest-group repl-8-->
```python
>>> print()  # repl-7
>>> print()  # repl-8

