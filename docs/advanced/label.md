# label directive on code and sessions

When used on a Python code block or session the label is printed
after the filename and line in the log.
Here is the command and terminal output of the
label, skip, and skipif directive example
Please note this example is in a different file than this page's source.

```shell
phmutest tests/md/directive1.md --log --replmode
```

In the output, note the label "doctest_print_coffee" shows after
tests/md/directive1.md:78 below.

```txt
log:
args.files: 'tests/md/directive1.md'
args.replmode: 'True'
args.log: 'True'

location|label                                  result  reason
----------------------------------------------  ------  -------------
tests/md/directive1.md:41.....................  skip    phmutest-skip
tests/md/directive1.md:78 doctest_print_coffee  pass
----------------------------------------------  ------  -------------
```
