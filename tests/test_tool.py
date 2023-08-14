"""Test tool.py"""
import phmutest.tool


def test_fcbs():
    """Test fenced_code_blocks(). Contents of all FCBs in the file."""
    markdown_filename = "tests/md/more_directives.md"
    fenced = phmutest.tool.fenced_code_blocks(markdown_filename)
    assert len(fenced) == 8
    assert fenced[0] == "assert False\n"
    assert fenced[1] == "assert False\n"
    assert fenced[2] == "assert False\n"
    assert fenced[3] == "assert False\n"
    assert fenced[4] == "assert False\n"
    assert "b = 10" in fenced[5]
    assert "10, 1" in fenced[6]
    assert fenced[7] == "assert False\n"


def test_labeled_fcbs():
    """Test labeled_fenced_code_blocks()."""
    markdown_filename = "tests/md/more_directives.md"
    labeled = phmutest.tool.labeled_fenced_code_blocks(markdown_filename)
    assert len(labeled) == 2
    assert labeled[0].label == "my-label"
    assert labeled[0].line == "43"
    assert labeled[0].contents == "(10, 1)\n"
    assert labeled[1].label == "  EXTRA_SPACES  "
    assert labeled[1].line == "49"
    assert labeled[1].contents == "assert False\n"


def test_contents():
    """Pick an FCB that has a phmutest-label directive."""
    markdown_filename = "tests/md/more_directives.md"
    chooser = phmutest.tool.FCBChooser(markdown_filename)
    assert chooser.contents(label="my-label") == "(10, 1)\n"
    assert chooser.contents(label="  EXTRA_SPACES  ") == "assert False\n"


def test_contents_did_not_find():
    """Try cases where FCBChooser does not find a FCB."""
    # File does not have FCB with label directives.
    markdown_filename1 = "tests/md/reader.md"
    labeled1 = phmutest.tool.labeled_fenced_code_blocks(markdown_filename1)
    assert len(labeled1) == 0
    chooser1 = phmutest.tool.FCBChooser(markdown_filename1)
    assert chooser1.contents("never-will-be-found") == ""

    # Looking for a label which does match any of the label directives in the file.
    markdown_filename2 = "tests/md/more_directives.md"
    chooser2 = phmutest.tool.FCBChooser(markdown_filename2)
    assert chooser2.contents(label="never-will-be-found") == ""


class TestSelect:
    def setup_method(self):
        self.chooser = phmutest.tool.FCBChooser("tests/md/multi_label.md")

    def test_not_found(self):
        """Select multiple blocks with the same label."""
        selected = self.chooser.select(label="no-chance")
        assert selected == []

    def test_label(self):
        """Select multiple blocks with the same label."""
        selected = self.chooser.select(label="one-label-many-blocks")
        assert len(selected) == 3
        assert selected[0] == "first of many\n"
        assert selected[1] == "assert False\n"
        assert selected[2] == "third of many\n"

        selected1 = self.chooser.select(
            label="one-label-many-blocks", info_string="python"
        )
        assert len(selected1) == 1
        assert selected1[0] == "assert False\n"

        selected2 = self.chooser.select(
            label="one-label-many-blocks", info_string="python", contains="XXXX"
        )
        assert not selected2

    def test_many_labels(self):
        """Select by label blocks with more than one label directive."""
        selected = self.chooser.select(label="FIRST")
        assert len(selected) == 1
        assert selected[0] == "ls -l\n"

        selected1 = self.chooser.select(label="SECOND")
        assert len(selected1) == 2
        assert selected1[0] == "ls -l\n"
        assert selected1[1] == "ls -r\n"

        selected2 = self.chooser.select(label="THIRD")
        assert len(selected2) == 1
        assert selected2[0] == "ls -r\n"

    def test_info_string(self):
        """Select multiple blocks with the same info string."""
        selected = self.chooser.select(info_string="python")
        assert len(selected) == 3
        assert selected[0] == "assert False\n"
        assert selected[1] == "assert False\n"
        assert selected[2] == "b = 10\nprint(b.as_integer_ratio())\n"

        selected1 = self.chooser.select(info_string="bogus")
        assert not selected1

        selected2 = self.chooser.select(info_string="python", contains="ratio")
        assert len(selected2) == 1
        assert selected2[0] == "b = 10\nprint(b.as_integer_ratio())\n"

        # Find blocks with no info string.
        selected3 = self.chooser.select(info_string="")
        assert len(selected3) == 3
        assert selected3[0] == "first of many\n"
        assert selected3[1] == "(10, 1)\n"
        assert selected3[2] == "third of many\n"

    def test_contains(self):
        """Select multiple blocks with the same substring."""
        selected = self.chooser.select(contains="python")  # no matches
        assert not selected

        selected1 = self.chooser.select(contains="many")
        assert len(selected1) == 2
        assert selected1[0] == "first of many\n"
        assert selected1[1] == "third of many\n"

    def test_all_criteria(self):
        """Select block(s) with all criteria."""
        selected = self.chooser.select(
            label="one-label-many-blocks", info_string="python", contains="many"
        )
        assert not selected

        selected1 = self.chooser.select(info_string="bash", contains="ls")
        assert len(selected1) == 2
        assert selected1[0] == "ls -l\n"
        assert selected1[1] == "ls -r\n"

    def test_all_default_args(self):
        """Call with no arguments to select all blocks."""
        selected = self.chooser.select()
        assert len(selected) == 8

    def test_default_args_values(self):
        """Call with explicitly stated default argument values."""
        selected = self.chooser.select(label="", info_string=None, contains="")
        assert len(selected) == 8
