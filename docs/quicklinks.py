"""Generate quick links Markdown source from README headers."""

from pathlib import Path
from typing import List


def remove_fenced_code_blocks(lines: List[str], fence="```"):
    """Return lines not starting with fence or between fences."""
    skipping = False
    for line in lines:
        if skipping and line.startswith(fence):
            skipping = False
            continue

        if not skipping and line.startswith(fence):
            skipping = True
            continue

        if not skipping:
            yield line


def make_label(title: str) -> str:
    """Make the [] part of a link.  Rewrite if last word is 'option'."""
    # Special handling if the last word of the title is option.
    # The word option indicates the preceding word should have the
    # prefix '--' in the link label since it is a command line option.
    # Titles with '--' seem to break on GitHub pages.
    parts = title.split()
    if parts[-1] == "option":
        parts.pop(-1)
        parts[-1] = "--" + parts[-1]
    title = " ".join(parts)
    return "[" + title + "]"


def make_quick_links(filename: str) -> str:
    """Generate links for a quick links section."""
    header_level = "## "  # note trailing space
    text = Path(filename).read_text(encoding="utf-8")
    lines = text.splitlines()
    # README.md has fenced code blocks that enclose other
    # fenced code blocks.  The outer blocks use ~~~ as the fence.
    # Remove the outer fenced code blocks first.
    lines = remove_fenced_code_blocks(lines, "~~~")
    lines = remove_fenced_code_blocks(lines)
    links = []
    for line in lines:
        if line.startswith(header_level):
            assert "--" not in line, "Please rewrite to avert breakage on Pages."
            title = line.replace(header_level, "")
            label = make_label(title)
            link = title.lower()
            link = link.replace(" ", "-")
            link = "(#" + link + ")"
            links.append(label + link)

    # remove the links for sections before before [Installation]
    ix = links.index("[Installation](#installation)")
    links = links[ix:]
    return " |\n".join(links)


if __name__ == "__main__":
    # To generate quick links, from repository root run: python tests/test_readme.py
    text = make_quick_links("README.md")
    print(text)
    print()
    num_links = text.count("\n") + 1
    print("created {} links, {} characters".format(num_links, len(text)))
