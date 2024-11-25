import phmutest.summary


def test_empty_log(capsys):
    """Coverage for passing empty log to show_log()."""
    log = []
    phmutest.summary.show_log(log=log, highighter=None)
    output = capsys.readouterr().out.strip()
    assert output == ""
