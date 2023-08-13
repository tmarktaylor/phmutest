"""Tests --sharing printing."""
import contextlib
import io
import unittest

import phmutest.main


def namelist(text, unwanted_prefix):
    """Return list of comma-space separated names in the text line, less the prefix."""
    # Custom tool to extract the names in --sharing printed output.
    # Any one of the names can include the prefix, so order should not matter.
    raw_tokens = text.split(", ")
    tokens = [t.replace(unwanted_prefix, "") for t in raw_tokens]
    tokens.sort()
    return tokens


def test_share_across_with_setup_sharing():
    """Show that setup blocks are not shared by share-across-files."""
    # --quiet is passed through to unittest to prevent the progress dot printing.
    with contextlib.redirect_stderr(io.StringIO()) as err:
        command = (
            "--log --config tests/toml/acrossfiles2.toml "
            "--sharing tests/md/setupnoteardown.md --quiet"
        )
        phmresult = phmutest.main.main(command.split())
        want = phmutest.summary.Metrics(
            number_blocks_run=6,
            passed=6,
            failed=0,
            skipped=0,
            suite_errors=0,
            number_of_files=2,
            files_with_no_blocks=0,
            number_of_deselected_blocks=0,
        )
        assert want == phmresult.metrics
        assert phmresult.is_success is True
        assert isinstance(phmresult.test_program, unittest.TestProgram)

        lines = err.getvalue().splitlines()
        assert "sharing-mod initialized" in lines[0]
        assert "sharing-class initialized" in lines[1]
        # setUpClass
        assert "sharing-class-tests/md/setupnoteardown.md adding=" in lines[2]
        assert "sharing-class-tests/md/setupnoteardown.md names= " in lines[3]
        # due to share-across-files done at end of class tests() before class teardown.
        assert "sharing-mod-tests/md/setupnoteardown.md adding=" in lines[4]
        assert "sharing-mod-tests/md/setupnoteardown.md names= " in lines[5]
        # tearDownClass
        assert "sharing-class clearing= " in lines[6]
        assert "sharing-class is empty" in lines[7]
        # tearDownModule
        assert "sharing-mod clearing= " in lines[8]
        assert "sharing-mod is empty" in lines[9]

        # Check the names in the setup block that are shared to the test class
        got_setup_names = namelist(
            lines[2], "sharing-class-tests/md/setupnoteardown.md adding= "
        )
        # The list of expected values below is created by inspecting
        # tests/md/setupnoteardown.md blocks with phmutest-setup directive
        # for the names on:
        # 1. left hand side of =
        # 2. right hand of import or from import statement
        want_setup_names = [
            "math",
            "my_function",
            "myglobs_list",
        ]
        assert set(want_setup_names) == set(got_setup_names)

        # Check the names in the non-setup blocks that are shared across files.
        got_shared_names = namelist(
            lines[4], "sharing-mod-tests/md/setupnoteardown.md adding= "
        )
        want_shared_names = [
            "shared_int",
            "shared_string",
        ]
        assert set(want_shared_names) == set(got_shared_names)

        err.close()


def test_setup_across_sharing():
    """Run the setup across files example with --sharing."""
    with contextlib.redirect_stderr(io.StringIO()) as err:
        command = (
            "docs/setup/across1.md docs/setup/across2.md "
            "--setup-across-files docs/setup/across1.md --log "
            "--sharing docs/setup/across1.md"
        )
        phmresult = phmutest.main.main(command.split())
        want = phmutest.summary.Metrics(
            number_blocks_run=6,
            passed=6,
            failed=0,
            skipped=0,
            suite_errors=0,
            number_of_files=2,
            files_with_no_blocks=0,
            number_of_deselected_blocks=0,
        )
        assert want == phmresult.metrics
        assert phmresult.is_success is True
        assert isinstance(phmresult.test_program, unittest.TestProgram)
        lines = err.getvalue().splitlines()
        assert "sharing-mod initialized" in lines[0]
        assert "sharing-mod adding= " in lines[1]
        assert "sharing-mod names= " in lines[2]
        assert "sharing-mod clearing= " in lines[3]
        assert "sharing-mod is empty" in lines[4]

        added_names = namelist(lines[1], "sharing-mod adding= ")
        # The list of expected values below is created by inspecting
        # docs/setup/across1.md for the names on:
        # 1. left hand side of =
        # 2. right hand of import or from import statement
        assigned_names = [
            "CONTENTS",
            "ExitStack",
            "FILENAME",
            "Path",
            "cleanup_tmpdir",
            "create_tmpdir",
            "original_cwd",
            "os",
            "tempfile",
        ]
        assert set(added_names) == set(assigned_names)
        # uncomment to troubleshoot   print(err.getvalue()) assert False
        err.close()


