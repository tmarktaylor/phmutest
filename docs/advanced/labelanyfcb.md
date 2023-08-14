# label directive on any FCB
On any fenced code block, the label directive identifies the block
for later retrieval by the class **phmdoctest.tool.FCBChooser()**.
The `FCBChooser` is used separately from phmutest in
a different pytest file. This allows the test developer to write
additional test cases for fenced code blocks that are not handled by
phmutest. The directive value can be any string.

[tool API](../api.md)

Here is a YAML FCB with a `<!--phmutest-label my-label-->` label directive.
<!--phmutest-label my-label-->
<!-- Other one line HTML comments or directives-->
```yml
theme: readthedocs
```

Here is example code to retrieve the directive. Note that FCBs typically
end with a newline.

```python
import phmutest.tool
chooser = phmutest.tool.FCBChooser("docs/advanced/labelanyfcb.md")
fcb_contents = chooser.select(label="my-label")
print(fcb_contents[0], end="")
```

```
theme: readthedocs
```

