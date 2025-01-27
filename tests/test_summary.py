"""Test show_log() output for empty log."""

import phmutest.summary


def test_empty_log(capsys):
    """Coverage for passing empty log to show_log()."""
    log = []
    phmutest.summary.show_log(log=log, highighter=None, use_color=False)
    output = capsys.readouterr().out.strip()
    assert output == ""
