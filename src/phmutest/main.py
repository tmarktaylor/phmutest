"""Command line parsing, main entry point, and top level operations."""
import argparse
import pathlib
import sys
from pathlib import Path
from typing import List, Optional, Tuple

import phmutest.cases
import phmutest.code
import phmutest.config
import phmutest.select
import phmutest.session
import phmutest.summary

KnownArgs = Tuple[argparse.Namespace, List[str]]


def existing_path(filename: str) -> Path:
    """Return Path object constructed from filename, check that the file exists."""
    path = Path(filename)
    if not path.exists():
        raise argparse.ArgumentTypeError(f"File {filename} not found.")
    return path


def main_argparser() -> argparse.ArgumentParser:
    """Create argument parser."""
    parser = argparse.ArgumentParser(
        prog="phmutest",
        description=(
            "Detect broken Python examples in Markdown."
            " Accepts relevant unittest options."
        ),
    )

    parser.add_argument(
        "--version",
        action="version",
        version=f"{parser.prog} {phmutest.__version__}",
    )

    parser.add_argument(
        "files",
        help="Markdown input file.",
        metavar="FILE",
        nargs="*",
        type=existing_path,
    )

    parser.add_argument(
        "--skip",
        help="Any block that contains the substring TEXT is not tested.",
        metavar="TEXT",
        action="extend",
        default=[],
        nargs="*",
    )

    parser.add_argument(
        "--fixture",
        help="Function run before testing.",
        metavar="DOTTED_PATH.FUNCTION",
        type=pathlib.Path,
    )

    parser.add_argument(
        "--share-across-files",
        help="Shares names from Markdown file to later positional files.",
        metavar="FILE",
        default=[],
        nargs="*",
        type=existing_path,
    )

    parser.add_argument(
        "--setup-across-files",
        help="Apply Markdown file setup blocks to files.",
        metavar="FILE",
        default=[],
        nargs="*",
        type=existing_path,
    )

    parser_group = parser.add_mutually_exclusive_group()
    parser_group.add_argument(
        "--select",
        help="Select all blocks with phmutest-group GROUP directive for testing.",
        metavar="GROUP",
        default=[],
        nargs="*",
    )

    parser_group.add_argument(
        "--deselect",
        help="Exclude all blocks with phmutest-group GROUP directive from testing.",
        metavar="GROUP",
        default=[],
        nargs="*",
    )

    parser.add_argument(
        "--config",
        help=".toml configuration file.",
        metavar="TOMLFILE",
        type=existing_path,
    )

    parser.add_argument(
        "--replmode",
        help="Test Python interactive sessions.",
        default=False,
        action="store_true",
    )

    parser.add_argument(
        "-g",
        "--generate",
        help=("Write generated Python or docstring to output file or stdout."),
        metavar="OUTFILE",
        type=argparse.FileType("w", encoding="utf-8"),
    )

    parser.add_argument(
        "--progress",
        help="Print block by block test progress. File by file in --replmode.",
        default=False,
        action="store_true",
    )

    parser.add_argument(
        "--sharing",
        help="For these files print name sharing. . means all files.",
        metavar="FILE",
        default=[],
        nargs="*",
        type=existing_path,
    )

    parser.add_argument(
        "--log",
        help="Print log items when done.",
        default=False,
        action="store_true",
    )

    parser.add_argument(
        "--summary",
        help="Print test count and skipped tests.",
        default=False,
        action="store_true",
    )

    parser.add_argument(
        "--report",
        help="Print fenced code block configuration, deselected blocks.",
        default=False,
        action="store_true",
    )
    return parser


def check_across_files(args: argparse.Namespace) -> None:
    """Avoid hard to troubleshoot KeyError in phmutest.select.get_blocks()."""
    for f in args.share_across_files:
        assert (
            f in args.files
        ), f"{f} in share-across-files must also be positional argument."
    for f in args.setup_across_files:
        assert (
            f in args.files
        ), f"{f} in setup-across-files must also be positional argument."


def remove_duplicate_files(args: argparse.Namespace) -> None:
    """Remove duplicate positional args files. Modifies in place."""
    unique_files = []
    for f in args.files:
        if f not in unique_files:
            unique_files.append(f)
    args.files = unique_files
    assert len(args.files) == len(set(args.files)), "no duplicates"


def generate_and_run(known_args: KnownArgs) -> Optional[phmutest.summary.PhmResult]:
    """Check args, delete duplicate files, read FCBs, call a test runner."""

    args = known_args[0]
    if args.config:
        phmutest.config.process_config_file(args)
    check_across_files(args)
    remove_duplicate_files(args)

    # Find, process, and select/deselect Python fenced code blocks.
    block_store = phmutest.select.BlockStore(args)
    if args.report:
        print("Command line plus --config file args:")
        phmutest.summary.show_args(args)
        for path in args.files:
            fileblocks = block_store.get_blocks(path)
            print(f"\nFenced blocks from {fileblocks.built_from}:")
            for block in fileblocks.all_blocks:
                print(block)
        print("\nDeselected blocks:")
        for location in block_store.deselected_names:
            print(location)
        return None

    if args.generate:
        if args.replmode:
            _ = phmutest.session.run_repl(args, known_args[1], block_store)
        else:
            text = phmutest.cases.testfile(args, block_store)
            text = text.rstrip()
            args.generate.write(text + "\n")
            args.generate.close()
        return None

    if args.replmode:
        phmresult = phmutest.session.run_repl(args, known_args[1], block_store)
    else:
        num_deselected_names = len(block_store.deselected_names)
        text = phmutest.cases.testfile(args, block_store)
        phmresult = phmutest.code.run_code(
            args, known_args[1], num_deselected_names, text
        )
    phmutest.summary.show_results(args, phmresult)
    return phmresult


def main(argv: Optional[List[str]] = None) -> Optional[phmutest.summary.PhmResult]:
    """For call from Python that does not call sys.exit()."""
    parser = main_argparser()
    known_args = parser.parse_known_args(argv)
    return generate_and_run(known_args)


def entry_point(argv: Optional[List[str]] = None) -> None:
    """Entry point for command line invocation."""
    phmresult = main(argv)
    if phmresult is not None:
        sys.exit(not phmresult.is_success)
    else:
        sys.exit(0)
