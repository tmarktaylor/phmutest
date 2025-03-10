# Broken REPL example

When tests fail we show what caused the error to help you quickly find the root cause.
This example shows how to use the Python library answerlib
| [answerlib.py](../answerlib_py.md).  The ask method returns an answer.
The example imports classes from answerlib. | [phmutest output](#console-stdout)

```python
>>> from docs.answerlib import RightAnswer, WrongAnswer, RaiserBot
```

Create a RightAnswer instance
and ask a question.
The assert statement checks the answer.
phmutest assigns a pass/failed/error/skip status to each Python FCB.
This FCB is given 'pass' status.
Note how the example continues across multiple FCBs.
It continues for the
entire Markdown file.

## pass result

```python
>>> pass_bot = RightAnswer()
>>> pass_bot.ask(question="What floats?")
'apples'
```

## failed result

Create a WrongAnswer instance and ask a question.
The WrongAnswer instance ask() method returns an
incorrect answer.
The assert statement checks the answer,
finds that
it is wrong and raises an AssertionError.
This FCB is given 'failed' status.

```python
>>> fail_bot = WrongAnswer()
>>> fail_bot.ask(question="What floats?")
'apples'
```

## error result

Now we are going to cause the answerlib to raise an
exception by calling the method inquire() which does not exist.
This raises an AttributeError in the library which propagates
up and out of the first line of the FCB below.
This FCB is given 'error' status.

```python
>>> pass_bot.inquire(query="What floats?")
'apples'
```

The test runner keeps going even after an exception. To stop
on first failure use the "-f" option.

```python
>>> pass_bot.ask(question="What floats?")
'apples'
```

Cause another exception within answerlib to see the FCB line
where the exception propagates out of the FCB in the log.
This FCB is also given 'error' status. See the results in the
log below.

```python
>>> raiser_bot = RaiserBot()
>>> _ = raiser_bot.ask(question="What floats?")
```

## phmutest command line

```shell
phmutest docs/repl/REPLexample.md --summary --log --replmode
```

## console stdout

```txt
**********************************************************************
Line 42, in docs/repl/REPLexample.md
Failed example:
    assert answer == "apples", f"got '{answer}'"
Exception raised:
    Traceback (most recent call last):
      File "C:\Users\XXX\AppData\Local\Programs\Python\Python310\lib\doctest.py", line 1350, in __run
        exec(compile(example.source, filename, "single",
      File "<doctest docs/repl/REPLexample.md[6]>", line 1, in <module>
        assert answer == "apples", f"got '{answer}'"
    AssertionError: got 'very small rocks'
**********************************************************************
Line 54, in docs/repl/REPLexample.md
Failed example:
    answer = pass_bot.inquire(query="What floats?")
Exception raised:
    Traceback (most recent call last):
      File "C:\Users\XXX\AppData\Local\Programs\Python\Python310\lib\doctest.py", line 1350, in __run
        exec(compile(example.source, filename, "single",
      File "<doctest docs/repl/REPLexample.md[7]>", line 1, in <module>
        answer = pass_bot.inquire(query="What floats?")
    AttributeError: 'RightAnswer' object has no attribute 'inquire'
**********************************************************************
Line 55, in docs/repl/REPLexample.md
Failed example:
    assert answer == "apples", f"got '{answer}'"
Exception raised:
    Traceback (most recent call last):
      File "C:\Users\XXX\AppData\Local\Programs\Python\Python310\lib\doctest.py", line 1350, in __run
        exec(compile(example.source, filename, "single",
      File "<doctest docs/repl/REPLexample.md[8]>", line 1, in <module>
        assert answer == "apples", f"got '{answer}'"
    AssertionError: got 'very small rocks'
**********************************************************************
Line 73, in docs/repl/REPLexample.md
Failed example:
    _ = raiser_bot.ask(question="What floats?")
Exception raised:
    Traceback (most recent call last):
      File "C:\Users\XXX\AppData\Local\Programs\Python\Python310\lib\doctest.py", line 1350, in __run
        exec(compile(example.source, filename, "single",
      File "<doctest docs/repl/REPLexample.md[12]>", line 1, in <module>
        _ = raiser_bot.ask(question="What floats?")
      File "C:\Users\XXX\Documents\u0\docs\answerlib.py", line 32, in ask
        raise ValueError("What was the question?")
    ValueError: What was the question?
**********************************************************************
Line 83, in docs/repl/REPLexample.md
Failed example:
    print("Incorrect expected output.")
Expected:
    Hello World!
Got:
    Incorrect expected output.

summary:
metric
--------------------  -
blocks run            6
blocks passed         3
blocks failed         1
blocks skipped        0
suite errors          2
Markdown files        1
files with no blocks  0
deselected blocks     0
--------------------  -

log:
args.files: 'docs/repl/REPLexample.md'
args.replmode: 'True'
args.log: 'True'
args.summary: 'True'

location|label               result  reason
---------------------------  ------  ---------------------------------------------------------------
docs/repl/REPLexample.md:8.  pass
docs/repl/REPLexample.md:23  pass
docs/repl/REPLexample.md:39  failed
docs/repl/REPLexample.md:53  error   AttributeError: 'RightAnswer' object has no attribute 'inquire'
docs/repl/REPLexample.md:61  pass
docs/repl/REPLexample.md:71  error   ValueError: What was the question?
---------------------------  ------  ---------------------------------------------------------------

docs/repl/REPLexample.md:39
    40  >>> fail_bot = WrongAnswer()
>   41  >>> fail_bot.ask(question="What floats?")
    42  'apples'

docs/repl/REPLexample.md:53
>   54  >>> pass_bot.inquire(query="What floats?")
    55  'apples'
        AttributeError: 'RightAnswer' object has no attribute 'inquire'

docs/repl/REPLexample.md:71
    72  >>> raiser_bot = RaiserBot()
>   73  >>> _ = raiser_bot.ask(question="What floats?")
        ValueError: What was the question?
```

## Notes

- The console stdout above does not show the line
  "This is RaiserBot.ask() on stderr: Uh oh!" which was printed
  on stderr.
- The location is the file and line number of the opening fence of the FCB.
- To see Markdown line numbers, on GitHub view this file and choose
  the Code button. (Code is between Preview and Blame).
- An FCB can have more than one line that raises an exception. Note the
  suite errors metric above is larger than the number of blocks that
  have "error" result.
- There is one Exception raised: line in the tracebacks above for
  each counted suite error.
