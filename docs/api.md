# API version 0.0.1

## API - phmutest.tool.

```python
class FCBChooser:
    """Choose Markdown FCBs matching criteria."""

    def __init__(self, markdown_filename: str):
        """Gather all the Markdown fenced code blocks in the file.

        Args:
            markdown_filename:
                Path to the Markdown file as a string.
        """
```

```python
    def select(
        self, *, label: str = "", info_string: Optional[str] = None, contains: str = ""
    ) -> List[str]:
        """Return list of contents of each FCB that matches all criteria.

        Args:
            label
                FCB has phmutest label directive 'label'. Empty string means
                select all FCBs (default).

            info_string
                FCB info string matches 'info_string'. Empty string means match
                FCBs with no info string. None means select all FCBs (default).

            contains
                FCB contents have substring 'contains'. Empty string means
                select all FCBs (default).

        Returns:
            List of strings, in file order, of the contents of selected FCBs.
            Empty list if no matches are found.
            Fenced code block strings typically end with a newline.
        """
```

```python
    def contents(self, label: str = "") -> str:
        """Return contents of the labeled fenced code block with label.

        This works the same as phmdoctest.tool.FCBChooser.contents().

        Args:
            label
                FCB has phmutest label directive 'label'.

        Returns:
            Contents of the labeled fenced code block as a string
            or empty string if the label is not found. Fenced code block
            strings typically end with a newline.
        """
```

```python
@dataclass
class LabeledFCB:
    label: str  # the label directive's value
    line: str  # Markdown file line number of block contents
    contents: str  # fenced code block contents


"""Information about a fenced code block that has a label directive."""
```

```python
def labeled_fenced_code_blocks(markdown_filename: str) -> List[LabeledFCB]:
    """Return Markdown fenced code blocks that have label directives.

    Label directives are placed immediately before a fenced code block
    in the Markdown source file. The directive can be placed before any
    fenced code block.
    The label directive is the HTML comment `<!--phmutest-label VALUE-->`
    where VALUE is a string with no embedded whitespace.
    The space before VALUE must be present.
    If there is more than one label directive on the block, the
    label value that occurs earliest in the file is used.

    Args:
        markdown_filename
            Path to the Markdown file.

    Returns:
        List of LabeledFCB objects.

        LabeledFCB is has these fields:

        - label is the value of a label directive
          placed in a HTML comment before the fenced code block.
        - line is the line number in the Markdown file where the block
          starts.
        - contents is the fenced code block contents as a string.
    """
```

```python
def fenced_code_blocks(markdown_filename: str) -> List[str]:
    """Return Markdown fenced code block contents as a list of strings.

    Args:
        markdown_filename
            Path to the Markdown file.

    Returns:
        List of strings, one for the contents of each Markdown
        fenced code block.
    """
```

