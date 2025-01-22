"""Test .toml configuration."""

import unittest
from pathlib import Path

import pytest

import phmutest.config
import phmutest.main
import phmutest.summary


def get_settings(commandline_args):
    """Process command line args including a config file. Return settings."""
    parser = phmutest.main.main_argparser()
    known_args = parser.parse_known_args(commandline_args)
    return phmutest.config.get_settings(known_args)


def process_args(commandline_args):
    """Process command line args including a config file. Return args."""
    settings = get_settings(commandline_args)
    return settings.args


def test_messy_toml_within_pyproject():
    """Read [tool.phmutest] from a simulated pyproject.toml file."""
    # The input toml file also has some un-processed keys that don't belong.
    # The logic in config.py does not check for keys that don't belong.
    commandline_args = [
        "tests/md/noreadernodes.md",
        "--config",
        "tests/toml/sample_pyproject.toml",
    ]
    args = process_args(commandline_args)
    assert len(args.files) == 3
    assert args.files[0] == Path("docs/share/file1.md")
    assert args.files[1] == Path("docs/share/file2.md")

    # Command line files tacked on at end after toml specified files.
    assert args.files[2] == Path("tests/md/noreadernodes.md")

    assert args.skip[0] == "hello-world"
    assert args.skip[1] == "abcd"
    assert args.share_across_files[0] == Path("docs/share/file1.md")
    assert args.share_across_files[1] == Path("docs/share/file2.md")
    assert args.setup_across_files == []

    # config.py sets args.fixture to None if no-existing or un-truthy value in toml.
    assert args.fixture is None

    assert args.select == []
    assert args.deselect[0] == "notmygroup3"
    assert args.deselect[1] == "notmygroup4"


def test_nokeys_in_section():
    """All the keys in the section are commented out."""
    command = "--config tests/toml/nokeys.toml"
    args = command.split()
    phmresult = phmutest.main.main(args)
    want = phmutest.summary.Metrics(
        number_blocks_run=0,
        passed=0,
        failed=0,
        skipped=0,
        suite_errors=0,
        number_of_files=0,
        files_with_no_blocks=0,
        number_of_deselected_blocks=0,
    )
    assert want == phmresult.metrics
    assert phmresult.is_success is True


def test_toml_fixture_key():
    """Show fixture key is read from .toml."""
    commandline_args = ["--config", "tests/toml/chdir.toml"]
    args = process_args(commandline_args)
    assert len(args.files) == 1
    assert args.files[0] == Path("docs/fix/code/chdir.md")
    assert args.skip == []
    assert args.share_across_files == []
    assert args.setup_across_files == []
    assert args.fixture == Path("docs.fix.code.chdir.change_dir")
    assert args.select == []
    assert args.deselect == []


def test_md_file_not_exists():
    """Input Markdown file does not exist."""
    command = "NotAnExistingFile.md --log"
    args = command.split()
    with pytest.raises(SystemExit):
        phmutest.main.main(args)


def test_share_across_not_exists():
    """Filename provided .toml share-across-files key does not exist."""
    command = "--config tests/toml/filenotexists1.toml --log"
    args = command.split()
    with pytest.raises(ValueError) as exc_info:
        phmutest.main.main(args)
    assert "NotAnExistingFile1.md not found" in str(exc_info.value)


def test_share_across_not_in_files():
    """Filename provided .toml share-across-files key does not exist."""
    command = "--config tests/toml/share_across_not_in_files.toml --log"
    args = command.split()
    with pytest.raises(ValueError) as exc_info:
        phmutest.main.main(args)
    assert "share-across-files must also be positional argument" in str(exc_info.value)


def test_setup_across_not_in_files():
    """Filename provided .toml setup-across-files key does not exist."""
    command = "--config tests/toml/setup_across_not_in_files.toml --log"
    args = command.split()
    with pytest.raises(ValueError) as exc_info:
        phmutest.main.main(args)
    assert "setup-across-files must also be positional argument" in str(exc_info.value)


