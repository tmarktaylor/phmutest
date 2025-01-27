"""Import user's fixture function given the relative dotted path."""

import importlib.util
import sys
from pathlib import Path

from phmutest.fixture import FixtureFunction


def python_file_importer(file_path, module_name):  # type: ignore
    """Import .py source file directly.  See importlib Examples."""
    spec = importlib.util.spec_from_file_location(module_name, file_path)
    module = importlib.util.module_from_spec(spec)  # type: ignore
    sys.modules[module_name] = module
    spec.loader.exec_module(module)  # type: ignore
    return module


def fixture_function_importer(dotted_path_string: str) -> FixtureFunction:
    """Return imported user's fixture function given its relative dotted path.

    The dotted_path has components separated by ".".
    The last component is the function name.
    The next to last component is the python file name without the .py suffix.
    The preceding components identify parent folders. Folders should be
    relative to the current working directory which is typically the
    project root.
    """
    dotted_path = Path(dotted_path_string)
    function = dotted_path.suffix  # pathlib Rocks!
    function_name = function[1:]
    dotted_file_name = dotted_path.stem
    file_name = dotted_file_name.replace(".", "/")
    file_path = Path(file_name).with_suffix(".py")
    module_name = dotted_file_name.replace(".", "_")
    module = python_file_importer(file_path, module_name)  # type: ignore
    f = getattr(module, function_name)
    return f  # type: ignore
