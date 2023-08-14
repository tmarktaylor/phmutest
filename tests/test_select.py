"""Test test group select/deselect."""
from pathlib import Path

import phmutest.main
import phmutest.select


def get_selected_blocks(filename, args):
    parser = phmutest.main.main_argparser()
    known_args = parser.parse_known_args(args)
    blockstore = phmutest.select.BlockStore(known_args[0])
    fileblocks = blockstore.get_blocks(Path(filename))
    return fileblocks.selected


def test_select_no_group_match():
    filename = "tests/md/code_groups.md"
    args = [filename, "--select", "groupp-1"]  # mispelled group
    blocks = get_selected_blocks(filename, args)
    assert len(blocks) == 0


def test_deselect_no_group_match():
    filename = "tests/md/code_groups.md"
    args = [filename, "--deselect", "groupp-1"]  # mispelled group
    blocks = get_selected_blocks(filename, args)
    assert len(blocks) == 4


def test_select_code_group1():
    filename = "tests/md/code_groups.md"
    args = [filename, "--select", "group-1"]
    blocks = get_selected_blocks(filename, args)
    assert len(blocks) == 2
    assert "legacy-group-1" in blocks[0].contents
    assert "code-group-1" in blocks[1].contents


def test_deselect_code_group1():
    filename = "tests/md/code_groups.md"
    args = [filename, "--deselect", "group-1"]
    blocks = get_selected_blocks(filename, args)
    assert len(blocks) == 2


def test_select_code_group2():
    filename = "tests/md/code_groups.md"
    args = [filename, "--select", "group-2"]
    blocks = get_selected_blocks(filename, args)
    assert len(blocks) == 1
    assert "code-group-2" in blocks[0].contents


def test_select_code_group4():
    filename = "tests/md/code_groups.md"
    args = [filename, "--select", "group-4"]
    blocks = get_selected_blocks(filename, args)
    assert len(blocks) == 1
    assert "code-group-4" in blocks[0].contents


def test_deselect_code_group4():
    filename = "tests/md/code_groups.md"
    args = [filename, "--deselect", "group-4"]
    blocks = get_selected_blocks(filename, args)
    assert len(blocks) == 3
    assert "legacy-group-1" in blocks[0].contents
    assert "code-group-1" in blocks[1].contents
    assert "code-group-2" in blocks[2].contents
    assert "code-group-3" in blocks[2].contents


def test_select_code_group2and3():
    filename = "tests/md/code_groups.md"
    args = [filename, "--select", "group-2", "group-3"]
    blocks = get_selected_blocks(filename, args)
    assert len(blocks) == 2
    assert "code-group-2" in blocks[0].contents
    assert "code-group-3" in blocks[1].contents


def test_deselect_code_group2and3():
    filename = "tests/md/code_groups.md"
    args = [filename, "--deselect", "group-2", "group-3"]
    blocks = get_selected_blocks(filename, args)
    assert len(blocks) == 2
    assert "legacy-group-1" in blocks[0].contents
    assert "code-group-1" in blocks[1].contents


def test_select_repl5():
    # Also shows that --replmode only considers Python interactive session blocks
    # since both code and session blocks are marked with the
    # <!--phmutest-group group-1--> directive.
    filename = "tests/md/code_groups.md"
    args = [filename, "--replmode", "--select", "repl-5"]
    blocks = get_selected_blocks(filename, args)
    assert len(blocks) == 2
    assert "legacy-repl-5" in blocks[0].contents
    assert "repl-5" in blocks[1].contents


def test_deselect_repl5():
    filename = "tests/md/code_groups.md"
    args = [filename, "--replmode", "--deselect", "repl-5"]
    blocks = get_selected_blocks(filename, args)
    assert len(blocks) == 4


def test_select_repl6():
    filename = "tests/md/code_groups.md"
    args = [filename, "--replmode", "--select", "repl-6"]
    blocks = get_selected_blocks(filename, args)
    assert len(blocks) == 1
    assert "repl-6" in blocks[0].contents


def test_select_repl8():
    filename = "tests/md/code_groups.md"
    args = [filename, "--replmode", "--select", "repl-8"]
    blocks = get_selected_blocks(filename, args)
    assert len(blocks) == 1
    assert "repl-8" in blocks[0].contents


def test_deselect_repl8():
    filename = "tests/md/code_groups.md"
    args = [filename, "--replmode", "--deselect", "repl-8"]
    blocks = get_selected_blocks(filename, args)
    assert len(blocks) == 5
    assert "legacy-1" in blocks[0].contents
    assert "repl-1" in blocks[1].contents
    assert "legacy-repl-5" in blocks[2].contents
    assert "repl-5" in blocks[3].contents
    assert "repl-6" in blocks[4].contents
    assert "repl-7" in blocks[4].contents


def test_select_repl6and7():
    filename = "tests/md/code_groups.md"
    args = [filename, "--replmode", "--select", "repl-6", "repl-7"]
    blocks = get_selected_blocks(filename, args)
    assert len(blocks) == 2
    assert "repl-6" in blocks[0].contents
    assert "repl-7" in blocks[1].contents


def test_deselect_repl6and7():
    filename = "tests/md/code_groups.md"
    args = [filename, "--replmode", "--deselect", "repl-6", "repl-7"]
    blocks = get_selected_blocks(filename, args)
    assert len(blocks) == 4
    assert "legacy-1" in blocks[0].contents
    assert "repl-1" in blocks[1].contents
    assert "legacy-repl-5" in blocks[2].contents
    # Note= The leading blank below prevents a match with 'legacy-repl-5'.
    assert " repl-5" in blocks[3].contents
