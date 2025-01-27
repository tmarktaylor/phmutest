"""Syntax highlight Python code with pygments."""

import re
from typing import Optional


class Highlighter:
    """Encapsulate pygments setup to syntax highlight Python code."""

    # Detect Python exception name in the log.
    _pattern = r"(([A-Z]\w*?Error:)|(AssertionError))"

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
            self.start_color = ""
            self.reset = ""
            self.is_enabled = False  # Not able to do highlighting.
        else:
            # Determine pre and post ANSI terminal sequence strings to set color.
            self.formatter = TerminalTrueColorFormatter(style=style)
            sequences = self.pygments_highlight(
                "ValueError", self.lexer, self.formatter
            ).rstrip()
            self.start_color, self.reset = sequences.split("ValueError")
            self.is_enabled = True  # Able to do highlighting.

    def disable(self) -> None:
        """Don't insert ANSI terminal color sequences into text."""
        self.is_enabled = False  # Not able to do highlighting.

    def highlight(self, text: str) -> str:
        """Return syntax highlighted text."""
        if self.is_enabled:
            text = self.pygments_highlight(text, self.lexer, self.formatter).rstrip()
        return text

    def highlight_exception(self, text: str) -> str:
        """Return text that highlights the exception name."""
        if self.is_enabled:
            repl = self.start_color + r"\1" + self.reset
            text = re.sub(self._pattern, repl, text, count=1)
        return text
