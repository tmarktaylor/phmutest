"""Show type information is packaged for distribution. Run mypy on this file."""

from typing import List

import phmutest.fenced
import phmutest.reader
import phmutest.tool


def test_mypy_likes_fenced_code_blocks() -> None:
    """Compile time use of fenced_code_blocks() to be type checked by mypy."""
    blocks: List[phmutest.fenced.FencedBlock] = []
    blocks = phmutest.tool.fenced_code_blocks("tests/md/example1.md")
    assert len(blocks) > 0


def test_mypy_likes_fenced_block_nodes() -> None:
    """Compile time use of fenced_block_nodes() to be type checked by mypy."""
    nodes: List[phmutest.reader.DocType] = []
    nodes = phmutest.reader.fcb_nodes("tests/md/example1.md")
    assert len(nodes) > 0
