### Skipif directive has non-numeric or negative minor number.

Malformed skipif directives silently ignored. Both blocks pass.
<!--phmutest-skipif<3.A-->
```python
user = 'eric_idle'
print(f"{user=}")
```

```
user='eric_idle'
```

<!--phmutest-skipif<3.-1-->
```python
user = 'palin'
print(f"{user=}")
```

```
user='palin'
```
