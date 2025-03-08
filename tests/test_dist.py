"""Test project packaging."""

import configparser
import subprocess
from pathlib import Path

import phmutest


class TestSameVersions:
    """Verify same release version string in all places.

    Obtain the version string from various places in the source tree
    and check that they are all the same.
    Compare all the occurrences to phmutest.__version__.
    This test does not prove the version is correct.
    Whitespace may be significant in some cases.
    Text surrounding the x.y.z version number may be tested as well.
    """

    package_version = phmutest.__version__

    def verify_found_in_file(self, filename, format_spec="{}"):
        """Format the package version and look for result in caller's file."""
        looking_for = format_spec.format(self.package_version)
        text = Path(filename).read_text(encoding="utf-8")
        assert looking_for in text, f"expected {self.package_version}"

    def test_readme_md(self):
        """Check the version near the top of README.md."""
        self.verify_found_in_file("README.md", "# phmutest {}\n")

    def test_changelog_tag(self):
        """Check the version tag name is anywhere in CHANGELOG.md."""
        self.verify_found_in_file("CHANGELOG.md", "## [{}] - ")

    def test_changelog_tag_link(self):
        """Check the version tag link is anywhere in CHANGELOG.md."""
        self.verify_found_in_file(
            "CHANGELOG.md",
            "[{0}]: https://github.com/tmarktaylor/phmutest/releases/tag/v{0}\n",
        )

    def test_tool_api(self):
        """Check the version is anywhere in docs/api.md."""
        self.verify_found_in_file("docs/api.md", "API for phmutest version {}\n")

    def test_fixture_api(self):
        """Check the version is anywhere in src/phmutest/fixture.py."""
        self.verify_found_in_file("src/phmutest/fixture.py", "v{} ")
        # This is the 'wrapped' copy.
        self.verify_found_in_file("docs/fixture_py.md", "v{} ")

    def test_mkdocs(self):
        """Check the version is anywhere in mkdocs.yml"""
        self.verify_found_in_file("mkdocs.yml", "site_name: phmutest {}\n")

    def test_setup_cfg(self):
        """Check the version in setup.cfg."""
        config = configparser.ConfigParser()
        config.read("setup.cfg")
        metadata_version = config["metadata"]["version"]
        assert metadata_version == self.package_version

    def test_publish_yml(self):
        """Check the ref: value in the GitHub publish.yml action."""
        self.verify_found_in_file(".github/workflows/publish.yml", "\n  ref: v{}\n")

    def test_pages_yml(self):
        """Check the ref: value in the GitHub pages.yml action."""
        self.verify_found_in_file(".github/workflows/pages.yml", "\n  ref: v{}\n")

    def test_wheel_yml(self):
        """Check the ref: value in the GitHub wheel.yml action."""
        self.verify_found_in_file(".github/workflows/wheel.yml", "\n  version: {}\n")


def test_consistent_copyright():
    """Assure same copyright phrasing in the various source locations."""
    year = 2025
    assert f"Copyright (c) {year}" in Path("LICENSE").read_text(encoding="utf-8")
    assert f"Copyright (c) {year}" in Path("mkdocs.yml").read_text(encoding="utf-8")


def test_trail_spaces_and_only_ascii():  # pragma: no cover
    """Fail if files in repository have non-ASCII or trailing spaces.

    Note- The IDE and/or git may be configurable to prevent trailing spaces
    making this test redundant.
    Non ASCII gets in when cutting and pasting from HTML. Cut from raw rendering.
    """
    completed = subprocess.run(["git", "ls-files"], capture_output=True, text=True)
    files = completed.stdout.splitlines()
    assert files, "No files were checked. Check that a git repos is present."
    found_trailing_spaces = False
    for name in files:
        text = Path(name).read_text(encoding="ASCII")  # just ASCII character codes
        lines = text.splitlines()
        for num, got in enumerate(lines, start=1):
            wanted = got.rstrip()
            if got != wanted:
                print(name, "line", num, "has trailing whitespace.")
                found_trailing_spaces = True
    assert not found_trailing_spaces, "Line has trailing whitespace."


def string_to_dependencies(text: str) -> set:
    """Return the set of pip dependencies from a multi-line string.

    Whitespace and empty lines are not significant.
    Comment lines are ignored.
    """
    lines = text.splitlines()
    lines = [line for line in lines if not line.startswith("#")]
    collapsed_lines = [line.replace(" ", "") for line in lines if line]
    items = set(collapsed_lines) - {""}  # remove an unlikely empty str
    return items


def setup_dependencies(section, option) -> set:
    """Extract set of dependencies from setup.cfg section/option."""
    config = configparser.ConfigParser()
    config.read("setup.cfg", encoding="utf-8")
    text = config.get(section, option)
    return string_to_dependencies(text)


def file_dependencies(filename: str) -> set:
    """Extract set of dependencies from a requirements.txt file."""
    text = Path(filename).read_text(encoding="utf-8")
    return string_to_dependencies(text)


def test_install_requires():
    """setup.cfg install_requires == requirements.txt."""
    setup_values = setup_dependencies("options", "install_requires")
    requirements_values = file_dependencies("requirements.txt")
    assert setup_values == requirements_values


def test_extras_require_color():
    """setup.cfg extras_require:color values are in dev/requirements_dev.txt."""
    requirements_values = file_dependencies("dev/requirements_dev.txt")
    setup_color_values = setup_dependencies("options.extras_require", "color")
    assert setup_color_values.issubset(requirements_values)


def test_extras_require_traceback():
    """setup.cfg extras_require:traceback values are in dev/requirements_dev.txt."""
    requirements_values = file_dependencies("dev/requirements_dev.txt")
    setup_traceback_values = setup_dependencies("options.extras_require", "traceback")
    assert setup_traceback_values.issubset(requirements_values)


def test_extras_require_dev():
    """setup.cfg extras_require:dev values are in dev/requirements_dev.txt."""
    requirements_values = file_dependencies("dev/requirements_dev.txt")
    setup_dev_values = setup_dependencies("options.extras_require", "dev")
    assert setup_dev_values.issubset(requirements_values), f"{setup_dev_values=}"


def test_requirements_inspect():
    """tests/requirements_inspect.txt values are in setup.cfg extras_require:dev."""
    requirements_values = file_dependencies("tests/requirements_inspect.txt")
    setup_dev_values = setup_dependencies("options.extras_require", "dev")
    assert requirements_values.issubset(setup_dev_values)