def test_setup_across_not_exists():
    """Filename provided .toml setup-across-files key does not exist."""
    command = "--config tests/toml/filenotexists2.toml --log"
    args = command.split()
    with pytest.raises(ValueError) as exc_info:
        phmutest.main.main(args)
    assert "NotAnExistingFile2.md not found" in str(exc_info.value)


def test_skip_pattern_override():
    """Command line skip pattern overrides the config file skip key."""
    command = "--config tests/toml/sample_pyproject.toml --skip partying --log"
    args = command.split()
    phmresult = phmutest.main.main(args)
    want = phmutest.summary.Metrics(
        number_blocks_run=5,
        passed=5,
        failed=0,
        skipped=1,
        suite_errors=0,
        number_of_files=2,
        files_with_no_blocks=0,
        number_of_deselected_blocks=0,
    )
    assert want == phmresult.metrics
    assert phmresult.is_success is True


def test_include_exclude_globs():
    """include-globs selects 3 files, exclude-globs deselects one of them."""
    command = "--config tests/toml/excludeglobs.toml --log"
    args = command.split()
    phmresult = phmutest.main.main(args)
    want = phmutest.summary.Metrics(
        number_blocks_run=5,
        passed=4,
        failed=1,
        skipped=1,
        suite_errors=0,
        number_of_files=2,
        files_with_no_blocks=0,
        number_of_deselected_blocks=0,
    )
    assert want == phmresult.metrics
    assert phmresult.is_success is False


def test_share_across_precedence():
    """share-across-files on command line supersedes .toml section."""
    command = (
        " tests/md/setupnoteardown.md"
        " tests/md/sharedto2.md"
        " --config tests/toml/badacrossfiles.toml --log"
        " --share-across-files tests/md/setupnoteardown.md"
        " --setup-across-files tests/md/directive2.md"
    )
    args = command.split()
    phmresult = phmutest.main.main(args)
    want = phmutest.summary.Metrics(
        number_blocks_run=14,
        passed=13,
        failed=1,
        skipped=0,
        suite_errors=0,
        number_of_files=5,
        files_with_no_blocks=0,
        number_of_deselected_blocks=0,
    )
    assert want == phmresult.metrics
    assert phmresult.is_success is False


def fixture(**kwargs):
    """Phmutest fixture function."""
    log = kwargs["log"]
    log.append(["fixture", "complete", ""])
    raise unittest.SkipTest


def test_fixture_precedence(capsys, endswith_checker):
    """Fixture specified on command line overrides fixture key in .toml."""
    command = "--config tests/toml/chdir.toml --fixture tests.test_config.fixture --log"
    args = command.split()
    phmresult = phmutest.main.main(args)
    want = phmutest.summary.Metrics(
        number_blocks_run=0,
        passed=0,
        failed=0,
        skipped=0,
        suite_errors=0,
        number_of_files=1,
        files_with_no_blocks=0,
        number_of_deselected_blocks=0,
    )
    assert want == phmresult.metrics
    assert phmresult.is_success is True

    output = capsys.readouterr().out.strip()
    expected = """location|label  result
        --------------  --------
        setUpModule...
        fixture.......  complete
        --------------  --------
        """
    endswith_checker(expected, output)


def test_select_no_override(capsys, endswith_checker):
    command = "tests/md/code_groups.md --config tests/toml/groupa.toml --log"
    args = command.split()
    phmresult = phmutest.main.main(args)
    want = phmutest.summary.Metrics(
        number_blocks_run=2,
        passed=2,
        failed=0,
        skipped=0,
        suite_errors=0,
        number_of_files=1,
        files_with_no_blocks=0,
        number_of_deselected_blocks=2,
    )
    assert want == phmresult.metrics
    assert phmresult.is_success is True
    output = capsys.readouterr().out.strip()
    expected = """location|label             result
        -------------------------  ------
        tests/md/code_groups.md:4  pass
        tests/md/code_groups.md:9  pass
        -------------------------  ------
        """
    endswith_checker(expected, output)


