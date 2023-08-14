"""Produce nodes describing elements of interest in Markdown.

Produce a DocNode for each non-overlapping HTML comment, fenced code block,
and blank line.
"""

import re
from enum import Enum
from pathlib import Path
from typing import Any, List, Optional


class NodeType(Enum):
    """Type of Markdown document element."""

    BLANK_LINE = 1
    FENCED_CODE_BLOCK = 2
    HTML_COMMENT = 3


class DocNode:
    """Information about a NodeType identified in the Markdown document."""

    def __init__(self, match: Any):
        # Using Any annotation here since re.Match[str] does not work on Python 3.8.
        # Detect the NodeType.
        if match["blank"] is not None:
            self.ntype = NodeType.BLANK_LINE
        elif match["comment"] is not None:
            self.ntype = NodeType.HTML_COMMENT
        else:
            assert match["fcb"] is not None, "sanity check"
            self.ntype = NodeType.FENCED_CODE_BLOCK
        self.startpos = match.start()
        self.endpos = match.end()
        if self.ntype == NodeType.HTML_COMMENT:
            self.payload = match["comment"]
        else:
            self.payload = ""
        if self.ntype == NodeType.FENCED_CODE_BLOCK:
            self.info_string = match["info_string"].strip()
            self.payload = match["contents"]
            if match["indent"]:
                self.payload = self.dedent(match["indent"], match["contents"])
            else:
                self.payload = match["contents"]

        else:
            self.info_string = ""
            self.contents = ""
        self.backlink: Optional[DocNode] = None
        self.line = 0
        self.end_line = 0

    def set_backlink(self, other: "DocNode") -> None:
        """Set a link to a preceeding DocNode."""
        self.backlink = other

    def set_line_numbers(self, start_line: int, end_line: int) -> None:
        """Set the DocNode's line number span in the Markdown document."""
        self.line = start_line
        self.end_line = end_line

    @staticmethod
    def dedent(indent: str, contents: str) -> str:
        """De-indent FCB lines. All lines and fences assumed to have the indent."""
        dedented = []
        lines = contents.splitlines()
        for line in lines:
            line = line.replace(indent, "", 1)
            dedented.append(line)
        return "\n".join(dedented) + "\n"


class PositionToLineNumber:
    """Given position in multiline string determine the line number."""

    def __init__(self, text: str):
        """Initialize the position to line number mapping."""
        self.maxpos = len(text)
        self.mapping = {}
        pos = 0
        for num, text_line in enumerate(text.splitlines(), start=1):
            self.mapping[pos] = num  # start of line
            pos += len(text_line)
            self.mapping[pos] = num  # end of line
            pos += 1

    def get_line(self, position: int) -> int:
        """Return the line number that contains character position in the file."""
        assert position <= (
            self.maxpos
        ), f"must not be a lot beyond EOF {position}/{self.maxpos}."
        while position > 0:
            if position not in self.mapping:
                position -= 1
            else:
                return self.mapping[position]
        return 1


def read_markdown(markdown_path: Path) -> List[DocNode]:
    """From Markdown return list of DocNode except for trailing blank lines."""
    text = markdown_path.read_text(encoding="utf-8")

    fcb = (
        r"^(?P<fcb>(?P<indent> {0,3})"
        # openfence-
        # 3 or more consecutive tilde or backtick.
        r"((?P<tilde>[\~]{3,})|(?P<backtick>[`]{3,}))"
        #
        r"(?P<info_string>.*?)[\n](?P<contents>.*?)"
        # closefence-
        # Indent up to 3.
        # Tilde open fence + 0 or more tilde OR
        # backtick open fence + 0 or more backtick OR
        # end of file.
        r"(^ {0,3}((?P=tilde)[\~]*$|(?P=backtick)[`]*$)|\Z)"
        #
        r")"
    )
    blank = r"^(?P<blank>[ \t]*)$"
    comment = r"^ {0,3}(?P<comment><!--.*?-->)$"
    node_pattern = "|".join([comment, fcb, blank])

    nodefinder = re.finditer(
        pattern=node_pattern, string=text, flags=re.MULTILINE | re.DOTALL
    )
    nodes = [DocNode(m) for m in nodefinder]

    # throw out the trailing blank lines.
    while nodes and nodes[-1].ntype == NodeType.BLANK_LINE:
        _ = nodes.pop()

    # install line numbers
    position_map = PositionToLineNumber(text)
    for n in nodes:
        n.set_line_numbers(
            start_line=position_map.get_line(n.startpos),
            end_line=position_map.get_line(n.endpos),
        )

    # install back link if previous node is adjacent to the current one.
    if nodes:
        prev = nodes[0]
        for n in nodes[1:]:
            if prev.endpos + 1 == n.startpos:
                n.set_backlink(prev)
            prev = n

    for node in nodes:
        post(node)
    return nodes


def fcb_nodes(markdown_filename: str) -> List[DocNode]:
    """From Markdown return list of the DocNode of type NodeType.FENCED_CODE_BLOCK."""
    fcbs = []
    for node in read_markdown(Path(markdown_filename)):
        if node.ntype == NodeType.FENCED_CODE_BLOCK:
            fcbs.append(node)
    return fcbs


# This is a designated patch point. Developers: Please treat this as if it were an API.
# Use this to modify the DocNode. See examples in tests/test_patching.py.
# To patch:
# - Create a function with the same signature as post(), for example, mypost().
# - with mock.patch("phmutest.reader.post", mypost):
def post(node: DocNode) -> None:
    """Patch point called for each DocNode before read_markdown() returns."""
    pass
