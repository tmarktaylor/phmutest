# Test share-across-files of file with setup directive.

Names shared_int and shared_string are shared from non-setup blocks
in the file setupnoteardown.md. That file is specified by the
--share-across-files command line option. See the
tests/toml/acrossfiles2.toml.

Note that Python prints the string value with single quotes.


Names shared_int and shared_string are shared from the non-setup
blocks in the file specified by --share-across-files.
```python
print(shared_int)
print(shared_string)
```

Expected output:
```
9999
coffee
```

