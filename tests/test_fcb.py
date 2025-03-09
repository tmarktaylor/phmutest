"""Statement coverage for fcb.py markdown map missing key error message."""

import ast

import pytest

import phmutest.cases
import phmutest.config
import phmutest.fcb
import phmutest.main
from phmutest.fenced import Role


def test_map_missing_key(capsys, startswith_checker):
    """Markdown map missing key error message."""
    parser = phmutest.main.main_argparser()
    line = "tests/md/project.md"
    args = line.split()
    known_args = parser.parse_known_args(args)
    settings = phmutest.config.get_settings(known_args)
    args = settings.args
    block_store = phmutest.select.BlockStore(args)
    _, markdown_map = phmutest.cases.testfile(args, block_store)

    # The log[4] exception line number is not present in the map.
    log = [["tests/md/project.md:29", "failed", "broken", "1234", "5678"]]

    phmutest.fcb.show_broken_fcbs(
        log=log,
        block_store=block_store,
        markdown_map=markdown_map,
        highlighter=settings.highlighter,
    )
    output = capsys.readouterr().out.strip()
    startswith_checker(
        "phmutest.fcb.show_broken_fcbs()- markdown_map is missing key = 5678.", output
    )


def test_end_of_statement_exception():
    """Pass FCB contents that will fail ast.parse()."""
    contents = """\
class RightAnswer:
    '''Provide correct answer to the question'''

    answer = "apples"

    defbogus ask(self, question: str) -> str:
        _ = question
        return self.answer
"""
    # Show that the contents cause an exception.
    with pytest.raises(Exception):
        _ = ast.parse(contents)
    # Run with contents that cause an exception.
    eos = phmutest.fcb.find_end_of_statement(
        contents=contents, role=Role.CODE, open_fence=0, broken_code_line=5
    )
    assert eos == 5


def test_end_of_statement_multiline():
    """Test determine endline of multiline statements."""
    contents = """\
from phmutest.printer import (  # line 1
                    DIFFS,
                    DOC_LOCATION,
                    EXCEPTION_LINE,
                    FRAME,
                    RESULT,
                    TESTFILE_BLOCK_START_LINE,
                    TRACE,
                    Log,
                    LogEntry,
                    bogus,
                )  # line 12

def render_setup_module(
    args: argparse.Namespace,
    block_store: phmutest.select.BlockStore,
) -> str:
    setup_blocks = ""
    for path in args.setup_across_files:
        fileblocks = block_store.get_blocks(path)
        setup_blocks += phmutest.subtest.format_setup_blocks(  # line 21
            args,
            fileblocks,
        )  # line 24
    if setup_blocks:  # Share the names in the setup blocks.
        payload = block_store.get_contents("README.md", 92)  # 26
    total = sum(1,  # line 27
        2,
        3,
        4,
        5,
        6,
        7,
        8,
        9,
        10,
        11,
        12,  # line 38
        13,
        14
    )
"""
    # import items
    end_line1 = phmutest.fcb.find_end_of_statement(
        contents=contents, role=Role.CODE, open_fence=0, broken_code_line=1
    )
    assert end_line1 == 12

    # function call
    end_line2 = phmutest.fcb.find_end_of_statement(
        contents=contents, role=Role.CODE, open_fence=0, broken_code_line=21
    )
    assert end_line2 == 24

    # single line statement
    end_line3 = phmutest.fcb.find_end_of_statement(
        contents=contents, role=Role.CODE, open_fence=0, broken_code_line=26
    )
    assert end_line3 == 26

    # truncated at 12 lines
    end_line4 = phmutest.fcb.find_end_of_statement(
        contents=contents, role=Role.CODE, open_fence=0, broken_code_line=27
    )
    assert end_line4 == 38


def test_repl_end_of_statement():
    contents = """\
>>> fail_bot = WrongAnswer()  # line 1
>>> answer = fail_bot.ask(question="What floats?")
>>> assert answer == "apples"
>>> answer = pass_bot.inquire(query="What floats?")  # line 4
>>> assert answer == "apples"
>>> answer = pass_bot.ask(question="What floats?")
>>> assert answer == "apples"
>>> raiser_bot = RaiserBot()
>>> _ = raiser_bot.ask(question="What floats?")  # line 9
"""
    end_line1 = phmutest.fcb.find_end_of_statement(
        contents=contents, role=Role.SESSION, open_fence=0, broken_code_line=1
    )
    assert end_line1 == 2

    # function call
    end_line2 = phmutest.fcb.find_end_of_statement(
        contents=contents, role=Role.SESSION, open_fence=0, broken_code_line=4
    )
    assert end_line2 == 5

    # single line statement
    end_line3 = phmutest.fcb.find_end_of_statement(
        contents=contents, role=Role.SESSION, open_fence=0, broken_code_line=9
    )
    assert end_line3 == 10
