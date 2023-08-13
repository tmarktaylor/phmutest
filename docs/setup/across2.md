# docs/setup/across2.md

## This block shows the temporary file exists.
```python
print(Path(FILENAME).read_text(encoding="utf-8"))
```
expected output:
```
apples, cider, cherries, very small rocks.
```

```python
assert Path.cwd() != original_cwd, "In a different cwd, presumably tempdir."
```

