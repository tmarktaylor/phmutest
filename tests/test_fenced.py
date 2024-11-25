"""Test Python info string matching, command line skip, and --report."""

import phmutest.main
import phmutest.summary


def test_python_code_matcher():
    """Test Python code block identification."""
    line = "tests/md/pythonmatch.md"
    phmresult = phmutest.main.command(line)
    want = phmutest.summary.Metrics(
        number_blocks_run=14,
        passed=14,
        failed=0,
        skipped=0,
        suite_errors=0,
        number_of_files=1,
        files_with_no_blocks=0,
        number_of_deselected_blocks=0,
    )
    assert want == phmresult.metrics


def test_python_repl_matcher():
    """Test Python session block identification."""
    line = "tests/md/pythonmatch.md --replmode"
    phmresult = phmutest.main.command(line)
    want = phmutest.summary.Metrics(
        number_blocks_run=16,
        passed=16,
        failed=0,
        skipped=0,
        suite_errors=0,
        number_of_files=1,
        files_with_no_blocks=0,
        number_of_deselected_blocks=0,
    )
    assert want == phmresult.metrics


def test_no_python_code_matches():
    """Test illegal Python code block identification."""
    line = "tests/md/nopythonmatch.md"
    phmresult = phmutest.main.command(line)
    want = phmutest.summary.Metrics(
        number_blocks_run=1,
        passed=1,
        failed=0,
        skipped=0,
        suite_errors=0,
        number_of_files=1,
        files_with_no_blocks=0,
        number_of_deselected_blocks=0,
    )
    assert want == phmresult.metrics


def test_no_python_repl_matches():
    """Test illegal Python session block identification."""
    line = "tests/md/nopythonmatch.md --replmode"
    phmresult = phmutest.main.command(line)
    want = phmutest.summary.Metrics(
        number_blocks_run=1,
        passed=1,
        failed=0,
        skipped=0,
        suite_errors=0,
        number_of_files=1,
        files_with_no_blocks=0,
        number_of_deselected_blocks=0,
    )
    assert want == phmresult.metrics


def test_report(capsys, checker):
    """Run with --report option. Shows"""
    expected = """Command line plus --config file args:
        args.files: 'tests/md/report.md'
        args.skip: 'CHERRIES'
        args.skip: 'CHERRIES'
        args.report: 'True'


        Fenced blocks from tests/md/report.md:
        FencedBlock:
          info_string= python
          lines= 4-7
          role= Role.CODE
          output block= no
          directives= []
        FencedBlock:
          info_string= python
          lines= 10-13
          role= Role.CODE
          output block= lines 18-20
          directives= []
        FencedBlock:
          info_string=
          lines= 18-20
          role= Role.OUTPUT
          directives= []
        FencedBlock:
          info_string= python
          lines= 24-27
          role= Role.CODE
          output block= lines 31-33
          directives= []
        FencedBlock:
          info_string= expected-output
          lines= 31-33
          role= Role.OUTPUT
          directives= []
        FencedBlock:
          info_string= python
          lines= 38-49
          role= Role.CODE
          output block= lines 51-56
          skip patterns= 'CHERRIES'
          directives: (line, type, HTML):
            35, LABEL, <!--phmutest-label example1-outfile-->
            36, SKIP, <!--phmutest-skip-->
        FencedBlock:
          info_string=
          lines= 51-56
          role= Role.OUTPUT
          directives= []
        FencedBlock:
          info_string= yml
          lines= 60-65
          role= Role.NOROLE
          output block= no
          directives: (line, type, HTML):
            58, LABEL, <!--phmutest-label LABEL-->

        Deselected blocks:
        """
    line = "tests/md/report.md --skip CHERRIES CHERRIES --report"
    # Note- duplicate skip pattern CHERRIES is not shown in list of
    #       block skip patterns.
    phmresult = phmutest.main.command(line)
    assert phmresult is None
    checker(expected, capsys.readouterr().out.rstrip())
