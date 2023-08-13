# Test reader.py FCB DocNodes.
4 tilde start fence, 4 tilde closing fence
<!-- an html comment -->
~~~~python
```python
assert False
```
~~~~
4 tilde start fence, 5 tilde closing fence
~~~~python
```python
assert False
```
~~~~~
4 backtick start fence, 4 backtick closing fence
````python
~~~python
assert very small rocks
~~~
````
4 backtick start fence, 5 backtick closing fence
````python
~~~python
assert False
~~~
`````
indented 1 blank
 ~~~python
 assert False
 ~~~
  indented 2 blanks
  ~~~python
  assert False
  ~~~
   indented 3 blanks
   ```python
   assert False
   ```
    indented 4 blanks is not an FCB
    ```python
    assert False
    ```
    ~~~python
    assert False
    ~~~
    ````python
    assert False
    ````
    ~~~~python
    assert False
    ~~~~
<!-- another html comment -->
spacing is trimmed from info string
``` python
assert False
```
info string continues across blanks to EOL
~~~~ python extra stuff
assert False
~~~~

<details>

```python
print("testing @pytest.mark.skip().")
```
```
incorrect expected output
```

</details>

