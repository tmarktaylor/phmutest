# Examples to test patching doctest optionflags in --replmode.

## Passes.
```py
>>> print("Hello World!")
Hello World!
```

## Passes with NORMALIZE_WHITESPACE.
```py
>>> print("Hello   World!")
Hello World!
```

## Passes with ELLIPSIS.
```py
>>> print("Hello       World!")
Hello...World!
```
