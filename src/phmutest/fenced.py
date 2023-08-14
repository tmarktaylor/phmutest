"""Fenced code block data structures."""

import re
import textwrap
from enum import Enum
from typing import List, Optional

import phmutest.direct
import phmutest.reader


class PythonMatcher:
    """RE to check beginning of FCB info string to see if Python.

    The info string can continue beyond the end of the matching pattern.
    The matching text is discarded.
    """

    def __init__(self) -> None:
        self.python_patterns = [
            r"^python( |$)",
            r"^py( |$)",
            r"^py3( |$)",
            r"python3( |$)",
            r"pycon( |$)",
            r"^[{].*?[.]python.*?[}]( |$)",
        ]
        """List of re patterns applied to FCB info_string to identify Python."""
        self.compile()

    def compile(self) -> None:
        self.re = re.compile("|".join(self.python_patterns))


# This is a designated patch point. Developers: Please treat this as if it were an API.
# To patch:
# - Create new instance of PythonMatcher.
# - Modify the patterns attribute.
# - Call compile().
# - with mock.patch("phmutest.fenced.python_matcher", <the new instance>):
# - See example in tests/test_patching.py.
python_matcher = PythonMatcher()


class Role(Enum):
    """Role that markdown fenced code block plays in testing."""

    NOROLE = "--"
    CODE = "code"
    OUTPUT = "output"
    SESSION = "session"


class FencedBlock:
    """Markdown fenced code block, test role, and its HTML comment directives."""

    def __init__(self, node: phmutest.reader.DocNode) -> None:
        """Initialize from document fenced code block node."""
        self.info_string = node.info_string
        self.line = node.line
        self.end_line = node.end_line
        self.role = Role.NOROLE
        self.contents = node.payload  # type: str
        if python_matcher.re.match(self.info_string):
            if self.contents.startswith(">>> "):
                self.role = Role.SESSION
            else:
                self.role = Role.CODE
        self.output = None  # type: Optional["FencedBlock"]
        self.skip_patterns = []  # type: List[str]
        self.directives = phmutest.direct.get_directives(node)
        self._directive_markers = set(d.type for d in self.directives)

    def __str__(self) -> str:
        info_string = (" " + self.info_string) if self.info_string else ""
        if self.role == Role.OUTPUT:
            lines = [
                "FencedBlock:",
                f"  info_string={info_string}",
                f"  lines= {self.line}-{self.end_line}",
                f"  role= {self.role}",
            ]
        else:
            if self.output is not None:
                has_output = f"lines {self.output.line}-{self.output.end_line}"
            else:
                has_output = "no"
            lines = [
                "FencedBlock:",
                f"  info_string={info_string}",
                f"  lines= {self.line}-{self.end_line}",
                f"  role= {self.role}",
                f"  output block= {has_output}",
            ]
        if self.skip_patterns:
            quoted_patterns = [repr(p) for p in self.skip_patterns]
            lines.append("  skip patterns= " + ", ".join(quoted_patterns))

        if self.directives:
            lines.append("  directives: (line, type, HTML):")
            ds = [f"{d.line}, {d.type.name}, {d.literal}" for d in self.directives]
            lines.append(textwrap.indent("\n".join(ds), "    "))
        else:
            lines.append("  directives= []")
        return "\n".join(lines)

    def set(self, role: Role) -> None:
        """Set the role for the fenced code block in subsequent testing."""
        self.role = role

    def set_link_to_output(self, fenced_block: "FencedBlock") -> None:
        """Save a reference to the code block's output block."""
        assert self.role == Role.CODE, "only allowed to be code"
        assert fenced_block.role == Role.OUTPUT, "only allowed to be output"
        self.output = fenced_block

    def get_output_contents(self) -> str:
        """Return contents of linked output block or empty str if no link."""
        assert self.output, "Must be called on a block with Role.OUTPUT"
        return self.output.contents

    def add_skip_pattern(self, pattern: str) -> None:
        """Keep track of the skip pattern. Valid for CODE and SESSION."""
        assert self.role in [Role.CODE, Role.SESSION]
        if pattern not in self.skip_patterns:
            self.skip_patterns.append(pattern)

    def get_directive(
        self, *markers: phmutest.direct.Marker
    ) -> Optional[phmutest.direct.Directive]:
        """Return the value of first directive of type any of markers or None."""
        for directive in self.directives:
            if directive.type in markers:
                return directive
        return None

    def has_directive(self, marker: phmutest.direct.Marker) -> bool:
        """Return true if block has a directive of type marker."""
        return marker in self._directive_markers


def convert(nodes: List[phmutest.reader.DocNode]) -> List[FencedBlock]:
    """Create FencedBlock objects from DocNode."""
    blocks = []
    for node in nodes:
        if node.ntype == phmutest.reader.NodeType.FENCED_CODE_BLOCK:
            blocks.append(FencedBlock(node))
    return blocks
