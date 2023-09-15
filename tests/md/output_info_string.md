# Test output FCB info string patch point

Markdown file to show the expected output FCB info string patch detects the
expected output FCB below.

## Interactive Python session (doctest)

```py
>>> print("Hello World!")
Hello World!
```

## Source Code and terminal output

Code:

```python
from enum import Enum

class Floats(Enum):
    APPLES = 1
    CIDER = 2
    CHERRIES = 3
    ADUCK = 4

for floater in Floats:
    print(floater)
```

sample output with the info string "captured-stdout".
A mock.patch() is required. The --log output will have
a " o" at the end of the location line for the
above python FCB.

```captured-stdout
Floats.APPLES
Floats.CIDER
Floats.CHERRIES
Floats.ADUCK
```
