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
    Text surronding the x.y.z version number may be tested as well.
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

    def test_recent_changes(self):
        """Check the version is anywhere in recent_changes.md."""
        self.verify_found_in_file("docs/recent_changes.md", "{} - ")

    def test_tool_api(self):
        """Check the version is anywhere in docs/api.md."""
        self.verify_found_in_file("docs/api.md", "API version {}\n")

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

    def test_wheel_yml(self):
        """Check the ref: value in the GitHub wheel.yml action."""
        self.verify_found_in_file(".github/workflows/wheel.yml", "\n  version: {}\n")


def test_consistent_copyright():
    """Assure same copyright phrasing in the various source locations."""
    year = 2023
    assert f"Copyright (c) {year}" in Path("LICENSE").read_text(encoding="utf-8")
    assert f"Copyright (c) {year}" in Path("mkdocs.yml").read_text(encoding="utf-8")


def test_trail_spaces_and_only_ascii():
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
