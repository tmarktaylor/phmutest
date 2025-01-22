"""Determine settings from caller's known args and config file.

Read values from [tool.phmuttest] table in a .toml document.

    Only these keys can be configured:
        include-globs
        exclude-globs
        share-across-files
        setup-across-files
        runpytest
        fixture
        select
        deselect
        color
        style
        pytest_command
    Command positional FILEs extend configured files list.
    For all other keys, if also present as command line options
    the command line options take precedence.
    These cannot be configured:
          --replmode,
          --generate, --progress, --sharing,
          --log, --summary, --stdout, --report
"""

import argparse
import sys
from dataclasses import dataclass
from pathlib import Path
from typing import List, Optional, Tuple

import phmutest.syntax

if sys.version_info >= (3, 11):
    import tomllib
else:
    import tomli as tomllib


KnownArgs = Tuple[argparse.Namespace, List[str]]


RUNPYTEST_CHOICES = ["only", "on-error"]
"""Choices for runpytest key."""


PYTEST_COMMAND = "pytest -vv"
"""Command line to invoke pytest."""


@dataclass
class Settings:
    args: argparse.Namespace
    extra_args: List[str]
    pytest_command: str
    highlighter: phmutest.syntax.Highlighter


def get_settings(known_args: KnownArgs) -> Settings:
    """Determine settings from caller's known args and config file."""
    args = known_args[0]
    args, pytest_command = process_config_file(args)
    check_across_files(args)
    remove_duplicate_files(args)
    check_disallowed(args)
    highlighter: phmutest.syntax.Highlighter = phmutest.syntax.Highlighter(
        style=args.style
    )
    return Settings(
        args=args,
        extra_args=known_args[1],
        pytest_command=pytest_command,
        highlighter=highlighter,
    )


def check_across_files(args: argparse.Namespace) -> None:
    """Avoid hard to troubleshoot KeyError in phmutest.select.get_blocks()."""
    for f in args.share_across_files:
        if f not in args.files:
            raise ValueError(
                f"{f} in share-across-files must also be positional argument."
            )
    for f in args.setup_across_files:
        if f not in args.files:
            raise ValueError(
                f"{f} in setup-across-files must also be positional argument."
            )


def remove_duplicate_files(args: argparse.Namespace) -> None:
    """Remove duplicate positional args files. Modifies in place."""
    unique_files = []
    for f in args.files:
        if f not in unique_files:
            unique_files.append(f)
    args.files = unique_files


def check_disallowed(args: argparse.Namespace) -> None:
    """Point out combinations of args that don't make sense."""
    if args.runpytest and args.replmode:
        print("--runpytest has no effect when used with --replmode.")


class ConfigSection:
    """Get settings from TOML config file, update command line args."""

    def __init__(self, args: argparse.Namespace):
        """Fetch tool.phmutest section."""
        self.config_filename = args.config.as_posix()
        with open(args.config, "rb") as f:
            toml_config = tomllib.load(f)
        self.section = toml_config["tool"]["phmutest"]

    def get_string_key(self, key: str, default: str = "") -> Optional[str]:
        """Return key's value or None if key is empty string or key does not exist.

        If default is truthy, return it instead of None.
        """
        value = self.section.get(key, None)
        if value:
            return str(value)  # avoid mypy nag
        elif default:
            return default
        else:
            return None

    def select_files(self) -> List[Path]:
        """Resolve globs into a list of existing paths."""
        include_globs = self.section.get("include-globs", [])
        exclude_globs = self.section.get("exclude-globs", [])
        working_directory = Path(".")  # current working directory
        included: List[Path] = []
        for glob in include_globs:
            included.extend(working_directory.glob(glob))

        excluded: List[Path] = []
        for glob in exclude_globs:
            excluded.extend(working_directory.glob(glob))

        selected: List[Path] = []
        for keeper in included:
            if keeper in excluded:
                continue
            selected.append(keeper)
        return selected

    def get_paths(self, key: str) -> List[Path]:
        """Get list of existing paths at the config file section key."""
        names = self.section.get(key, [])
        return [self.existing_file(n, self.config_filename) for n in names]

    @staticmethod
    def existing_file(filename: str, config_name: str) -> Path:
        """Return Path object constructed from filename, check that the file exists."""
        path = Path(filename)
        if not path.exists():
            raise ValueError(f"In {config_name} {filename} not found.")
        return path

    # --select and --deselect are mutually exclusive- It is an error
    # if they are both specified on the command line.  The code here
    # checks for the same situation caused by presence of keys
    # in the .toml file. Note this will catch an args item combined with
    # a toml section since the updated args values are checked.
    def validate_select_and_deselect(
        self, select: List[Path], deselect: List[Path]
    ) -> None:
        """Check for dis-allowed settings."""
        if select and deselect:
            raise ValueError(
                f"In {self.config_filename} non-empty deselect not allowed with select"
            )

    def get_fixture_path(self) -> Optional[Path]:
        """Get the fixture key and convert a truthy value to a Path."""
        # fixture is not a Path to an existing file, so no exists check.
        fixture = self.get_string_key("fixture")
        if fixture:
            return Path(fixture)
        else:
            return None

    def get_runpytest_choice(self) -> Optional[str]:
        """Get runpytest key, if present it must be one of choices."""
        runpytest: Optional[str] = self.get_string_key("runpytest")
        if runpytest is not None:
            if runpytest not in RUNPYTEST_CHOICES:
                raise ValueError(f"{runpytest} must be one of {RUNPYTEST_CHOICES}")
        return runpytest


def process_config_file(
    args: argparse.Namespace,
) -> Tuple[argparse.Namespace, str]:
    """Rewrite args using values from the .toml configuration file."""
    if not args.config:
        return args, PYTEST_COMMAND
    toml = ConfigSection(args)
    section = toml.section  # rename

    # Resolve globs into a list of existing paths.
    # Rewrite args.files inserting files selected by the configuration file first.
    selected = toml.select_files()
    args.files = selected + args.files

    # Configuration is superseded by command line args.
    args.skip = args.skip or section.get("skip", [])
    args.share_across_files = args.share_across_files or toml.get_paths(
        "share-across-files"
    )
    args.setup_across_files = args.setup_across_files or toml.get_paths(
        "setup-across-files"
    )
    args.fixture = args.fixture or toml.get_fixture_path()
    args.runpytest = args.runpytest or toml.get_runpytest_choice()
    args.color = args.color or section.get("color", False)
    args.style = args.style or toml.get_string_key("style")
    args.select = args.select or section.get("select", [])
    args.deselect = args.deselect or section.get("deselect", [])
    toml.validate_select_and_deselect(args.select, args.deselect)
    pytest_command = toml.get_string_key("pytest_command", PYTEST_COMMAND)
    assert pytest_command is not None  # avoid mypy nag
    return args, pytest_command
