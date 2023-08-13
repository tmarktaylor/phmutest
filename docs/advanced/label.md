# label directive on code and sessions

When used on a Python code block or session the label is printed
after the filename and line in the log.
Here is the command and terminal output of the
label, skip, and skipif directive example
Please note this example is in a different file than this page's source.

```
phmutest tests/md/directive1.md --log --replmode
```

In the output, note the label "doctest_print_coffee" shows after
tests/md/directive1.md:69 below.

```
log:
args.files: 'tests/md/directive1.md'
args.replmode: 'True'
args.log: 'True'

location|label                                  result  skip reason
----------------------------------------------  ------  -------------
tests/md/directive1.md:35.....................  skip    phmutest-skip
tests/md/directive1.md:69 doctest_print_coffee  pass
----------------------------------------------  ------  -------------
```

