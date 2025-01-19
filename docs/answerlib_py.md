# docs/answerlib.py

```python
"""Example user library imported and called from Markdown FCB."""

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
