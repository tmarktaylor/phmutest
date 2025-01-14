rem These were mostly copied from ci.yml
py -m phmutest --version
py -m phmutest docs/advanced/skip.md --log -c --style one-dark
py -m phmutest docs/advanced/skipif.md --log
py -m phmutest docs/advanced/label.md --log
py -m phmutest docs/advanced/labelanyfcb.md --log
py -m phmutest tests/md/project.md --report --style solarized-dark
py -m phmutest tests/md/optionflags.md --log --replmode --fixture tests.test_patching.setflags
py -m phmutest docs/fix/code/globdemo.md --fixture docs.fix.code.globdemo.init_globals --log --style one-dark
py -m phmutest tests/md/tracer_repl.md --log --replmode --color
py -m phmutest tests/md/tracer.md --log -c
rem
isort . --profile black --skip "*_cache"
black **/*.py --check --force-exclude="tests/py|dev|t[0-9].py"
mypy src/phmutest --strict
mypy tests/test_type_packaging.py --strict
flake8 --max-complexity=10 --exclude .mine,tests/py,dev,t[0-9].py
