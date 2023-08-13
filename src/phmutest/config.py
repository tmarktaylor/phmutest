"""Read values from [tool.phmuttest] table in a .toml document.

    Only these keys can be configured:
        include-globs
        exclude-globs
        share-across-files
        setup-across-files
        fixture
        select
        deselect
    Command positional FILEs extend configured files list.
    For all other keys, if also present as command line options
    the command line options take precedence.
    These cannot be configured:
          --replmode,
          --generate, --progress, --sharing,
          --log, --summary, --report
"""
import argparse
from pathlib import Path
from typing import List

try:
    import tomllib  # type: ignore
except ModuleNotFoundError:
    import tomli as tomllib


def existing_file(filename: str, config_name: str) -> Path:
    """Return Path object constructed from filename, check that the file exists."""
    path = Path(filename)
    if not path.exists():
        raise ValueError(f"In {config_name} {filename} not found.")
    return path


def select_files(include_globs: List[str], exclude_globs: List[str]) -> List[Path]:
    """Process config file globs to make list of existing Paths of files to test."""
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


def process_config_file(args: argparse.Namespace) -> argparse.Namespace:
    """Rewrite args using values from the .toml configuration file."""
    config_name = args.config.as_posix()
    with open(args.config, "rb") as f:
        toml_config = tomllib.load(f)
    section = toml_config["tool"]["phmutest"]

    # Resolve globs into a list of existing paths.
    include_globs = section.get("include-globs", [])
    exclude_globs = section.get("exclude-globs", [])
    selected = select_files(include_globs, exclude_globs)

    # Rewrite args.files inserting files selected by the configuration file first.
    args.files = selected + args.files

    # Configuration is superceded by command line args.
    if not args.skip:
        args.skip = section.get("skip", [])

    if not args.share_across_files:
        names = section.get("share-across-files", [])
        paths = [existing_file(n, config_name) for n in names]
        args.share_across_files = paths

    if not args.setup_across_files:
        names = section.get("setup-across-files", [])
        paths = [existing_file(n, config_name) for n in names]
        args.setup_across_files = paths

    if not args.fixture:
        fixture = section.get("fixture", None)
        if fixture:
            # fixture is not a Path to an existing file, so do not validate.
            args.fixture = Path(fixture)

    # --select and --deselect are mutually exclusive- It is an error
    # if they are both specified on the command line.  The same situation
    # applies to the .toml file.
    if not args.select:
        args.select = section.get("select", [])

    if not args.deselect:
        args.deselect = section.get("deselect", [])

    if args.select and args.deselect:
        raise ValueError(f"In {config_name} non-empty deselect not allowed with select")

    return args
