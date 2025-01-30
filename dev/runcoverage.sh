python3 -m coverage erase
python3 -m coverage run --branch --source=src --append -m phmutest README.md --report
python3 -m coverage run --branch --source=src --append -m phmutest docs/repl/REPLexample.md --log --replmode --color
python3 -m coverage run --branch --source=src --append -m phmutest --version
python3 -m coverage run --branch --source=src --append -m phmutest tests/md/no_code_blocks.md --log
python3 -m coverage run --branch --source=src --append -m phmutest README.md
python3 -m coverage run --branch --source=src --append -m phmutest README.md --log --style solarized-dark
python3 -m coverage run --branch --source=src --append -m phmutest README.md --log --style default
python3 -m coverage run --branch --source=src --append -m pytest tests
# Coverage for running a generated testfile with errors separately with pytest.
python3 -m phmutest tests/md/does_not_print.md --generate dev/test_temptestfile.py
python3 -m coverage run --branch --source=src --append -m pytest dev/test_temptestfile.py
python3 -m coverage report -m
python3 -m coverage html
# Coverage for tests
# python3 -m coverage erase
# python3 -m coverage run --branch  --omit tests/check_classifiers.py --source=tests -m pytest tests
# python3 -m coverage report -m --precision=2
# python3 -m coverage html --precision=2 --dir htmltests