# Example testfile traceback

Here is a --log output with the extra [traceback] installed. Each broken FCB is followed
by the traceback.
Please note near the bottom, for the FCB tests/md/tracer.md:90, there are two broken FCBs.
The ValueError is raised by tests/md/tracer.md:5 by the call in tests/md/tracer.md:90.
The broken FCB listings have line references to the Markdown file.
The tracebacks have line references to the rendered FCBs in the generated testfile.

```txt
log:
args.files: 'tests/md/tracer.md'
args.log: 'True'

location|label            result  reason
------------------------  ------  ---------------------------------------------------------------
tests/md/tracer.md:5....  pass
tests/md/tracer.md:41...  pass
tests/md/tracer.md:57...  failed  AssertionError
tests/md/tracer.md:71...  error   AttributeError: 'RightAnswer' object has no attribute 'inquire'
tests/md/tracer.md:80...  pass
tests/md/tracer.md:90...  error   ValueError: What was the question?
tests/md/tracer.md:101 o  failed
------------------------  ------  ---------------------------------------------------------------

tests/md/tracer.md:57
    58  fail_bot = WrongAnswer()
    59  answer = fail_bot.ask(question="What floats?")
>   60  assert answer == "apples"
        AssertionError

File "C:\Users\XXX\AppData\Local\Temp\YYY\_phm1.py", line 67, in tests
    18   def tests(self):
 (...)
    63       with self.subTest(msg="tests/md/tracer.md:57"):
    64           with _phmPrinter(_phm_log, "tests/md/tracer.md:57", flags=0x0, testfile_lineno=64):
    65               fail_bot = WrongAnswer()
    66               answer = fail_bot.ask(question="What floats?")
--> 67               assert answer == "apples"
    68
    ..................................................
     self.subTest = *****
     _phmPrinter = *****
     _phm_log = *****
     fail_bot = <_phm1.Test001.tests.<locals>.WrongAnswer object at ZZZ>
     answer = 'very small rocks'
     fail_bot.ask = <method 'Test001.tests.<locals>.WrongAnswer.ask' of <_phm1.T
                     est001.tests.<locals>.WrongAnswer object at ZZZ> _phm1.py:42>
    ..................................................

AssertionError

tests/md/tracer.md:71
>   72  answer = pass_bot.inquire(query="What floats?")
        AttributeError: 'RightAnswer' object has no attribute 'inquire'

File "C:\Users\XXX\AppData\Local\Temp\YYY\_phm1.py", line 72, in tests
    18   def tests(self):
 (...)
    68
    69       # ------ tests/md/tracer.md:71 ------
    70       with self.subTest(msg="tests/md/tracer.md:71"):
    71           with _phmPrinter(_phm_log, "tests/md/tracer.md:71", flags=0x0, testfile_lineno=71):
--> 72               answer = pass_bot.inquire(query="What floats?")
    73               assert answer == "apples"
    ..................................................
     self.subTest = *****
     _phmPrinter = *****
     _phm_log = *****
     answer = 'very small rocks'
     pass_bot.inquire = # AttributeError
          pass_bot = <_phm1.Test001.tests.<locals>.RightAnswer object
           at ZZZ>
    ..................................................

AttributeError: 'RightAnswer' object has no attribute 'inquire'

tests/md/tracer.md:90
    91  raiser_bot = RaiserBot()
>   92  _ = raiser_bot.ask(question="What floats?")
        ValueError: What was the question?

tests/md/tracer.md:5
     6  """Example classes."""
     7  import sys
     8
     9
    10  class RightAnswer:
    11      """Provide correct answer to the question"""
    12
    13      answer = "apples"
    14
    15      def ask(self, question: str) -> str:
    16          _ = question
    17          return self.answer
    18
    19
    20  class WrongAnswer:
    21      """Provide wrong answer to the question"""
    22
    23      answer = "very small rocks"
    24
    25      def ask(self, question: str) -> str:
    26          _ = question
    27          return self.answer
    28
    29
    30  class RaiserBot:
    31      """Print to both stdout, stderr and raise ValueError."""
    32
    33      def ask(self, question: str) -> str:
    34          print(f"This is RaiserBot.ask() on stdout answering '{question}'.")
    35          print("This is RaiserBot.ask() on stderr: Uh oh!", file=sys.stderr)
>   36          raise ValueError("What was the question?")

File "C:\Users\XXX\AppData\Local\Temp\YYY\_phm1.py", line 85, in tests
    18   def tests(self):
 (...)
    81       # ------ tests/md/tracer.md:90 ------
    82       with self.subTest(msg="tests/md/tracer.md:90"):
    83           with _phmPrinter(_phm_log, "tests/md/tracer.md:90", flags=0x0, testfile_lineno=83):
    84               raiser_bot = RaiserBot()
--> 85               _ = raiser_bot.ask(question="What floats?")
    86
    ..................................................
     self.subTest = *****
     _phmPrinter = *****
     _phm_log = *****
     raiser_bot = <_phm1.Test001.tests.<locals>.RaiserBot object at ZZZ>
     raiser_bot.ask = <method 'Test001.tests.<locals>.RaiserBot.ask' of <_phm1.Tes
                       t001.tests.<locals>.RaiserBot object at ZZZ>
                       _phm1.py:50>
    ..................................................

File "C:\Users\XXX\AppData\Local\Temp\YYY\_phm1.py", line 53, in ask
    50   def ask(self, question: str) -> str:
    51       print(f"This is RaiserBot.ask() on stdout answering '{question}'.")
    52       print("This is RaiserBot.ask() on stderr: Uh oh!", file=sys.stderr)
--> 53       raise ValueError("What was the question?")
    ..................................................
     self = <_phm1.Test001.tests.<locals>.RaiserBot object at ZZZ>
     question = 'What floats?'
     sys.stderr = *****
    ..................................................

ValueError: What was the question?

tests/md/tracer.md:101
   102  print("Incorrect expected output.")
AssertionError: 'Hello World!\n' != 'Incorrect expected output.\n'
- Hello World!
+ Incorrect expected output.
```
