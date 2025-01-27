# python3 -m is required for README.md example to import docs.answerlib and others
python3 -m phmutest README.md tests/md/directive1.md --log --color --style one-dark
python3 -m phmutest tests/md/tracer.md --log --color
python3 -m phmutest docs/repl/REPLexample.md --log --replmode -c --style one-dark
python3 -m phmutest tests/md/tracer_repl.md --log --replmode -c
true  # script always succeeds