def test_share_across_sharing_replmode(capsys):
    """Run the share across files example with --sharing."""
    command = (
        "docs/repl/repl1.md docs/repl/repl2.md docs/repl/repl3.md --replmode "
        "--share-across-files docs/repl/repl1.md docs/repl/repl2.md --log"
        " --sharing ."
    )
    args = command.split()
    phmresult = phmutest.main.main(args)
    want = phmutest.summary.Metrics(
        number_blocks_run=8,
        passed=8,
        failed=0,
        skipped=0,
        suite_errors=0,
        number_of_files=3,
        files_with_no_blocks=0,
        number_of_deselected_blocks=0,
    )
    assert want == phmresult.metrics
    output = capsys.readouterr().out.rstrip()
    lines = output.splitlines()
    assert "docs/repl/repl1.md is sharing: " in lines[0]
    assert "docs/repl/repl2.md is sharing: " in lines[1]

    got_repl1_names = namelist(lines[0], "docs/repl/repl1.md is sharing: ")
    # The list of expected values below is created by inspecting
    # docs/repl/repl1.md for the names on:
    # 1. left hand side of =
    # 2. right hand of import or from import statement
    want_repl1_names = [
        "BeverageActivity",
        "cc",
        "dataclass",
        "we",
    ]
    assert set(want_repl1_names) == set(got_repl1_names)

    got_repl2_names = namelist(lines[1], "docs/repl/repl2.md is sharing: ")
    want_repl2_names = ["bp"]
    assert set(want_repl2_names) == set(got_repl2_names)


def test_fixture_sharing_replmode(capsys):
    """Show sharing message for the fixture globs to get code coverage."""

    # The fixture globs are not used by the FILEs in this test.
    command = (
        "docs/repl/repl1.md docs/repl/repl2.md docs/repl/repl3.md --replmode "
        "--share-across-files docs/repl/repl1.md docs/repl/repl2.md --log"
        " --sharing ."
        " --fixture docs.fix.repl.drink.init"
    )
    args = command.split()
    phmresult = phmutest.main.main(args)
    want = phmutest.summary.Metrics(
        number_blocks_run=8,
        passed=8,
        failed=0,
        skipped=0,
        suite_errors=0,
        number_of_files=3,
        files_with_no_blocks=0,
        number_of_deselected_blocks=0,
    )
    assert want == phmresult.metrics
    output = capsys.readouterr().out.rstrip()
    lines = output.splitlines()
    assert "Acquiring Drink tea." in lines[0]
    assert "docs.fix.repl.drink.init is sharing:" in lines[1]
    assert "docs/repl/repl1.md is sharing: " in lines[2]
    assert "docs/repl/repl2.md is sharing: " in lines[3]

    got_fixture_names = namelist(lines[1], "docs.fix.repl.drink.init is sharing: ")
    # The list of expected values below is created by inspecting
    # docs/fix/repl/drink.py init() 'Fixture(globs=' value.
    want_fixture_names = ["drink", "EXTRA"]
    assert set(want_fixture_names) == set(got_fixture_names)

    got_repl1_names = namelist(lines[2], "docs/repl/repl1.md is sharing: ")
    # The list of expected values below is created by inspecting
    # docs/repl/repl1.md for the names on:
    # 1. left hand side of =
    # 2. right hand of import or from import statement
    want_repl1_names = [
        "BeverageActivity",
        "cc",
        "dataclass",
        "we",
    ]
    assert set(want_repl1_names) == set(got_repl1_names)

    got_repl2_names = namelist(lines[3], "docs/repl/repl2.md is sharing: ")
    want_repl2_names = ["bp"]
    assert set(want_repl2_names) == set(got_repl2_names)


def test_share_across_sharing():
    """Run the share across files example with '--sharing .' and '--quiet'.

    Note the dot after --sharing. That means print sharing debug messages
    for all shared files.
    The --quiet option pases through to unittest and suppresses printing.
    Otherwise the case suceeded status character "." gets into the
    output.
    """
    with contextlib.redirect_stderr(io.StringIO()) as err:
        command = (
            "docs/share/file1.md docs/share/file2.md docs/share/file3.md "
            "--share-across-files docs/share/file1.md docs/share/file2.md --log "
            "--sharing . --quiet"
        )
        args = command.split()
        phmresult = phmutest.main.main(args)
        want = phmutest.summary.Metrics(
            number_blocks_run=8,
            passed=8,
            failed=0,
            skipped=0,
            suite_errors=0,
            number_of_files=3,
            files_with_no_blocks=0,
            number_of_deselected_blocks=0,
        )
        assert want == phmresult.metrics
        assert phmresult.is_success is True
        assert isinstance(phmresult.test_program, unittest.TestProgram)
        lines = err.getvalue().splitlines()

        assert "sharing-mod initialized" in lines[0]
        assert "sharing-mod-docs/share/file1.md adding= " in lines[1]
        assert "sharing-mod-docs/share/file1.md names= " in lines[2]
        assert "sharing-mod-docs/share/file2.md adding= " in lines[3]
        assert "sharing-mod-docs/share/file2.md names= " in lines[4]
        assert "sharing-mod clearing= " in lines[5]
        assert "sharing-mod is empty" in lines[6]

        got_file1_names = namelist(lines[1], "sharing-mod-docs/share/file1.md adding= ")
        # The list of expected values below is created by inspecting
        # docs/setup/across1.md for the names on:
        # 1. left hand side of =
        # 2. right hand of import or from import statement
        want_file1_names = [
            "BeverageActivity",
            "cc",
            "dataclass",
            "we",
        ]
        assert set(want_file1_names) == set(got_file1_names)

        got_file2_names = namelist(lines[3], "sharing-mod-docs/share/file2.md adding= ")
        want_file2_names = ["bp"]
        assert set(want_file2_names) == set(got_file2_names)

        # uncomment to troubleshoot   print(err.getvalue()) err.close()
