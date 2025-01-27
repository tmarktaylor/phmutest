"""Statement coverage for fcb.py markdown map missing key error message."""

import phmutest.cases
import phmutest.config
import phmutest.fcb
import phmutest.main


def test_map_missing_key(capsys, startswith_checker):
    """Markdown map missing key error message."""
    parser = phmutest.main.main_argparser()
    line = "tests/md/project.md"
    args = line.split()
    known_args = parser.parse_known_args(args)
    settings = phmutest.config.get_settings(known_args)
    args = settings.args
    block_store = phmutest.select.BlockStore(settings.args)
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