def test_select_override(capsys, endswith_checker):
    command = (
        "tests/md/code_groups.md --config tests/toml/groupa.toml"
        " --select group-2 group-3 --log"
    )
    args = command.split()
    phmresult = phmutest.main.main(args)
    want = phmutest.summary.Metrics(
        number_blocks_run=2,
        passed=2,
        failed=0,
        skipped=0,
        suite_errors=0,
        number_of_files=1,
        files_with_no_blocks=0,
        number_of_deselected_blocks=2,
    )
    assert want == phmresult.metrics
    assert phmresult.is_success is True
    output = capsys.readouterr().out.strip()
    expected = """location|label              result
        --------------------------  ------
        tests/md/code_groups.md:15  pass
        tests/md/code_groups.md:22  pass
        --------------------------  ------
        """
    endswith_checker(expected, output)


def test_deselect_no_override(capsys, endswith_checker):
    command = "tests/md/code_groups.md --config tests/toml/groupb.toml --log"
    args = command.split()
    phmresult = phmutest.main.main(args)
    want = phmutest.summary.Metrics(
        number_blocks_run=3,
        passed=3,
        failed=0,
        skipped=0,
        suite_errors=0,
        number_of_files=1,
        files_with_no_blocks=0,
        number_of_deselected_blocks=1,
    )
    assert want == phmresult.metrics
    assert phmresult.is_success is True
    output = capsys.readouterr().out.strip()
    expected = """location|label              result
        --------------------------  ------
        tests/md/code_groups.md:4.  pass
        tests/md/code_groups.md:9.  pass
        tests/md/code_groups.md:15  pass
        --------------------------  ------
        """
    endswith_checker(expected, output)


def test_deselect_override(capsys, endswith_checker):
    command = (
        "tests/md/code_groups.md --config tests/toml/groupb.toml"
        " --deselect group-2 group-3 --log"
    )
    args = command.split()
    phmresult = phmutest.main.main(args)
    want = phmutest.summary.Metrics(
        number_blocks_run=2,
        passed=2,
        failed=0,
        skipped=0,
        suite_errors=0,
        number_of_files=1,
        files_with_no_blocks=0,
        number_of_deselected_blocks=2,
    )
    assert want == phmresult.metrics
    assert phmresult.is_success is True
    output = capsys.readouterr().out.strip()
    expected = """location|label             result
        -------------------------  ------
        tests/md/code_groups.md:4  pass
        tests/md/code_groups.md:9  pass
        -------------------------  ------
        """
    endswith_checker(expected, output)


def test_mutual_exclusion():
    """Both select and deselect keys are non-empty which raises ValueError."""
    command = "--config tests/toml/badgroup.toml --log"
    args = command.split()
    with pytest.raises(ValueError) as exc_info:
        phmutest.main.main(args)
    assert (
        "In tests/toml/badgroup.toml non-empty deselect not allowed with select"
        in str(exc_info.value)
    )


def test_a_pygments_style():
    """Show a pygments style name is read from style key in .toml."""
    commandline_args = ["--config", "tests/toml/style-is-material.toml"]
    args = process_args(commandline_args)
    assert len(args.files) == 2
    assert args.style == "material"


def test_color_config():
    """Show args.color is set when color key in .toml is true."""
    commandline_args = ["--config", "tests/toml/color.toml"]
    args = process_args(commandline_args)
    assert len(args.files) == 3
    assert args.color is True


def test_color_override():
    """Show a command line --color overrides .toml file style key."""
    commandline_args = [
        "--config",
        "tests/toml/project.toml",
        "--color",
    ]
    settings = get_settings(commandline_args)
    args = settings.args
    assert len(args.files) == 3
    assert args.color is True


def test_style_override():
    """Show a command line --style overrides .toml file style key."""
    commandline_args = [
        "--config",
        "tests/toml/style-is-material.toml",
        "--style",
        "dracula",
    ]
    settings = get_settings(commandline_args)
    args = settings.args
    assert len(args.files) == 2
    assert args.style == "dracula"
    settings = get_settings(commandline_args)
