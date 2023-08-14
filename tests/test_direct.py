"""Test HTML comment directives implemented in direct.py and fenced.py."""
from pathlib import Path

import phmutest.select
from phmutest.direct import Marker
from phmutest.fenced import Role


def get_all_fcbs(filename):
    """Get all configured FCBs from the file."""
    return phmutest.select.configure_block_roles(skips=(), markdown_file=Path(filename))


class TestPhmdoctest:
    """Check directives that start with <~--phmdoctest."""

    def setup_method(self):
        self.blocks = get_all_fcbs("tests/md/legacy_directives.md")

    def test_label(self):
        assert len(self.blocks) == 14
        assert self.blocks[6].has_directive(Marker.LABEL)
        assert self.blocks[6].directives[0].value == "skipif-pyversion"
        assert self.blocks[7].role == Role.OUTPUT
        assert self.blocks[10].has_directive(Marker.LABEL)
        assert self.blocks[10].role == Role.SESSION

    def test_skip(self):
        assert self.blocks[0].has_directive(Marker.SKIP)
        assert self.blocks[0].directives[0].literal == "<!--phmdoctest-skip-->"
        assert self.blocks[1].role == Role.CODE
        assert self.blocks[2].has_directive(Marker.SKIP)
        assert self.blocks[2].directives[0].literal == "<!--phmdoctest-skip-->"
        assert self.blocks[3].role == Role.SESSION

    def test_mark_skip(self):
        assert self.blocks[4].has_directive(Marker.SKIP)
        assert self.blocks[4].directives[0].literal == "<!--phmdoctest-mark.skip-->"
        assert self.blocks[5].role == Role.OUTPUT

    def test_mark_skipif(self):
        assert self.blocks[6].has_directive(Marker.SKIPIF_PYVERSION)
        assert self.blocks[6].directives[1].type == Marker.SKIPIF_PYVERSION
        assert self.blocks[6].directives[1].value == "8"
        assert (
            self.blocks[6].directives[1].literal == "<!--phmdoctest-mark.skipif<3.8-->"
        )
        assert self.blocks[7].role == Role.OUTPUT

    def test_mark_skip_group(self):
        assert self.blocks[8].has_directive(Marker.TEST_GROUP)
        assert self.blocks[8].directives[0].type == Marker.TEST_GROUP
        assert self.blocks[8].directives[0].value == "my-group"
        assert self.blocks[8].directives[0].literal == "<!--phmdoctest-mark.my-group-->"
        assert self.blocks[9].role == Role.OUTPUT

    def test_setup(self):
        assert self.blocks[11].has_directive(Marker.SETUP)

    def test_teardown(self):
        assert self.blocks[12].has_directive(Marker.TEARDOWN)

    def test_2blank_lines(
        self,
    ):  # Does not qualify as a directive due to 2 blank lines before FCB.
        assert self.blocks[13].directives == []

    def test_fields(self):
        directive = self.blocks[0].directives[0]
        assert directive.type == Marker.SKIP
        assert directive.value == ""
        assert directive.line == 4
        assert directive.literal == "<!--phmdoctest-skip-->"


class TestPhutest:
    """Check directives that start with <~--phmutest."""

    def setup_method(self):
        self.blocks = get_all_fcbs("tests/md/directives.md")

    def test_label(self):
        assert len(self.blocks) == 13
        assert self.blocks[4].has_directive(Marker.LABEL)
        assert self.blocks[4].directives[0].value == "skipif-pyversion"
        assert self.blocks[5].role == Role.OUTPUT
        assert self.blocks[8].has_directive(Marker.LABEL)
        assert self.blocks[8].role == Role.SESSION

    def test_skip(self):
        assert self.blocks[0].has_directive(Marker.SKIP)
        assert self.blocks[0].directives[0].literal == "<!--phmutest-skip-->"
        assert self.blocks[1].role == Role.CODE
        assert self.blocks[2].has_directive(Marker.SKIP)
        assert self.blocks[2].directives[0].literal == "<!--phmutest-skip-->"
        assert self.blocks[3].role == Role.SESSION

    def test_skipif(self):
        assert self.blocks[4].role == Role.CODE
        assert self.blocks[4].has_directive(Marker.SKIPIF_PYVERSION)
        assert self.blocks[4].directives[1].type == Marker.SKIPIF_PYVERSION
        assert self.blocks[4].directives[1].value == "8"
        assert self.blocks[4].directives[1].literal == "<!--phmutest-skipif<3.8-->"
        assert self.blocks[5].directives == []
        assert self.blocks[5].role == Role.OUTPUT

    def test_group(self):
        assert self.blocks[6].has_directive(Marker.TEST_GROUP)
        assert self.blocks[6].directives[0].type == Marker.TEST_GROUP
        assert self.blocks[6].directives[0].value == "my-group"
        assert self.blocks[6].directives[0].literal == "<!--phmutest-group my-group-->"
        assert self.blocks[7].role == Role.OUTPUT

    def test_setup(self):
        assert self.blocks[9].has_directive(Marker.SETUP)

    def test_teardown(self):
        assert self.blocks[10].has_directive(Marker.TEARDOWN)

    def test_2blank_lines(self):
        assert self.blocks[11].directives == []

    def test_fields(self):
        directive = self.blocks[9].directives[0]
        assert directive.type == Marker.SETUP
        assert directive.value == ""
        assert directive.line == 71
        assert directive.literal == "<!--phmutest-setup-->"

    def test_comments_blanks(self):
        directive = self.blocks[12].directives[0]
        assert directive.type == Marker.SKIP
        assert directive.value == ""
        assert directive.line == 102
        assert directive.literal == "<!--phmutest-skip-->"


class TestMisc:
    """Try indented, illegal, on output block, embedded spaces."""

    def setup_method(self):
        self.blocks = get_all_fcbs("tests/md/more_directives.md")

    def test_indented(self):
        assert len(self.blocks) == 8
        assert self.blocks[0].has_directive(Marker.SKIP)
        assert self.blocks[0].role == Role.CODE
        directive = self.blocks[0].directives[0]
        assert directive.line == 5

        # over indented HTML comment
        assert self.blocks[1].directives == []
        assert self.blocks[1].role == Role.CODE

        # directive below the FCB is not detected
        assert self.blocks[2].directives == []
        assert self.blocks[2].role == Role.CODE
        assert self.blocks[3].directives == []
        assert self.blocks[3].role == Role.CODE

    def test_text_between(self):
        # text between directive and FCB
        assert self.blocks[4].directives == []
        assert self.blocks[4].role == Role.CODE

    def test_output_block(self):
        # directive on an output block
        assert self.blocks[5].directives == []
        assert self.blocks[5].role == Role.CODE
        assert self.blocks[6].directives[0].type == Marker.SKIP
        assert self.blocks[6].directives[1].type == Marker.LABEL
        assert self.blocks[6].role == Role.OUTPUT

    def test_extra_spaces(self):
        # directive on an output block
        assert self.blocks[7].has_directive(Marker.LABEL)
        assert (
            self.blocks[7].directives[0].literal
            == "<!--phmutest-label   EXTRA_SPACES  -->"
        )
