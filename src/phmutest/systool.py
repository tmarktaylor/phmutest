"""Access Python standard library sys variables without an explicit import sys."""

import sys
from typing import Any


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
