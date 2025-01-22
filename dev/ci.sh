# These were mostly copied from ci.yml
python3 -m phmutest --version
python3 -m phmutest docs/advanced/skip.md --log -c --style one-dark
python3 -m phmutest docs/advanced/skipif.md --log
python3 -m phmutest docs/advanced/label.md --log
python3 -m phmutest docs/advanced/labelanyfcb.md --log
python3 -m phmutest tests/md/project.md --report --style solarized-dark
python3 -m phmutest tests/md/optionflags.md --log --replmode --fixture tests.test_patching.setflags
python3 -m phmutest docs/fix/code/globdemo.md --fixture docs.fix.code.globdemo.init_globals --log --style one-dark
python3 -m phmutest tests/md/tracer_repl.md --log --replmode --color
python3 -m phmutest tests/md/tracer.md --log -c
# This test has intentional failing FCBs.
python3 -m phmutest tests/md/cleanups.md --fixture docs.fix.code.chdir.change_dir --log --runpytest only
#
isort . --profile black --skip "*_cache"
black **/*.py --check --force-exclude="tests/py|dev|t.py|t[0-9].py"
mypy src/phmutest --strict
mypy tests/test_type_packaging.py --strict
flake8 --max-complexity=10 --exclude .mine,tests/py,dev,t.py,t[0-9].py
