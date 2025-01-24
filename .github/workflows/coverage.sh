python3 -m coverage erase
python3 -m coverage run --branch --source=src --append -m phmutest --version
# Exercise code that handles import errors when the
# extras modules are not installed.
python3 -m coverage run --branch --source=src --append -m phmutest README.md --log
# Manually install the setup.cfg extras here.
# Typically they are installed by
# pip install phmutest[colors, pytest, traceback]
# Here, we run checked out sources for coverage, not an installed phmutest.
pip install colorama
pip install pygments
pip install pytest
pip install pytest-subtests
pip install stackprinter
python3 -m coverage run --branch --source=src --append -m phmutest README.md --report
python3 -m coverage run --branch --source=src --append -m phmutest docs/repl/REPLexample.md --log --replmode
python3 -m coverage run --branch --source=src --append -m phmutest --version
python3 -m coverage run --branch --source=src --append -m phmutest tests/md/no_code_blocks.md --log
python3 -m coverage run --branch --source=src --append -m phmutest README.md
python3 -m coverage run --branch --source=src --append -m phmutest README.md --log --style solarized-dark
python3 -m coverage run --branch --source=src --append -m phmutest README.md --log --style default
python3 -m coverage run --branch --source=src --append -m pytest tests
# Coverage for running a generated testfile with errors separately with pytest.
python3 -m phmutest tests\md\does_not_print.md --generate dev/test_temptestfile.py
python3 -m coverage run --branch --source=src --append -m pytest dev/test_temptestfile.py
python3 -m coverage report --show-missing --precision=2
python3 -m coverage xml
