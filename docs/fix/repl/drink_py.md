# docs/fix/repl/drink.py
```python
"""--replmode fixture acquires resource, passes to tests via globs, releases it."""
from phmutest.fixture import Fixture


class Drink:
    """Represents an acquired and released resource."""

    def __init__(self, name):
        self.name = name
        print(f"Acquiring Drink {self.name}. ...")

    def release(self):
        print(f"Releasing Drink {self.name}. ...")

    def add(self, ingredient):
        self.name = self.name + " + " + ingredient

    def __repr__(self):
        return self.name


EXTRA = "sugar"


def init(**kwargs):
    """Initialize Drink, pass to tests as dict globs. Pass its cleanup function."""

    drink = Drink("tea")
    globs = dict(drink=drink, EXTRA=EXTRA)
    return Fixture(globs=globs, repl_cleanup=drink.release)
```
