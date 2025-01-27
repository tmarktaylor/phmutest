# Show how generated testfile effects printed class name

Try running this Markdown file with this command directly
from the shell.

```txt
phmutest tests/md/qualname.md --log -v
```

```python
class RightAnswer:
    """Provide correct answer to the question"""

    answer = "apples"

    def ask(self, question: str) -> str:
        _ = question
        return self.answer
```

Print the class. Note we are printing the class here
not an instance.

```python
print(RightAnswer)
```

This what gets printed.

```expected-output
<class '_phm1.Test001.tests.<locals>.RightAnswer'>
```

The `__qualname__` attribute of the class was printed.

```python
assert "Test001.tests.<locals>.RightAnswer" == f"{RightAnswer.__qualname__}"
```

A way to show the classname is to print the `__name__` attribute.

```python
print(RightAnswer.__name__)
```

```expected-output
RightAnswer
```
