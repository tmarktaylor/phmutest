# Recent changes

0.0.1 - 2023-08-14

- Initial upload to Python Package Index.

0.0.2 - 2023-09-15

- Bugfix- Use new recipe in importer.py to import the fixture function.
- Add main.command().
- Remove import io, sys, contextlib from generated testfile.
- Catch exception raised by --replmode --fixture.
- Add FCB info string "expected-output" to indicate expected output.
- Add patch point to change info strings that indicate expected output.
- Indicate expected output was checked with "o" in --log location.
- Moved options.entry_points to setup.cfg and removed setup.py.
- Markdown linting.
- Setup classifiers, cleanups, Docs, renames.
- Move twine check to build.yml.
- serialize ci.yml jobs

0.0.3 - 2023-09-24

- Add test_importer.py. Cleanups

0.0.4 - 2024-09-05

- Bugfix- Issue- The generated expected output check in code mode
  asserts if the FCB length is greater than a fairly small value.
- Python source formatting updates per Black 24.3.0.
