"""Fill in code template strings."""

import re
import textwrap
from string import Template
from typing import Mapping


def get_indent(template: str, key: str) -> str:
    """Get whitespace string that indents key."""
    assert key.startswith("$")
    assert key in template, f"Key {key} must be present in the template"
    key = key.replace("$", "[$]", 1)
    indent_pat = r"^([ ]*)" + key + r"$\n"
    m = re.search(pattern=indent_pat, string=template, flags=re.MULTILINE)
    assert m is not None, "A match is always expected here."
    return m.group(1)


def remove_line_with_key(template: str, key: str) -> str:
    """Return template after removing the line containing only the key."""
    assert key.startswith("$")
    key = key.replace("$", "[$]", 1)
    replace_pat = r"^([ ]*" + key + r"$\n)"
    return re.sub(pattern=replace_pat, repl="", string=template, flags=re.MULTILINE)


def remove_trailng_spaces(text: str) -> str:
    """Remove each line's trailing spaces."""
    lines = [line.rstrip(" ") for line in text.splitlines()]
    return "\n".join(lines) + "\n"


def justify(template: str, key: str, text: str) -> str:
    """Determine indent from template and template key, return indented text."""
    assert text, "unittest check"
    indent = get_indent(template, key)
    indented_text = textwrap.indent(text, indent)
    # Remove the indent, if present, from the first line since the key is indented.
    if indented_text.startswith(indent):
        indented_text = indented_text.replace(indent, "", 1)
    return indented_text


def fill_in(template: str, replacements: Mapping[str, str]) -> str:
    """Return filled in template with replacements less the unused/un-truthy keys.

    The keys in the String.Template template start with "$", but
    keys in the mapping passed to Template.substitute do not.
    The replacements keys must not start with "$".
    For keys in the template that are on lines with no other text except indentation
    no replacement is needed.  Lines with such keys will be removed
    from the template.
    A replacement that is an empty string or None is not processed and the
    corresponding key and its line is removed from the template.
    Values for template keys that are embedded in non-whitespace should always be
    present in replacements.
    """
    for k in replacements:
        assert not k.startswith("$"), "easy to make mistake, requires no leading $"
    standalone_keys = re.findall(
        pattern=r"^\s*([$]\w+)$", string=template, flags=re.MULTILINE | re.DOTALL
    )
    for key in standalone_keys:
        replacement_key = key[1:]
        if replacement_key not in replacements:
            template = remove_line_with_key(template, key)
        else:
            # Also remove if there is only whitespace or None value for key.
            if not replacements.get(replacement_key, "").strip():
                template = remove_line_with_key(template, key)
    text = Template(template).substitute(replacements)

    text = remove_trailng_spaces(text)
    # Drop the final newline that comes from the end of the template.
    return chop_final_newline(text)


def chop_final_newline(text: str) -> str:
    """If text ends with a newline, return text less the newline."""
    if text.endswith("\n"):
        return text[:-1]
    else:
        return text
