import argparse
import re
import textwrap
from string import Template
from typing import Mapping

import phmutest.select
import phmutest.skip
from phmutest.direct import Marker
from phmutest.fenced import FencedBlock


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
    assert text, "sanity check"
    indent = get_indent(template, key)
    indented_text = textwrap.indent(text, indent)
    # Remove the indent, if present, from the first line since the key is indented.
    if indented_text.startswith(indent):
        indented_text = indented_text.replace(indent, "", 1)
    return indented_text


def fill_in(template: str, replacements: Mapping[str, str]) -> str:
    """Return filled in the template with replacecments less the unused/un-truthy keys.

    The keys in the String.Template template start with "$", but
    keys in the mapping passed to Template.substitute do not.
    The replacements keys must not start with "$".
    For keys in the template that are on lines with no other text except indentation
    no replacement is needed.  Lines with such keys will be removed
    from the templace.
    A replacement that is an empty string or None is not processed and the
    corresponding key and its line is removed from the template.
    Values for template keys that are embedded in non-whitespace should always be
    present in replacements.
    """
    for k in replacements:
        assert not k.startswith("$"), "easy to make mistake, requires no leading $"
    finder = re.finditer(
        pattern=r"^\s*([$]\w+)$", string=template, flags=re.MULTILINE | re.DOTALL
    )
    standalone_keys = [m.group(1) for m in finder]
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


unconditional_skip_form = """\
        $subtestcontext
            $skip
"""

no_output_form = """\
        $subtestcontext
            $skip
            with _phmPrinter(_phm_log, "$line", $verbose):
                $code
"""

skipif_form = """\
        $subtestcontext
            $skip
            else:
                with _phmPrinter(_phm_log, "$line", $verbose):
                    $code
"""


expected_output_form = '''\
        $subtestcontext
            $skip
            with _phmPrinter(_phm_log, "$line", $verbose) as _phm_printer:
                $code
                # line $outline
                _phm_expected_str = """\\
$output
"""
                _phm_printer.cancel_print_capture_on_error()
                _phm_testcase.assertEqual(_phm_expected_str, _phm_printer.stdout())
'''


skipif_expected_output_form = '''\
        $subtestcontext
            $skip
            else:
                with _phmPrinter(_phm_log, "$line", $verbose) as _phm_printer:
                    $code
                    # line $outline
                    _phm_expected_str = """\\
$output
"""
                    _phm_printer.cancel_print_capture_on_error()
                    _phm_testcase.assertEqual(_phm_expected_str, _phm_printer.stdout())
'''


def render_code_block(
    args: argparse.Namespace,
    block: FencedBlock,
    doc_location: str,
    nosubtest: bool,
) -> str:
    """Generate source to test a Python fenced code block."""

    # nosubtest=True means don't wrap block with self.subTest so that
    # failures in blocks rendered in setUpClass don't abort the entire file.
    template = None
    replacements = {}
    replacements["line"] = doc_location
    replacements["verbose"] = args.progress
    if nosubtest:
        replacements["subtestcontext"] = "if True:"
    else:
        replacements["subtestcontext"] = f'with self.subTest(msg="{doc_location}"):'
    skipinfo = phmutest.skip.skipper(args, block, doc_location)
    skipping_output = block.output and (block.output.has_directive(Marker.SKIP))

    # For an unconditional skip we just log, print if verbose,
    # and nothing more. So use the unconditional_skip_form and
    # don't put in any of the caller's code block.
    if skipinfo:
        if skipinfo.is_conditional:
            if block.output and not skipping_output:
                template = skipif_expected_output_form
            else:
                template = skipif_form
        else:
            template = unconditional_skip_form
    else:
        if block.output and not skipping_output:
            template = expected_output_form
        else:
            template = no_output_form

    if skipinfo:
        replacements["skip"] = justify(template, "$skip", skipinfo.code)
    if template != unconditional_skip_form:
        code = chop_final_newline(block.contents)
        # Account for empty or all whitespace code block contents.
        if not len(code.strip()):
            code = "pass  # no FCB contents"
        replacements["code"] = justify(template, "$code", code)

        if block.output and not skipping_output:
            replacements["outline"] = str(block.output.line)
            expected_output = block.get_output_contents()
            replacements["output"] = chop_final_newline(expected_output)

    return fill_in(template, replacements)


# Added to code block file location to
# indicate the code block was run in a TestCase fixture.
SETUP_SUFFIX = " setup"  # setUp and setUpModule
TEARDOWN_SUFFIX = " teardown"  # tearDown and tearDownModule


def make_location_string(block: FencedBlock, built_from: str) -> str:
    """Shows Markdown file, line number, and directive label of the FCB."""
    label_directive = block.get_directive(Marker.LABEL)
    if label_directive is not None:
        label = " " + label_directive.value
    else:
        label = ""
    return f"{built_from}:{block.line}{label}"


def make_comment_string(doc_location: str) -> str:
    """Comment line showing Markdown file, line number, and directive label."""
    return f"        # ------ {doc_location} ------"


def format_code_blocks(
    args: argparse.Namespace,
    fileblocks: phmutest.select.FileBlocks,
) -> str:
    """Generate source for the Python example code FCBs."""
    parts = []
    code_blocks = []
    for block in fileblocks.selected:
        # Exclude setup and teardown blocks since they get handled elsewhere.
        if not (
            block.has_directive(Marker.SETUP) or block.has_directive(Marker.TEARDOWN)
        ):
            code_blocks.append(block)
    for block in code_blocks:
        doc_location = make_location_string(block, fileblocks.built_from)
        comment = make_comment_string(doc_location)
        parts.append(comment)
        parts.append(
            render_code_block(
                args,
                block,
                doc_location,
                nosubtest=False,
            )
        )
        parts.append("")
    return "\n".join(parts)


def format_setup_blocks(
    args: argparse.Namespace,
    fileblocks: phmutest.select.FileBlocks,
) -> str:
    """Generate source for the Python example code setup FCBs."""
    parts = []
    setup_blocks = [
        block for block in fileblocks.selected if block.has_directive(Marker.SETUP)
    ]
    for block in setup_blocks:
        doc_location = make_location_string(block, fileblocks.built_from)
        comment = make_comment_string(doc_location)
        parts.append(comment)
        parts.append(
            render_code_block(
                args,
                block,
                doc_location + SETUP_SUFFIX,
                nosubtest=True,
            )
        )
        parts.append("")
    return "\n".join(parts)


def format_teardown_blocks(
    args: argparse.Namespace,
    fileblocks: phmutest.select.FileBlocks,
) -> str:
    """Generate source for the Python example code teardown FCBs."""
    parts = []
    teardown_blocks = [
        block for block in fileblocks.selected if block.has_directive(Marker.TEARDOWN)
    ]
    for block in teardown_blocks:
        doc_location = make_location_string(block, fileblocks.built_from)
        comment = make_comment_string(doc_location)
        parts.append(comment)
        parts.append(
            render_code_block(
                args,
                block,
                doc_location + TEARDOWN_SUFFIX,
                nosubtest=True,
            )
        )
        parts.append("")
    return "\n".join(parts)
