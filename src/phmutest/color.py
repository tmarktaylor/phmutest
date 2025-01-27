"""Colorize a test result string."""

import os

try:
    from colorama import Fore  # type: ignore

    if os.name == "nt":
        from colorama import just_fix_windows_console

        just_fix_windows_console()
    is_enabled = True
    result_colors = {
        "pass": Fore.GREEN,
        "failed": Fore.LIGHTCYAN_EX,
        "error": Fore.RED,
        "skip": Fore.YELLOW,
    }
    """Test result status value and associated colorama Fore color object."""

    def colorize_result(item: str, use_color: bool = False) -> str:
        """Colorize matching initial substring of item by adding terminal codes."""

        if is_enabled and use_color:
            # Check if item starts with one of the result_colors keys.
            # If so, colorize that part of item.
            # Otherwise, return item unmodified.
            for result in result_colors:
                if item.startswith(result):
                    item = item.replace(
                        result, "".join([result_colors[result], result, Fore.RESET])
                    )
                    break
        return item

except (ModuleNotFoundError, ImportError):
    is_enabled = False
