"""Make sections and demos link page."""

import re
import textwrap
from pathlib import Path


def make_nav_links():
    """Create a Markdown page with navigation links from mkdocs.yml."""
    text = Path("mkdocs.yml").read_text(encoding="utf-8")
    lines = []
    # The 'un-navd' section should be last in the file.
    # The pattern omits the 'un-navd' section at the end since there is
    # only one blank line before the end of file.
    sections = re.findall(
        pattern=r"^\s*- \w*:$.*?\n\n", string=text, flags=re.MULTILINE | re.DOTALL
    )
    lines.append("# Sections and Demos")
    for s in sections:
        lines.append("")
        s = textwrap.dedent(s)
        for g in s.splitlines():
            if g:
                if g.startswith("-"):
                    # Make the heading.
                    g = g.replace("-", "##")
                    g = g.replace(":", "\n")
                else:
                    # Make the link.
                    g = g.replace("    - '", "- [")
                    g = g.replace("': ", "](")
                    g = g.replace("' : ", "](")
                    # Skip files not in docs folder.
                    # Remove docs/ from pathname since paths are relative to docs.
                    if "(docs/" in g:
                        g = g.replace("(docs/", "(")
                    else:
                        continue
                    g += ")"
                lines.append(g)
    lines.append("")  # Final newline.
    return "\n".join(lines)


if __name__ == "__main__":
    # Generate navigation links for docs/demos.md.
    import unittest

    testcase = unittest.TestCase()
    testcase.maxDiff = None
    want = make_nav_links()
    print(want)
    print()
    print("checking docs/demos.md...")
    got = Path("docs/demos.md").read_text(encoding="utf-8")
    testcase.assertEqual(want, got)
