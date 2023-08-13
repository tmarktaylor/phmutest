# --select and group directive example.

Using the phmutest-group directive and --select command line option.

The command line below

## Fenced code block with no directives and expected output block.

Example code adapted from the Python Tutorial:
```python
squares = [1, 4, 9, 16, 25]
print(squares)
```
expected output:
```
[1, 4, 9, 16, 25]
```

## Code block with phmutest-group directive.

Look for the `<!--phmutest-group GROUP-->` directive in the Markdown file.
Note there is a space before the group name.
The directive declares the block to be a member of test group "slow".

<!--phmutest-group slow-->
```python
from datetime import date

d = date.fromordinal(730920)  # 730920th day after 1. 1. 0001
print(d)
```

```
2002-03-11
```

## phmutest command line.

This command line selectes all blocks in this file that have a
`<!--phmutest-group slow-->` directive.
```
phmutest docs/group/select.md --select slow --summary --log
```

## phmutest output.

Terminal output after the `OK` line.
Note in the log below that only the second block is tested.
```
summary:
metric
--------------------  -
blocks run            1
blocks passed         1
blocks failed         0
blocks skipped        0
suite errors          0
Markdown files        1
files with no blocks  0
deselected blocks     1
--------------------  -

log:
args.files: 'docs/group/select.md'
args.select: 'slow'
args.log: 'True'
args.summary: 'True'

location|label           result
-----------------------  ------
docs/group/select.md:26  pass
-----------------------  ------
```
[1]: https://github.com/tmarktaylor/phmutest/docs/group
