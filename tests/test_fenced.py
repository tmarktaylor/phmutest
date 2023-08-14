"""Test Python info string matching, command line skip, and --report."""
import phmutest.main


def test_python_code_matcher():
    """Test Python block identification."""
    args = "tests/md/pythonmatch.md".split()
    phmresult = phmutest.main.main(args)
    want = phmutest.summary.Metrics(
        number_blocks_run=7,
        passed=7,
        failed=0,
        skipped=0,
        suite_errors=0,
        number_of_files=1,
        files_with_no_blocks=0,
        number_of_deselected_blocks=0,
    )
    assert want == phmresult.metrics


def test_python_repl_matcher():
    """Test Python block identification."""
    args = "tests/md/pythonmatch.md --replmode".split()
    phmresult = phmutest.main.main(args)
    want = phmutest.summary.Metrics(
        number_blocks_run=8,
        passed=8,
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
          lines= 6-9
          role= Role.CODE
          output block= no
          directives= []
        FencedBlock:
          info_string= python
          lines= 12-15
          role= Role.CODE
          output block= lines 20-22
          directives= []
        FencedBlock:
          info_string=
          lines= 20-22
          role= Role.OUTPUT
          directives= []
        FencedBlock:
          info_string= python
          lines= 26-29
          role= Role.CODE
          output block= lines 32-34
          directives= []
        FencedBlock:
          info_string=
          lines= 32-34
          role= Role.OUTPUT
          directives= []
        FencedBlock:
          info_string= python
          lines= 38-49
          role= Role.CODE
          output block= lines 51-56
          skip patterns= 'CHERRIES'
          directives: (line, type, HTML):
            36, LABEL, <!--phmutest-label example1-outfile-->
            37, SKIP, <!--phmutest-skip-->
        FencedBlock:
          info_string=
          lines= 51-56
          role= Role.OUTPUT
          directives= []
        FencedBlock:
          info_string= yml
          lines= 59-64
          role= Role.NOROLE
          output block= no
          directives: (line, type, HTML):
            58, LABEL, <!--phmutest-label LABEL-->

        Deselected blocks:
        """
    command = "tests/md/report.md --skip CHERRIES CHERRIES --report"
    # Note- duplicate skip pattern CHERRIES is not shown in list of
    #       block skip patterns.
    phmresult = phmutest.main.main(command.split())
    assert phmresult is None
    checker(expected, capsys.readouterr().out.rstrip())
