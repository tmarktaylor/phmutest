# docs/share/file1.md

First file of share across files demo.

```python
from dataclasses import dataclass
```


```python
@dataclass
class BeverageActivity:
    beverage: str
    activity: str

    def combine(self) -> str:
        if self.beverage == "coffee" and self.activity == "coding":
            return "enjoyment"
        else:
            return self.beverage + "-" + self.activity
```

Use `BeverageActivity` defined above to create the name `cc`.
```python
cc = BeverageActivity("coffee", "coding")
print(cc.combine())
```

```
enjoyment
```

Create the name `we` for use in later files.
```python
we = BeverageActivity("water", "exercise")
```

