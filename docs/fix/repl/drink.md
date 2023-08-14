# Fixture example: globs and resource cleanup in REPL Mode

The command line below produces the output at the bottom.

The name drink is assigned by the fixture function "init" in
[drink.py](drink_py.md).

```py
>>> drink
tea
```

```py
>>> drink.add(EXTRA)
>>> drink
tea + sugar
```

## phmutest command line.

```
phmutest docs/fix/repl/drink.md --fixture docs.fix.repl.drink.init --replmode --log
```

## phmutest output.

```
Acquiring Drink tea. ...
Releasing Drink tea + sugar. ...

log:
args.files: 'docs/fix/repl/drink.md'
args.fixture: 'docs.fix.repl.drink.init'
args.replmode: 'True'
args.log: 'True'

location|label             result
-------------------------  ------
docs/fix/repl/drink.md:8.  pass
docs/fix/repl/drink.md:13  pass
-------------------------  ------
```

Notice that 'Acquiring' and 'Releasing' lines in the output
precede the log.  In --replmode the --log printing happens after all
testing and cleanup completes.

