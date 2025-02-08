"""Test cases for phmutest/color.py."""

import pytest

import phmutest.color
import phmutest.syntax


@pytest.mark.skipif(not phmutest.color.is_enabled, reason="needs color extra")
def test_colorize_result(monkeypatch):
    """Check test result colorization."""
    assert len(phmutest.color.colorize_result(item="pass", use_color=True)) > 4
    assert len(phmutest.color.colorize_result(item="failed", use_color=True)) > 6
    assert len(phmutest.color.colorize_result(item="error", use_color=True)) > 5
    assert len(phmutest.color.colorize_result(item="skip", use_color=True)) > 4

    # Only one of "pass", "failed", "error", "skip" is colorized.
    text = phmutest.color.colorize_result(item="pass  ", use_color=True)
    assert text[-2:] == "  "
    text = phmutest.color.colorize_result(item="failed  ", use_color=True)
    assert text[-2:] == "  "
    text = phmutest.color.colorize_result(item="error  ", use_color=True)
    assert text[-2:] == "  "
    text = phmutest.color.colorize_result(item="skip  ", use_color=True)
    assert text[-2:] == "  "

    # Item need only start with "pass", "failed", "error", "skip".
    text = phmutest.color.colorize_result(item="passer", use_color=True)
    assert len(text) > 6
    assert text[-2:] == "er"

    # items that should not be colorized
    assert phmutest.color.colorize_result(item="", use_color=True) == ""
    assert phmutest.color.colorize_result(item="past", use_color=True) == "past"
    assert phmutest.color.colorize_result(item="ifailed", use_color=True) == "ifailed"
    assert phmutest.color.colorize_result(item="01234", use_color=True) == "01234"
    assert phmutest.color.colorize_result(item="  pass", use_color=True) == "  pass"
    assert phmutest.color.colorize_result(item="  error", use_color=True) == "  error"


def test_highlighter():
    """Show Highlighte() with no name is disabled."""
    h = phmutest.syntax.Highlighter()
    assert not h.is_enabled
    assert h.highlight("if False:") == "if False:"
