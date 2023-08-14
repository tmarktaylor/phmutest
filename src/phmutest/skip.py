"""Process skip directives. Encapsulate access to Python standard library sys."""
import argparse
import sys
from dataclasses import dataclass
from typing import Any, MutableMapping, Optional

import phmutest.subtest
from phmutest.direct import Marker
from phmutest.fenced import FencedBlock


class SysTool:
    """Access Python standard library sys variables without an explicit import sys."""

    @staticmethod
    def stderr_printer(text: str) -> None:
        """Print text to stderr while avoiding an extra import sys in the testfile."""
        # Note- Using this function instead of adding import sys avoids:
        # UnboundLocalError: local variable 'sys' referenced before assignment.
        # It should not be necessary because the generated testfile has import
        # sys at the top. Don't know why, but it does not occur in the
        # generated setUpModule() with verbose printing. A difference is
        # the UnboundLocalError occurs within a "with self.subTest"
        # context manager.
        # The file=sys.stderr was needed only for verbose printing selected
        # by the --progress command line option.
        print(text, file=sys.stderr)

    @staticmethod
    def version_info() -> Any:
        """Get sys.version_info while avoiding an extra import sys in the testfile."""
        # See rationale above in stderr_printer().
        return sys.version_info


sys_tool = SysTool()
"""This is imported as _phm_sys in the generated testfile."""


@dataclass
class SkipInfo:
    """Information from a skip directive used to generate Python code."""

    code: str
    reason: str
    is_conditional: bool


unconditional_form = """\
_phm_log.append(["$line", "skip", "$log_reason"])
$print
"""

conditional_form = """\
if $condition:
    _phm_log.append(["$line", "skip", "$log_reason"])
    $print
"""


def make_detailed_reason(doc_location: str, log_reason: str) -> str:
    """Combine the document location and the reason for skipping into one string."""
    return f'"{doc_location} {log_reason}"'


def make_replacements(
    doc_location: str, log_reason: str, verbose: bool
) -> MutableMapping[str, str]:
    """Create mapping for Template string replacement."""
    replacements = dict(line=doc_location, log_reason=log_reason)
    if verbose:
        replacements[
            "print"
        ] = f'_phm_sys.stderr_printer("{doc_location} ... skip   {log_reason}")'
    return replacements


def always_skip(reason: str, doc_location: str, verbose: bool) -> SkipInfo:
    """Unconditionally skip the block. No code. Just log/print the block and reason."""
    replacements = make_replacements(doc_location, reason, verbose)
    code = phmutest.subtest.fill_in(unconditional_form, replacements)
    return SkipInfo(
        code=code,
        reason=make_detailed_reason(doc_location, reason),
        is_conditional=False,
    )


def skipif(minor_version: int, doc_location: str, verbose: bool) -> SkipInfo:
    """Gather information to generate code for phmutest-skipif directive."""
    log_reason = f"requires Python >= 3.{minor_version}"
    replacements = make_replacements(doc_location, log_reason, verbose)
    replacements["condition"] = f"_phm_sys.version_info() < (3, {minor_version})"
    code = phmutest.subtest.fill_in(conditional_form, replacements)
    return SkipInfo(
        code=code,
        reason=make_detailed_reason(doc_location, log_reason),
        is_conditional=True,
    )


def skipper(
    args: argparse.Namespace,
    block: FencedBlock,
    doc_location: str,
) -> Optional[SkipInfo]:
    """Return data due to command line skip or skip directive otherwise None."""

    skip_info = None
    if block.skip_patterns:
        reason = "--skip " + ", ".join(block.skip_patterns)
        skip_info = always_skip(reason, doc_location, args.progress)

    else:
        if directive := block.get_directive(Marker.SKIP, Marker.SKIPIF_PYVERSION):
            if directive.type == Marker.SKIP:
                reason = directive.literal[4:-3]  # lose the directive <!-- and -->.
                skip_info = always_skip(reason, doc_location, args.progress)
            else:
                assert directive.type == Marker.SKIPIF_PYVERSION, "sanity check"
                minor_version = int(directive.value)
                skip_info = skipif(minor_version, doc_location, args.progress)
    return skip_info
