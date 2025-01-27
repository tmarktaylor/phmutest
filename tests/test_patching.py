"""Show use cases for patch points."""

import copy
import doctest
from contextlib import ExitStack
from unittest import mock

import phmutest.direct
import phmutest.fenced
import phmutest.fixture
import phmutest.main
import phmutest.reader
import phmutest.select
import phmutest.session
import phmutest.summary
from phmutest.direct import MarkerPattern

# Note that the last block is included because it has the
# info string ladenpython in the Markdown input file.
python_infostring_log = """\
log:
args.files: 'tests/md/patching1.md'
args.log: 'True'

location|label                           result
---------------------------------------  ------
tests/md/patching1.md:4 testing-1-2-3 o  pass
tests/md/patching1.md:13 o.............  pass
tests/md/patching1.md:23 o.............  pass
---------------------------------------  ------
"""


def test_python_infostring_patch(capsys):
    """Patching fenced code block info_string python language matching."""
    matcher = phmutest.fenced.PythonMatcher()
    matcher.python_patterns.append("ladenpython")  # Also match info string ladenpython.
    matcher.compile()
    with mock.patch("phmutest.fenced.python_matcher", matcher):
        line = "tests/md/patching1.md --log"
        phmresult = phmutest.main.command(line)
    want = phmutest.summary.Metrics(
        number_blocks_run=3,
        passed=3,  # counts the ladenpython FCB
        failed=0,
        skipped=0,
        suite_errors=0,
        number_of_files=1,
        files_with_no_blocks=0,
        number_of_deselected_blocks=0,
    )
    assert want == phmresult.metrics
    assert python_infostring_log == capsys.readouterr().out.lstrip()


def test_python_infostring_delimiter_patch(capsys):
    """Also patch info_string delimiter chars."""
    matcher = phmutest.fenced.PythonMatcher()
    # Also match additional info strings
    matcher.python_patterns.append("ladenpython")
    matcher.python_patterns.append("awesomepython")
    # Add ! as a delimiter for the info string.
    # This patch should work on future versions of delimiter_chars
    # that have more choices.
    matcher.delimiter_chars = matcher.delimiter_chars.replace(r"([", r"([!")
    matcher.compile()
    with mock.patch("phmutest.fenced.python_matcher", matcher):
        line = "tests/md/patching1.md --log"
        phmresult = phmutest.main.command(line)
    want = phmutest.summary.Metrics(
        number_blocks_run=4,
        passed=4,  # counts the ladenpython and awesomepython FCB
        failed=0,
        skipped=0,
        suite_errors=0,
        number_of_files=1,
        files_with_no_blocks=0,
        number_of_deselected_blocks=0,
    )
    assert want == phmresult.metrics


def make_finder(old_name, new_name):
    """Make a directive MarkerPattern to match new_name that behaves like old_name."""
    assert old_name != new_name
    finders = [f for f in phmutest.direct.directive_finders if old_name in f.pattern]
    assert finders, f"no finder pattern containing {old_name}."
    assert len(finders) == 1, f"more than 1 finder pattern containing {old_name}."
    finder = finders[0]
    regex = finder.pattern.replace(old_name, new_name)
    return MarkerPattern(finder.marker, regex)


# Note the FCB label directive value shown at right in the first column.
# The label "abc" is detected by the directive alias added by the patch.
# In the infostring_log above, which does not have the directive patch,
# "abc" is not present.
directive_log = """\
log:
args.files: 'tests/md/patching1.md'
args.log: 'True'

location|label                           result
---------------------------------------  ------
tests/md/patching1.md:4 testing-1-2-3 o  pass
tests/md/patching1.md:13 abc o.........  pass
---------------------------------------  ------
"""


def test_directive_patch(capsys):
    """Use patch to add an alias for the phmutest-label directive."""

    # Make a new finder to detect the new directive
    # based on the existing directive finder.
    finder_alias = make_finder("phmutest-label", "my-new-label")

    # Extend a copy of the list of finders with the new finder.
    updated_finders = copy.copy(phmutest.direct.directive_finders)
    updated_finders.append(finder_alias)
    with mock.patch("phmutest.direct.directive_finders", updated_finders):
        line = "tests/md/patching1.md --log"
        phmresult = phmutest.main.command(line)
    want = phmutest.summary.Metrics(
        number_blocks_run=2,
        passed=2,  # does not count the ladenpython FCB
        failed=0,
        skipped=0,
        suite_errors=0,
        number_of_files=1,
        files_with_no_blocks=0,
        number_of_deselected_blocks=0,
    )
    assert want == phmresult.metrics
    assert directive_log == capsys.readouterr().out.lstrip()


