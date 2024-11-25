"""Generate code to test Python FCBs."""

import argparse
import re

import phmutest.fillin
import phmutest.select
import phmutest.skip
from phmutest.direct import Marker
from phmutest.fenced import FencedBlock

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
