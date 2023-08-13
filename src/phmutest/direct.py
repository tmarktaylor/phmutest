"""Find phmutest Directives in HTML comment Nodes."""
import re
from dataclasses import dataclass
from enum import Enum, auto
from typing import List, Optional

import phmutest.reader
from phmutest.reader import NodeType


class Marker(Enum):
    """The kind of special HTML comment directive before a fenced code block."""

    SKIP = auto()
    SKIPIF_PYVERSION = auto()
    LABEL = auto()
    SETUP = auto()
    TEARDOWN = auto()
    TEST_GROUP = auto()


@dataclass
class MarkerPattern:
    """Marker and the re pattern that detects it in a HTML comment."""

    marker: Marker
    pattern: str  # regular expression pattern

    def __post_init__(self) -> None:
        self.reobj = re.compile(self.pattern)


# This is a designated patch point. Developers: Please treat this as if it were an API.
# Use this to detect aliases that will behave like the directives here.
# To patch:
# - Create a copy of directive_finders.
# - Add or remove items. Add items for aliases.  Items must be type
#   MarkerPattern where marker is one of the existing Marker enumerations.
# - with mock.patch("phmutest.direct.directive_finders", <the new instance>):
# - See example in tests/test_patching.py.
directive_finders = [
    #
    # Handle these Markdown directives from the PYPI phmdoctest project.
    #
    MarkerPattern(Marker.SKIP, r"(<!--phmdoctest-skip-->)$"),
    MarkerPattern(Marker.SKIP, r"(<!--phmdoctest-mark[.]skip-->)$"),
    MarkerPattern(
        Marker.SKIPIF_PYVERSION,
        r"(<!--phmdoctest-mark.skipif<3[.](?P<value>[1-9][0-9]*)-->)$",
    ),
    MarkerPattern(Marker.LABEL, r"(<!--phmdoctest-label (?P<value>.*?)-->)$"),
    MarkerPattern(Marker.SETUP, r"(<!--phmdoctest-setup-->)$"),
    MarkerPattern(Marker.TEARDOWN, r"(<!--phmdoctest-teardown-->)$"),
    # for mark.ATTRIBUTE note substring mark.skip is not matched.
    MarkerPattern(
        Marker.TEST_GROUP, r"(<!--phmdoctest-mark[.](?!skip)(?P<value>.*?)-->)$"
    ),
    #
    # These are the directives for phmutest.
    #
    MarkerPattern(Marker.SKIP, r"(<!--phmutest-skip-->)$"),
    MarkerPattern(
        Marker.SKIPIF_PYVERSION,
        r"(<!--phmutest-skipif<3[.](?P<value>[1-9][0-9]*)-->)$",
    ),
    MarkerPattern(Marker.LABEL, r"(<!--phmutest-label (?P<value>.*?)-->)$"),
    MarkerPattern(Marker.SETUP, r"(<!--phmutest-setup-->)$"),
    MarkerPattern(Marker.TEARDOWN, r"(<!--phmutest-teardown-->)$"),
    MarkerPattern(Marker.TEST_GROUP, r"(<!--phmutest-group (?P<value>.*?)-->)$"),
]


@dataclass
class Directive:
    """A phmutest directive taken from a HTML comment."""

    type: Marker
    value: str  # String value. Empty string if no value.
    line: int  # line number in file
    literal: str  # The HTML comment.


def find_one_directive(node: phmutest.reader.DocNode) -> Optional[Directive]:
    """Get a Directive instance from a HTML comment, if present."""
    assert node.ntype == NodeType.HTML_COMMENT, "Must be HTML"

    for finder in directive_finders:
        if match := finder.reobj.match(node.payload):
            value = match.groupdict().get("value", "")
            return Directive(
                type=finder.marker,
                value=value,
                line=node.line,
                literal=node.payload,
            )
    return None


def get_directives(node: phmutest.reader.DocNode) -> List[Directive]:
    """Scan adjacent preceding HTML comments for directives."""

    # The scan looks backward in the document.
    # Back links exist only if the preceding node is adjacent to
    # the current node.
    # The scan spans runs of HTML comments and single blank lines.
    # Two consectutive blank lines will stop the scan.
    # If the comment is a known directive a Directive instance
    # is assembled and added to a list.
    # This list is reversed so that the Directive(s) are in file order.
    # If no directives are found an empty list is returned.
    assert node.ntype == NodeType.FENCED_CODE_BLOCK, "must be FCB"
    directives = list()
    curr_ntype = None
    prev = node.backlink
    while prev is not None and (
        (prev.ntype == NodeType.BLANK_LINE) or (prev.ntype == NodeType.HTML_COMMENT)
    ):
        # Stop scan at two consecutive blank lines.
        if (curr_ntype == NodeType.BLANK_LINE) and (prev.ntype == NodeType.BLANK_LINE):
            break
        if prev.ntype == NodeType.HTML_COMMENT:
            one = find_one_directive(prev)
            if one:
                directives.append(one)
        curr_ntype = prev.ntype
        prev = prev.backlink

    directives.reverse()
    return directives
