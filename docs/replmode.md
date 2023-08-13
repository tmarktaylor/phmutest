# --replmode example

The command line below produces the output at the bottom.
The --replmode option runs fenced code blocks with doctests.
They are described by the Python Standard Library module doctest.
Note there is no need for an empty line at the end of each
fenced code block.

All fenced code blocks in the file are joined into one long docstring.

```python
>>> a = "Greetings Planet!"
>>> a
'Greetings Planet!'
>>> b = 12
>>> b
12
```

Example borrowed from Python Standard Library
fractions documentation.
```py
>>> from fractions import Fraction
>>> Fraction(16, -10)
Fraction(-8, 5)
>>> Fraction(123)
Fraction(123, 1)
>>> Fraction()
Fraction(0, 1)
>>> Fraction('3/7')
Fraction(3, 7)
```

Here we show name 'b' assigned in the first FCB is still visible.
```py
>>> b
12
```

# phmutest command line.

```
phmutest docs/replmode.md --replmode --log
```

## phmutest output.

```
log:
args.files: 'docs/replmode.md'
args.replmode: 'True'
args.log: 'True'

location|label       result
-------------------  ------
docs/replmode.md:11  pass
docs/replmode.md:22  pass
docs/replmode.md:35  pass
-------------------  ------
```

