# Illegal delimiter after info string python 'language' part.

## None of these blocks will be detected as Python

```python!extraneous info string extension
from hashlib import sha256
m = sha256()
```

```python!extraneous info string extension
>>> print('Hello World!')
Hello World!
```

```python3@ extraneous info string extension
from hashlib import sha256
m = sha256()
```

```python3@ extraneous info string extension
>>> print('Hello World!')
Hello World!
```

```py!extraneous info string extension
from hashlib import sha256
m = sha256()
```

```py!extraneous info string extension
>>> print('Hello World!')
Hello World!
```

```py|extraneous info string extension
from hashlib import sha256
m = sha256()
```

```py|extraneous info string extension
>>> print('Hello World!')
Hello World!
```

```py3!extraneous info string extension
from hashlib import sha256
m = sha256()
```

```py3!extraneous info string extension
>>> print('Hello World!')
Hello World!
```

Note- phmutest will identify this as a code block despite the pycon info string.

```pycon@extraneous info string extension
from hashlib import sha256
m = sha256()
```

```pycon@extraneous info string extension
>>> print('Hello World!')
Hello World!
```

```{ .python }|extraneous info string extension
from hashlib import sha256
m = sha256()
```

```{ .python }|extraneous info string extension
>>> print('Hello World!')
Hello World!
```

## 1 more REPL block than code block

```py3!extraneous info string extension
>>> print('Hello World!')
Hello World!
```

## 1 matching code block

```{ .python } pycon extraneous info string extension
from hashlib import sha256
m = sha256()
```

## 1 matching repl block

```py3:extraneous info string extension
>>> print('Hello World!')
Hello World!
```
