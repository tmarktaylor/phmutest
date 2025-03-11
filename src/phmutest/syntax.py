"""Syntax highlight Python code with pygments."""

from typing import Optional


class Highlighter:
    """Encapsulate pygments setup to syntax highlight Python code."""

    def __init__(self, style: Optional[str] = None):
        try:
            from pygments import highlight  # type: ignore
            from pygments.formatters import TerminalTrueColorFormatter  # type: ignore
            from pygments.lexers import Python3Lexer  # type: ignore

            self.pygments_highlight = highlight  # avoid flake8 error
            self.lexer = Python3Lexer()
        except ModuleNotFoundError:
            self.pygments_highlight = None
            self.lexer = None
        if self.pygments_highlight is None or style is None:
            self.formatter = None
            self.is_enabled = False  # Not able to do highlighting.
        else:
            self.formatter = TerminalTrueColorFormatter(style=style)
            self.is_enabled = True  # Able to do highlighting.

    def disable(self) -> None:
        """Don't insert ANSI terminal color sequences into text."""
        self.is_enabled = False  # Not able to do highlighting.

    def highlight(self, text: str) -> str:
        """Return syntax highlighted text."""
        if self.is_enabled:
            text = self.pygments_highlight(text, self.lexer, self.formatter).rstrip()
        return text
