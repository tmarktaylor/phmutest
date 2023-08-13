# --share-across-files --replmode example

The --share-across-files option generates test code that shares the names assigned
by the files specified by the option to the files specified later in the list
of input files (the input files are specified by FILE as shown in the usage.)
repl1.md shares its names to repl2.md and repl3.md. repl2.md shares its names
to repl3.md.

It is tempting to use shell file wildcards for the FILE names. Please be aware that
the order of files in the wildcard expansion might not be the order that you want.
That order may differ between shell and operating system combinations.
If you are calling from Python there will be no shell wildcard expansion.

- [docs/repl/repl1.md](repl1.md)
- [docs/repl/repl2.md](repl2.md)
- [docs/reol/repl3.md](repl3.md)

All the names assigned at the top level of all the Python blocks in the
file are shared. A later file might inadventently reassign a name that was
shared.

## phmutest command line.

```
phmutest docs/repl/repl1.md docs/repl/repl2.md docs/repl/repl3.md --replmode --share-across-files docs/repl/repl1.md docs/repl/repl2.md --log --summary
```

## phmutest output.

Terminal output after the `OK` line.
```
summary:
metric
--------------------  -
blocks run            8
blocks passed         8
blocks failed         0
blocks skipped        0
suite errors          0
Markdown files        3
files with no blocks  0
deselected blocks     0
--------------------  -

log:
args.files: 'docs/repl/repl1.md'
args.files: 'docs/repl/repl2.md'
args.files: 'docs/repl/repl3.md'
args.share_across_files: 'docs/repl/repl1.md'
args.share_across_files: 'docs/repl/repl2.md'
args.replmode: 'True'
args.log: 'True'
args.summary: 'True'

location|label         result
---------------------  ------
docs/repl/repl1.md:5.  pass
docs/repl/repl1.md:10  pass
docs/repl/repl1.md:24  pass
docs/repl/repl1.md:31  pass
docs/repl/repl2.md:8.  pass
docs/repl/repl2.md:15  pass
docs/repl/repl3.md:8.  pass
docs/repl/repl3.md:14  pass
---------------------  ------
```

