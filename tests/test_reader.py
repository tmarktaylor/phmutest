"""Test reading Markdown - reader.py."""
from pathlib import Path

import phmutest.reader
from phmutest.reader import NodeType


def show_node(node):
    print(node.line, node.ntype)
    if node.payload:
        print(repr(node.payload))


def show_file_nodes(filename):
    """Helper to show the DocNode values during test development."""
    nodes = phmutest.reader.read_markdown(Path(filename))
    for node in nodes:
        show_node(node)
        print("-" * 40)


class TestReader:
    """Check DocNode read from a Markdown file."""

    def setup_method(self):
        self.nodes = phmutest.reader.read_markdown(Path("tests/md/reader.md"))

    def test_num_nodes(self):
        assert len(self.nodes) == 13

    def test_backlinks(self):
        assert self.nodes[0].backlink is None
        assert self.nodes[1].backlink == self.nodes[0]
        assert self.nodes[2].backlink is None
        assert self.nodes[3].backlink == self.nodes[2]
        assert self.nodes[4].backlink == self.nodes[3]
        assert self.nodes[5].backlink == self.nodes[4]
        assert self.nodes[8].backlink is None
        assert self.nodes[9].backlink is None
        assert self.nodes[10].backlink == self.nodes[9]
        assert self.nodes[11].backlink == self.nodes[10]
        assert self.nodes[12].backlink == self.nodes[11]

    def test_blank_line(self):
        assert self.nodes[0].ntype == NodeType.BLANK_LINE
        assert self.nodes[0].payload == ""
        assert self.nodes[1].ntype == NodeType.BLANK_LINE
        assert self.nodes[1].line == 4
        assert self.nodes[1].end_line == 4
        assert self.nodes[6].ntype == NodeType.BLANK_LINE
        assert self.nodes[6].info_string == ""

    def test_html_comment(self):
        assert self.nodes[2].ntype == NodeType.HTML_COMMENT
        assert self.nodes[3].ntype == NodeType.HTML_COMMENT
        assert self.nodes[4].ntype == NodeType.HTML_COMMENT
        assert self.nodes[4].line == 10
        assert self.nodes[4].end_line == 10
        assert self.nodes[4].info_string == ""
        # HTML comment around an FCB
        assert self.nodes[7].ntype == NodeType.HTML_COMMENT
        # indented HTNL comments
        assert self.nodes[10].ntype == NodeType.HTML_COMMENT
        assert self.nodes[11].ntype == NodeType.HTML_COMMENT
        assert self.nodes[12].ntype == NodeType.HTML_COMMENT
        # comment indentation is stripped from payload
        assert self.nodes[12].payload == "<!-- indent 3 blanks html comment -->"
        assert self.nodes[12].line == 38

    def test_fenced_code_block(self):
        assert self.nodes[5].ntype == NodeType.FENCED_CODE_BLOCK
        assert self.nodes[5].line == 11
        assert self.nodes[5].end_line == 13
        assert self.nodes[5].payload == "assert False\n"

        # blank lines inside an FCB
        assert self.nodes[8].ntype == NodeType.FENCED_CODE_BLOCK
        assert self.nodes[8].line == 21
        assert self.nodes[8].end_line == 25
        assert self.nodes[8].payload == "\nassert False\n\n"

        # tilde start fence enclosing backtick
        assert self.nodes[9].ntype == NodeType.FENCED_CODE_BLOCK
        assert self.nodes[9].line == 27
        assert self.nodes[9].end_line == 35
        assert self.nodes[9].payload == "\n```python\n\nassert False\n\n```\n\n"


class TestReaderFcb:
    """Check FCB DocNode read from a Markdown file."""

    def setup_method(self):
        self.nodes = phmutest.reader.read_markdown(Path("tests/md/readerfcb.md"))

    def test_num_nodes(self):
        assert len(self.nodes) == 15
        assert self.nodes[0].backlink is None

    def test_fences(self):
        assert self.nodes[0].ntype == NodeType.HTML_COMMENT
        assert self.nodes[1].ntype == NodeType.FENCED_CODE_BLOCK
        assert self.nodes[2].ntype == NodeType.FENCED_CODE_BLOCK
        assert self.nodes[3].ntype == NodeType.FENCED_CODE_BLOCK
        assert self.nodes[4].ntype == NodeType.FENCED_CODE_BLOCK
        assert self.nodes[5].ntype == NodeType.FENCED_CODE_BLOCK
        assert self.nodes[6].ntype == NodeType.FENCED_CODE_BLOCK
        assert self.nodes[7].ntype == NodeType.FENCED_CODE_BLOCK
        assert self.nodes[7].line == 36
        assert self.nodes[7].end_line == 38
        assert self.nodes[8].ntype == NodeType.HTML_COMMENT
        assert self.nodes[8].line == 52
        assert self.nodes[8].end_line == 52
        assert self.nodes[9].ntype == NodeType.FENCED_CODE_BLOCK
        assert self.nodes[10].ntype == NodeType.FENCED_CODE_BLOCK
        assert self.nodes[10].end_line == 60
        assert self.nodes[11].ntype == NodeType.BLANK_LINE
        assert self.nodes[12].ntype == NodeType.BLANK_LINE
        # The next 2 FCBs are between <deails> and </details>.
        assert self.nodes[13].ntype == NodeType.FENCED_CODE_BLOCK
        assert self.nodes[14].ntype == NodeType.FENCED_CODE_BLOCK
        assert self.nodes[14].end_line == 69

    def test_payload(self):
        assert self.nodes[3].payload == "~~~python\nassert very small rocks\n~~~\n"
        assert self.nodes[3].line == 16
        assert self.nodes[3].end_line == 20

    def test_info_string(self):
        assert self.nodes[9].ntype == NodeType.FENCED_CODE_BLOCK
        assert self.nodes[9].info_string == "python"
        assert self.nodes[10].ntype == NodeType.FENCED_CODE_BLOCK
        assert self.nodes[10].info_string == "python extra stuff"
        assert self.nodes[10].line == 58
        assert self.nodes[10].end_line == 60
