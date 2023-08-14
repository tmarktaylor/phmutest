# --share-across-files example

The --share-across-files option generates test code that shares the names assigned
by the files specified by the option to the files specified later in the list
of input files (the input files are specified by FILE as shown in the usage.)
file1.md shares its names to file2.md and file3.md. file2.md shares its names
to file3.md.

It is tempting to use shell file wildcards for the FILE names. Please be aware that
the order of files in the wildcard expansion might not be the order that you want.
That order may differ between shell and operating system combinations.
If you are calling from Python there will be no shell wildcard expansion.

- [docs/share/file1.md](file1.md)
- [docs/share/file2.md](file2.md)
- [docs/share/file3.md](file3.md)

All the names assigned at the top level of all the Python blocks in the
file are shared. A later file might inadventently reassign a name that was
shared.

## phmutest command line.

```
phmutest docs/share/file1.md docs/share/file2.md docs/share/file3.md --share-across-files docs/share/file1.md docs/share/file2.md --log --summary
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
args.files: 'docs/share/file1.md'
args.files: 'docs/share/file2.md'
args.files: 'docs/share/file3.md'
args.share_across_files: 'docs/share/file1.md'
args.share_across_files: 'docs/share/file2.md'
args.log: 'True'
args.summary: 'True'

location|label          result
----------------------  ------
setUpModule...........
docs/share/file1.md:5.  pass
docs/share/file1.md:10  pass
docs/share/file1.md:24  pass
docs/share/file1.md:34  pass
docs/share/file2.md:8.  pass
docs/share/file2.md:18  pass
docs/share/file3.md:8.  pass
docs/share/file3.md:17  pass
tearDownModule........
----------------------  ------
```

