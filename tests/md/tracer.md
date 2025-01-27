# traceback example

## Library under test is part of the example

```python
"""Example classes."""
import sys


class RightAnswer:
    """Provide correct answer to the question"""

    answer = "apples"

    def ask(self, question: str) -> str:
        _ = question
        return self.answer


class WrongAnswer:
    """Provide wrong answer to the question"""

    answer = "very small rocks"

    def ask(self, question: str) -> str:
        _ = question
        return self.answer


class RaiserBot:
    """Print to both stdout, stderr and raise ValueError."""

    def ask(self, question: str) -> str:
        print(f"This is RaiserBot.ask() on stdout answering '{question}'.")
        print("This is RaiserBot.ask() on stderr: Uh oh!", file=sys.stderr)
        raise ValueError("What was the question?")
```

### pass result

```python
pass_bot = RightAnswer()
answer = pass_bot.ask(question="What floats?")
assert answer == "apples"
```

### failed result

Create a WrongAnswer instance and ask a question.
The WrongAnswer instance ask() method returns an
incorrect answer.
The assert statement checks the answer,
finds that
it is wrong and raises an AssertionError.
This FCB is given 'failed' status.

```python
fail_bot = WrongAnswer()
answer = fail_bot.ask(question="What floats?")
assert answer == "apples"
```

### error result

Now we are going to cause the example pass_bot instance to raise an
exception by calling the method inquire() which does not exist.
This raises an AttributeError in the library which propagates
up and out of the first line of the FCB below.
This FCB is given 'error' status.

```python
answer = pass_bot.inquire(query="What floats?")
assert answer == "apples"
```

The test runner keeps going even after
an exception. To stop
on first failure use the "-f" option.

```python
answer = pass_bot.ask(question="What floats?")
assert answer == "apples"
```

The next FCB causes an earlier example FCB to raise an exception.
The exception is returned to FCB below.
Then it propagates up out of the FCB to the _phm_printer context manager
and finally propagates up to the test runner.

```python
raiser_bot = RaiserBot()
_ = raiser_bot.ask(question="What floats?")
```

### Checking expected output

Add an FCB that immediately follows a Python code block that has no info string
or the info string `expected-output`. Captured stdout is compared to the block.
In the log a "o" after the filename indicates expected output was checked.

```python
print("Incorrect expected output.")
```

```expected-output
Hello World!
```
