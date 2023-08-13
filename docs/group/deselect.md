# --deselect example.

Using the phmutest-group directive and --deselect command line option.

## phmutest command line.

This command line selects all blocks in [select.md](select.md)
that don't have a "phmutest-group slow" directive.
```
phmutest docs/group/select.md --deselect slow --summary --log
```

## phmutest output.

Terminal output after the `OK` line.
Note in the log below that only the first block is tested.
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
args.deselect: 'slow'
args.log: 'True'
args.summary: 'True'

location|label           result
-----------------------  ------
docs/group/select.md:10  pass
-----------------------  ------
```

