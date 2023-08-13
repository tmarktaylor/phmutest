#

## Example

The example starts by creating the object m.
```python
from hashlib import sha256
m = sha256()
```

The example continues here.
```python
m.update(b"hello World")
print(m.hexdigest()[0:5])
```

Expected output here is checked. This fenced code block does not
have an info string.

```
db406
```

The example continues here. It will continue for the entire file. This is
the last Python FCB in the file.
```python
m.update(b"more bytes")
print(m.hexdigest()[0:5])
```

Note the expected output is different.
```
4c6ea
```

<!--phmutest-label example1-outfile-->
<!--phmutest-skip-->
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

```
Floats.APPLES
Floats.CIDER
Floats.CHERRIES
Floats.ADUCK
```

<!--phmutest-label LABEL-->
```yml
on:
  push:
  pull_request:
    branches: [develop]
```
