py -m coverage erase
py -m coverage run --branch --source=src --append -m phmutest README.md --report
py -m coverage run --branch --source=src --append -m phmutest docs/repl/REPLexample.md --log --replmode  --color
py -m coverage run --branch --source=src --append -m phmutest --version
py -m coverage run --branch --source=src --append -m phmutest tests/md/no_code_blocks.md --log
py -m coverage run --branch --source=src --append -m phmutest README.md
py -m coverage run --branch --source=src --append -m phmutest README.md --runpytest only
py -m coverage run --branch --source=src --append -m phmutest README.md --runpytest on-error
py -m coverage run --branch --source=src --append -m phmutest README.md --log --style
py -m coverage run --branch --source=src --append -m phmutest README.md --log --style default
py -m coverage run --branch --source=src --append -m pytest tests
rem Coverage for running a generated testfile with errors separately with pytest.
py -m phmutest tests\md\does_not_print.md --generate dev/test_temptestfile.py
py -m coverage run --branch --source=src --append -m pytest dev/test_temptestfile.py
py -m coverage report -m --precision=2
py -m coverage html --precision=2
