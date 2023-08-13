# Advanced feature details

## Directives

Directives are HTML comments associated with fenced code blocks.
They are edited into the Markdown file immediately before a fenced
code block. It is OK if other HTML comments are present either before
or after. A directive is recognized if it is in a continuous
series of either HTML comments or single blanks lines
ending at the fenced code block.

The `<!--phmutest-skip-->` directive in the raw Markdown below
is associated with the FCB.

~~~
<!--phmutest-skip-->
<!--Another HTML comment-->
```python
print("Hello World!")
```
Expected Output
```
Hello World!
```
~~~

Since directives are HTML comments they are not visible in rendered Markdown.
View directives on [Latest README on GitHub][1]
by pressing the `Code` button in the banner at the top of the file.

|       Directive HTML comment       | Use on FCBs  | Ok in REPL mode
| :--------------------------------: | :----------: | :----------:
| `<!--phmutest-label TEXT-->`       | any          | yes
| `<!--phmutest-skip-->`             | code, output | yes
| `<!--phmutest-skipif<3.N-->`       | code         | yes
| `<!--phmutest-setup-->`            | code         | No
| `<!--phmutest-teardown-->`         | code         | No
| `<!--phmutest-group NAME -->`      | code         | yes

List of directives




|  phmdoctest directive                 | phmutest equivalent
| :---------------------------------: | :---------:
| `<!--phmdoctest-label TEXT-->`      | `<!--phmutest-label TEXT-->`
| `<!--phmdoctest-skip-->`            | `<!--phmutest-skip-->`
| `<!--phmdoctest-mark.skip-->`       | `<!--phmutest-skip-->`
| `<!--phmdoctest-mark.skipif<3.N-->` | `<!--phmutest-skipif<3.N-->`
| `<!--phmdoctest-setup-->`           | `<!--phmutest-setup-->`
| `<!--phmdoctest-teardown-->`        | `<!--phmutest-teardown-->`
| `<!--phmdoctest-mark.ATTRIBUTE-->`  | `<!--phmutest-group NAME -->`

phmdoctest directives recognized by phmutest.


[Skip directive](advanced/skip.md)

[Skipif directive](advanced/skipif.md)

[Label directive, label and skipif example](advanced/label.md)

### Test groups

The test group directive identifies Python FCBs belonging to the group NAME.
Test groups can be included or excluded from testing by the --select and
--deselect command line options.

- Only one of --select and --deselect can be specified in a command.
- Excluded blocks will not have log entries.
- The --report option lists excluded blocks.
- The --summary option shows the number of deselected blocks.

### Setup and teardown

Blocks can be designated setup or teardown blocks by adding the
`<!--phmutest-setup-->` and `<!--phmutest-teardown-->` directives.
The Setup blocks are run by an instance of unittest.setUpClass().
All the names assigned in setUpClass() are dynamically shared
for the duration of that file's test class.

Setup and teardown is a niche and complex feature. Suggested reading:

- Python unittest **setUpClass**, **tearDownClass**, **setUpModule**, **tearDownModule**
- How it works | [Here](howitworks.md)

Setup blocks are useful when:

- used with teardown blocks to accomplish orderly teardown
- to document setup and teardown code examples
- to handle [phmdoctest][2] setup and teardown directives

A positional argument FILE may be added to the --setup-across-files option.
The file's setup blocks are run by **unittest.setUpModule()** and the names assigned in the
setup blocks are shared to **all** FILEs. Teardown blocks in FILE
are run by **unittest.tearDownModule()**.


[1]: https://github.com/tmarktaylor/phmutest/blob/master/README.md?plain=1
[2]: https://tmarktaylor.github.io/phmdoctest

