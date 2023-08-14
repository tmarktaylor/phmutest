"""Show type information is packaged for distribution. Run mypy on this file."""

from typing import List

import phmutest.fenced
import phmutest.reader
import phmutest.tool


def test_mypy_likes_imported_types() -> None:
    """Compile time use of imported types to be type checked by mypy."""
    nodes: List[phmutest.reader.DocNode] = []
    nodes = phmutest.reader.fcb_nodes("tests/md/example1.md")
    assert len(nodes) > 0

    blocks: List[phmutest.fenced.FencedBlock] = []
    blocks = phmutest.fenced.convert(nodes)
    assert len(blocks) > 0
