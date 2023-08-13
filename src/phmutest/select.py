"""Identify/select/deselect FCBs per info string, test groups and directives."""
import argparse
from dataclasses import dataclass
from pathlib import Path
from typing import List, MutableMapping, Set

import phmutest.fenced
import phmutest.reader
from phmutest.direct import Marker
from phmutest.fenced import FencedBlock, Role


def identify_output_blocks(blocks: List[FencedBlock]) -> None:
    """Guess which are blocks are output.

    The block.info_string is a copy of the Markdown fenced code block info_string.
    This string may indicate the language intended for syntax coloring.
    A block is an output block if it has an empty info_string
    and follows a designated python code block.
    """
    # Install link to output block if one exists.
    previous_block = None
    for block in blocks:
        if previous_block is not None:
            if not block.info_string and previous_block.role == Role.CODE:
                block.set(Role.OUTPUT)
                previous_block.set_link_to_output(block)
        previous_block = block


def apply_skips(skips: List[str], blocks: List[FencedBlock]) -> None:
    """Add command line --skip pattern(s) to CODE and SESSION blocks with matches."""
    # Do skip requests from the command line.
    for block in blocks:
        for pattern in skips:
            if block.contents.find(pattern) > -1:
                block.add_skip_pattern(pattern)


def configure_block_roles(skips: List[str], markdown_file: Path) -> List[FencedBlock]:
    """Find markdown blocks and pair up code and output blocks."""
    docnodes = phmutest.reader.read_markdown(markdown_file)
    blocks = phmutest.fenced.convert(docnodes)
    docnodes.clear()
    identify_output_blocks(blocks)
    skippable_blocks = [b for b in blocks if b.role in [Role.CODE, Role.SESSION]]
    apply_skips(skips, skippable_blocks)
    return blocks


def test_groups(block: FencedBlock) -> Set[str]:
    """Return set of names specified by all the group directives."""
    group_names = [d.value for d in block.directives if d.type == Marker.TEST_GROUP]
    return set(group_names)


def select_blocks(
    args: argparse.Namespace,
    blocks: List[FencedBlock],
    built_from: str,
    deselected: List[str],
) -> List[FencedBlock]:
    """If select/deselect args, apply them to blocks returning selected blocks.

    Blocks that are marked with phmutest-group NAME directives get
    selected/deselected per the --select and --deselect command line options.
    Append the names of deselected blocks to deselected.
    Note that presence of skip directives on a block does not affect select/deselect.
    """
    selecting = set(args.select)
    deselecting = set(args.deselect)
    if selecting or deselecting:
        selected_blocks = []
        for block in blocks:
            if selecting:
                # Select blocks if at least one group in the set selecting.
                if test_groups(block).isdisjoint(selecting):
                    deselected.append(f"{built_from}:{block.line}")
                else:
                    selected_blocks.append(block)

            else:
                assert deselecting, "selecting and deselecting are mutually exclusive"
                # Deselect blocks if at least one group in the set deselecting.
                if test_groups(block).isdisjoint(deselecting):
                    selected_blocks.append(block)
                else:
                    deselected.append(f"{built_from}:{block.line}")
    else:
        selected_blocks = blocks
    return selected_blocks


@dataclass
class FileBlocks:
    """Fenced code blocks selected for testing, all FCBs, .md filename."""

    path: Path
    built_from: str
    selected: List[FencedBlock]
    all_blocks: List[FencedBlock]


class BlockStore:
    """Selected/configured blocks and deselected block locations for many files.

    Identify all fenced code blocks in a Markdown file.
    Identify fenced code blocks that get selected/deselected for testing
    in a Markdown file.
    Keep track of results for later lookup for each file by its path.

    Accumulate a list of de-selected block locations covering all the
    files added to the BlockStore.

    Note that Role.OUTPUT blocks associated with Role.CODE blocks are not
    copied to the FileBlocks.selected list.
    """

    def __init__(self, args: argparse.Namespace):
        """Configure Python example blocks from each file. Select/deselect."""
        self._block_store: MutableMapping[Path, FileBlocks] = {}
        self.deselected_names: List[str] = []
        for path in args.files:
            built_from = path.as_posix()
            all_blocks = configure_block_roles(args.skip, path)
            if args.replmode:
                blocks = [b for b in all_blocks if b.role == Role.SESSION]
            else:
                blocks = [b for b in all_blocks if b.role == Role.CODE]
            selected = select_blocks(args, blocks, built_from, self.deselected_names)
            fileblocks = FileBlocks(path, built_from, selected, all_blocks)
            self._block_store[path] = fileblocks

    def get_blocks(self, path: Path) -> FileBlocks:
        """Return blocks for Markdown file at path."""
        return self._block_store[path]
