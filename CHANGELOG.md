# Changelog

<!-- Refs since the last tagged release: 07b6d0b..HEAD -->
## [1.0.1] - 2025-03-11

This release has changes to docs, tests, and comments.

### Removed

- Remove unneeded code left over after earlier commit.
([`33de2dc`](https://github.com/tmarktaylor/phmutest/commit/33de2dc))
See ([`d77e05a`](https://github.com/tmarktaylor/phmutest/commit/d77e05a))

## [1.0.0] - 2025-02-08

### Changed

- For broken FCB show whole statement if multiline.
  ([`238c41a`](https://github.com/tmarktaylor/phmutest/commit/238c41a))

### Removed

- Remove syntax highlight exception names in log.
  ([`d77e05a`](https://github.com/tmarktaylor/phmutest/commit/d77e05a))

## [0.1.0] - 2025-01-27

### Changed

- Allow malformed dotted path to raise exception.
  ([`93b0af3`](https://github.com/tmarktaylor/phmutest/commit/93b0af3))
- Rewrite toml configuration logic, add code for new features.
  ([`0049211`](https://github.com/tmarktaylor/phmutest/commit/0049211))
  Note runpytest feature was yanked.
- Move fill_in() and helpers to new file fillin.py.
  ([`f1a9dee`](https://github.com/tmarktaylor/phmutest/commit/f1a9dee),
  [`bf240be`](https://github.com/tmarktaylor/phmutest/commit/bf240be),
  [`2af6fc7`](https://github.com/tmarktaylor/phmutest/commit/2af6fc7),
  [`9c0c702`](https://github.com/tmarktaylor/phmutest/commit/9c0c702))
- Move SysTool from skip.py to systool.py
  ([`57b831b`](https://github.com/tmarktaylor/phmutest/commit/57b831b))
- No longer de-indenting setup/teardown blocks.
  ([`3641b32`](https://github.com/tmarktaylor/phmutest/commit/3641b32))
- Move docs/recent_changes.md to CHANGELOG.md and format based on advice
  in [common-changelog] and [keep a changelog].
  ([`43b2bd7`](https://github.com/tmarktaylor/phmutest/commit/43b2bd7),
  [`6b75fb6`](https://github.com/tmarktaylor/phmutest/commit/6b75fb6))
- Explicitly complete the with suite in code.py.
  ([`a2b3248`](https://github.com/tmarktaylor/phmutest/commit/a2b3248))

### Added

- New features: Show broken FCBs, traceback, --color, --stdout,
  syntax highlighting --style.
  ([`8f1ff10`](https://github.com/tmarktaylor/phmutest/commit/8f1ff10),
  [`7ddbbca`](https://github.com/tmarktaylor/phmutest/commit/7ddbbca),
  [`c410da7`](https://github.com/tmarktaylor/phmutest/commit/c410da7),
  [`ecb4335`](https://github.com/tmarktaylor/phmutest/commit/ecb4335),
  [`8ab39c3`](https://github.com/tmarktaylor/phmutest/commit/8ab39c3),
  [`9f83e09`](https://github.com/tmarktaylor/phmutest/commit/9f83e09),
  [`153022e`](https://github.com/tmarktaylor/phmutest/commit/153022e),
  [`8a3b4b2`](https://github.com/tmarktaylor/phmutest/commit/8a3b4b2),
  [`a79d946`](https://github.com/tmarktaylor/phmutest/commit/a79d946))
- Support doModuleCleanups() for running with pytest.
  ([`0de3c40`](https://github.com/tmarktaylor/phmutest/commit/0de3c40))
- Add ':' as a delimiter of the FCB info string.
  ([`44c0032`](https://github.com/tmarktaylor/phmutest/commit/44c0032),
  [`49f49fb`](https://github.com/tmarktaylor/phmutest/commit/49f49fb),
  [`039cb0e`](https://github.com/tmarktaylor/phmutest/commit/039cb0e))
- Add dev folder local development scripts.
  ([`785ddcf`](https://github.com/tmarktaylor/phmutest/commit/785ddcf))
- Add note to docs: Each block must start with no indent level.
  ([`139acd6`](https://github.com/tmarktaylor/phmutest/commit/139acd6))

### Removed

- Remove cases.deindent() since no longer used.
  ([`8f64dfd`](https://github.com/tmarktaylor/phmutest/commit/8f64dfd))
- Delete junit XML example.
  ([`4397244`](https://github.com/tmarktaylor/phmutest/commit/4397244))
- Remove requirement for typing module.
  ([`e8051f6`](https://github.com/tmarktaylor/phmutest/commit/e8051f6))
- Remove extra blank line in generated testfile.
  ([`a4424ff`](https://github.com/tmarktaylor/phmutest/commit/a4424ff))

### Fixed

- Update main.py- Add docstrings, fix entry_point().
  ([`7c23dae`](https://github.com/tmarktaylor/phmutest/commit/7c23dae))
- Doc fixes-
  ([`2fcdfc9`](https://github.com/tmarktaylor/phmutest/commit/2fcdfc9),
  [`9aaf826`](https://github.com/tmarktaylor/phmutest/commit/9aaf826))

## [0.0.4] - 2024-09-05

- Bugfix- Issue- The generated expected output check in code mode
  asserts if the FCB length is greater than a fairly small value.
- Python source formatting updates per Black 24.3.0.

## [0.0.3] - 2023-09-24

- Add test_importer.py. Cleanups

## [0.0.2] - 2023-09-15

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

## [0.0.1] - 2023-08-14

- Initial upload to Python Package Index.

[1.0.1]: https://github.com/tmarktaylor/phmutest/releases/tag/v1.0.1

[1.0.0]: https://github.com/tmarktaylor/phmutest/releases/tag/v1.0.0

[0.1.0]: https://github.com/tmarktaylor/phmutest/releases/tag/v0.1.0

[0.0.4]: https://github.com/tmarktaylor/phmutest/releases/tag/v0.0.4

[0.0.3]: https://github.com/tmarktaylor/phmutest/releases/tag/v0.0.3

[0.0.2]: https://github.com/tmarktaylor/phmutest/releases/tag/v0.0.2

[0.0.1]: https://github.com/tmarktaylor/phmutest/releases/tag/v0.0.1

[common-changelog]: https://common-changelog.org

[keep a changelog]: https://keepachangelog.com/en/1.1.0
