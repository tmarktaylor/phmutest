# docs/share/file2.md

Second file of --share-across-files demo.

This file references the names shared from [file1.md](file1.md).

Show the name `we` is visible.
```python
print(we.combine())
```

```
water-exercise
```

Show the name `BeverageActivity` is visible.
Create the name `bp`.
```python
bp = BeverageActivity("beer", "partying")
print(bp.combine())
```

```
beer-partying
```

