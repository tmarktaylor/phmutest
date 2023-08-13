# docs/repl/repl3.md

Third file of --share-across-files --replmode demo.

This file references the names shared from [repl1.md](repl1.md) and [repl2.md](repl2.md)

Use `bp` defined in repl2.md
```python
>>> bp.combine()
'beer-partying'
```

Use the name `BeverageActivity` defined in repl1.md.
```python
>>> ss = BeverageActivity("soda", "snacking")
>>> ss.combine()
'soda-snacking'
```