def remove_payload(node: phmutest.reader.DocNode) -> None:
    """Patch replacement function that sets DocNode.contents to empty string."""
    node.payload = ""


def test_docnode_patch():
    """Try patching phmutest.reader.post to modify arbitrary DocNodes."""
    # Make sure the FCB DocNodes really have contents.
    nodes1 = phmutest.reader.fcb_nodes("tests/md/patching1.md")
    for node1 in nodes1:
        assert node1.payload

    # Apply patch that sets contents to empty string.
    with mock.patch("phmutest.reader.post", remove_payload):
        nodes2 = phmutest.reader.fcb_nodes("tests/md/patching1.md")
        for node2 in nodes2:
            assert node2.payload == ""


def rewrite_docstring(text: str) -> str:
    """Replacement function that modifies the docstring."""
    text = text.replace("print", "zprint")
    return text


def test_modify_docstring_patch():
    """Show modify_docstring patch changes the docstring that gets run."""
    # Run twice, first time without the patch. The second time with the
    # patch that makes the 3 blocks fail.
    line = "tests/md/optionflags.md --replmode --fixture tests.test_patching.setflags"
    phmresult1 = phmutest.main.command(line)
    want1 = phmutest.summary.Metrics(
        number_blocks_run=3,
        passed=3,
        failed=0,
        skipped=0,
        suite_errors=0,
        number_of_files=1,
        files_with_no_blocks=0,
        number_of_deselected_blocks=0,
    )
    assert want1 == phmresult1.metrics
    assert phmresult1.is_success is True

    with mock.patch("phmutest.session.modify_docstring", rewrite_docstring):
        phmresult2 = phmutest.main.command(line)
    want2 = phmutest.summary.Metrics(
        number_blocks_run=3,
        passed=0,
        failed=0,
        skipped=0,
        suite_errors=3,
        number_of_files=1,
        files_with_no_blocks=0,
        number_of_deselected_blocks=0,
    )
    assert want2 == phmresult2.metrics
    assert phmresult2.is_success is False


class OptionflagRunner(phmutest.session.ExampleOutcomeRunner):
    """Doctest Runner to set optionflags."""

    myflags = doctest.NORMALIZE_WHITESPACE | doctest.ELLIPSIS

    def __init__(self, **kwargs):  # type: ignore
        of = kwargs.get("optionflags", 0)
        kwargs["optionflags"] = of | self.myflags
        super().__init__(**kwargs)


def setflags(**kwargs):
    """phmutest fixture function to patch the doctest runner."""
    with ExitStack() as stack:
        stack.enter_context(
            mock.patch("phmutest.session.ExampleOutcomeRunner", OptionflagRunner)
        )
        fixture = phmutest.fixture.Fixture(
            globs=None, repl_cleanup=stack.pop_all().close
        )
    return fixture


def test_doctest_optionflags_patch():
    """Test a --fixture that runs doctests with optionflags."""
    line = (
        "tests/md/optionflags.md --log --replmode "
        " --fixture tests.test_patching.setflags"
    )
    phmresult = phmutest.main.command(line)
    want = phmutest.summary.Metrics(
        number_blocks_run=3,
        passed=3,
        failed=0,
        skipped=0,
        suite_errors=0,
        number_of_files=1,
        files_with_no_blocks=0,
        number_of_deselected_blocks=0,
    )
    assert want == phmresult.metrics
    assert phmresult.is_success is True


output_infostring_log = """\
log:
args.files: 'tests/md/output_info_string.md'
args.log: 'True'

location|label                       result
-----------------------------------  ------
tests/md/output_info_string.md:17 o  pass
-----------------------------------  ------
"""


def test_output_infostring_patch(capsys):
    """Add a new FCB info string that identifies the expected output block."""
    info_strings = phmutest.select.OUTPUT_INFO_STRINGS
    info_strings.append("captured-stdout")
    line = "tests/md/output_info_string.md --log"
    with mock.patch("phmutest.select.OUTPUT_INFO_STRINGS", info_strings):
        phmresult = phmutest.main.command(line)
    want2 = phmutest.summary.Metrics(
        number_blocks_run=1,
        passed=1,
        failed=0,
        skipped=0,
        suite_errors=0,
        number_of_files=1,
        files_with_no_blocks=0,
        number_of_deselected_blocks=0,
    )
    assert want2 == phmresult.metrics
    assert phmresult.is_success is True
    assert output_infostring_log == capsys.readouterr().out.lstrip()
