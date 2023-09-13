# How it works and troubleshooting

## Identifying blocks

The Markdown [GFM fenced code blocks][1] are identified as Python by
looking at the [info string][2].
To be treated as Python the FCB info string should start
with one of these:

- python
- python3
- py
- py3
- pycon
- { .python }

It is ok if the info string is laden with additional text, it will be ignored.
The report shows the entire info string.

A block is identified as Python interactive session block (REPL) if
it matches a Python info_string and the first line of the block starts with the
session prompt: `'>>> '`.

An output block is a fenced code block that immediately follows a
Python code (not REPL) block that has an empty info string.
To prevent a text block following a code block from being detected
as expected output, add the info string `txt`.

## --report

The --report option shows these fenced block details:

- info_string
- Markdown file line number range
- role
- output block
- directives

### role field values

| role          | meaning               | referred to in the docs as
| :-------------| :-----------------:   | :-----------------:
| Role.CODE     | Python code block     | code blocks or Python code blocks
| Role.OUTPUT   | expected output block | output blocks
| Role.SESSION  | Python REPL block     | session or REPL blocks
| Role.NOROLE   | all other blocks

The report also shows a list called Deselected blocks: at the end that lists each
block that was excluded by the --select or --deselect option.

## modes of operation

phmutest runs in one of two modes testing either the code/output blocks
or session blocks. Code blocks and session blocks cannot interact
in a test.

Test session blocks with --replmode. Test code and output blocks otherwise.
--setup-across-files and the setup/teardown directives only work on code blocks.

[Code mode](codemode.md) | [Session mode](sessionmode.md)

[1]: https://github.github.com/gfm/#fenced-code-blocks
[2]: https://github.github.com/gfm/#info-string
[3]: https://docs.python.org/3/library/unittest.html
[4]: https://spec.commonmark.org
