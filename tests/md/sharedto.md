# Test sharing of setup-across-files and share-across-files.

Names math, myglobs, and my_function shared from setup blocks by
using setup directives and sharing their file with
--setup-across-files.

```python
print(math.floor(10.7))
print(myglobs_list)
print(my_function(2))
```

Expected output:
```
10
[1, 2, 3, 4, 'A']
3
```
Note that Python prints the string value with single quotes.


Names shared_var and shared_string are shared from the non-setup
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


