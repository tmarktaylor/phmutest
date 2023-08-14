# docs/share/file3.md

Third file of --share-across-files demo.

This file references the names shared from [file1.md](file1.md) and [file2.md](file2.md)

Use `bp` defined in file2.md
```python
print(bp.combine())
```

```
beer-partying
```

Use the name `BeverageActivity` defined in file1.md.
```python
ss = BeverageActivity("soda", "snacking")
print(ss.combine())
```

```
soda-snacking
```

