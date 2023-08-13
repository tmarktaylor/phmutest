"""Imported by the generated test file to manage test module globals."""
import inspect
import sys
import types
from typing import Any, Dict, List, Mapping, MutableMapping, Optional, Set

Additions = MutableMapping[str, Any]


class Globals:
    """Add, remove, and keep track of globals added to a module.

    Dynamically add and remove values as module attributes.
    The attribute names are stored in the set global_names.
    The attribute values are stored in the module name passed
    to the constructor.
    self.m points to the module.
    """

    def __init__(self, module_name: str, shareid: str = ""):
        """Keep track of pre-existing attribute. Enable debug printing."""
        self.already_exists = (
            "phmutest- Not allowed to replace global name {} because\n"
            "it existed when this instance was created."
        )
        self.no_originals = (
            "phmutest- no pre-existing globals/module attributes can be managed."
        )
        self.no_extras = "phmutest- current attributes == original + global_names."
        if shareid:
            self.shareidmsg = "sharing-" + shareid
        else:
            self.shareidmsg = ""
        if self.shareidmsg:
            print(self.shareidmsg, "initialized", file=sys.stderr)
        self.m = sys.modules.copy()[module_name]
        self.original_attributes = set([name for name, _ in inspect.getmembers(self.m)])
        self.global_names: Set[str] = set()

    def check_attribute_name(self, name: str) -> None:
        """Check that name was not a module attribute at __init__() time."""
        if name in self.original_attributes:
            raise AttributeError(self.already_exists.format(name))

    def check_integrity(self, existing_names: Optional[Set[str]] = None) -> None:
        """Check module's attributes are pre-existing or in global_names.

        existing_names are names that were added to another coexisting
        instance of Globals.  They are not in this instance's self.global_names
        but they are module attributes.
        """
        current_attributes = set([name for name, _ in inspect.getmembers(self.m)])
        if not self.original_attributes.isdisjoint(self.global_names):
            raise AttributeError(self.no_originals)
        if current_attributes != self.original_attributes.union(self.global_names):
            extras = current_attributes - self.global_names - self.original_attributes
            if existing_names is not None:
                extras -= existing_names
            if extras:
                formatted_extras = "\n  extras= " + ", ".join([e for e in extras])
                raise AttributeError(self.no_extras + formatted_extras)

    def show_global_names(self, built_from: str) -> None:
        """Print the names of module globals currently in the global_names."""
        if self.shareidmsg:
            location = self.make_location(built_from)
            names = ", ".join(self.global_names)
            if names:
                print(location, "names=", names, file=sys.stderr)
            else:
                print(location, "is empty", file=sys.stderr)

    def clear(self) -> None:
        """Remove the global_names items from the module globals."""
        names = ", ".join(list(self.global_names))
        if self.shareidmsg:
            print(self.shareidmsg, "clearing=", names, file=sys.stderr)
        for name in self.global_names:
            self.check_attribute_name(name)
            delattr(self.m, name)
        self.global_names.clear()
        self.show_global_names(built_from="")

    def copy(self) -> Additions:
        """Return a shallow copy of the global_names/values."""
        if self.shareidmsg:
            print(self.shareidmsg, "returning a copy", file=sys.stderr)
        shallow_copy = dict()
        for name in self.global_names:
            shallow_copy[name] = getattr(self.m, name)
        return shallow_copy

    def get_names(self) -> Set[str]:
        """Return the global_names."""
        return self.global_names

    def update(
        self,
        additions: Additions,
        built_from: str = "",
        existing_names: Optional[Set[str]] = None,
    ) -> None:
        """Add and keep track of additions to the module globals.

        additions is a mapping of names and values of variables that
        should be added to the module globals.
        existing_names are names that have been added to the module
        by another instance of Globals since this instance was
        created.  Such names are not is this instance's self.global_names
        and are not original attributes of the module.
        """
        if additions is None:
            raise ValueError("phmutest- need additions to do an update")
        if not isinstance(additions, dict):
            raise TypeError("phmutest- must be a mapping")
        # Remove some items from additions that don't belong in global_names.
        _ = additions.pop("self", None)
        _ = additions.pop("cls", None)
        _ = additions.pop("_phm_expected_str", None)
        _ = additions.pop("_phm_printer", None)
        _ = additions.pop("_phm_fixture", None)

        # Module level imports by the generated test file should not be
        # modified. If they are present in additions they will
        # cause check_attribute_name() to raise an exception.
        # Users might have one or more of them in their code block.
        # So we remove them from additions.
        if "contextlib" in additions and "contextlib" in self.original_attributes:
            _ = additions.pop("contextlib", None)
        if "io" in additions and "io" in self.original_attributes:
            _ = additions.pop("io", None)
        if "sys" in additions and "sys" in self.original_attributes:
            _ = additions.pop("sys", None)
        if "unittest" in additions and "unittest" in self.original_attributes:
            _ = additions.pop("unittest", None)
        added_names = ", ".join(additions.keys())
        self.print_sharing(built_from, added_names)
        self._omit_already_imported(additions)
        for k, v in additions.items():
            self.check_attribute_name(k)
            setattr(self.m, k, v)
            self.global_names.add(k)
        self.check_integrity(existing_names=existing_names)
        self.show_global_names(built_from)

    def make_location(self, built_from: str) -> str:
        """Optionally append filename to the sharing debug message prefix."""
        if built_from:
            location = self.shareidmsg + "-" + built_from
        else:
            location = self.shareidmsg
        return location

    def print_sharing(self, built_from: str, added_names: str) -> None:
        """Print verbosity message showing the added names and their source."""
        if self.shareidmsg:
            if added_names:
                location = self.make_location(built_from)
                print(location, "adding=", added_names, file=sys.stderr)

    def _omit_already_imported(self, additions: Additions) -> None:
        """Don't add already imported modules.

        If there is more than one instance of Globals on the
        same module it is possible that both will add the same name.
        This will cause check_attribute_name() to raise an exception.
        If the offending name is an imported module, the code below will
        prevent that addition.
        """
        names_not_added = []
        for k, v in additions.items():
            existing_module = getattr(self.m, k, None)
            if (
                existing_module is not None
                and isinstance(existing_module, types.ModuleType)
                and (id((existing_module)) == id(v))
            ):
                names_not_added.append(k)
        for k in names_not_added:
            if self.shareidmsg:
                print(
                    self.shareidmsg,
                    "Not adding",
                    repr(k),
                    "since it already exists in module.",
                    file=sys.stderr,
                )
            _ = additions.pop(k, None)


class AssignmentExtractor:
    """Determine names and values assigned in a section of code.

    Call start(locals().keys()) at the beginning of the section of code.
    Calling finish(locals()) stores all the local names assigned
    since the start() call plus the values as a mapping to self.assignments.
    """

    def __init__(self) -> None:
        self.start_names: Set[str] = set()
        self.assignments: Dict[str, Any] = {}

    def start(self, start_names: List[str]) -> None:
        """Save the names returned by built in function locals().keys()."""
        self.start_names = set(start_names)

    def finish(self, finish_locals: Mapping[str, Any]) -> None:
        """Copy names and values assigned since start() was called."""
        finish_names = set(finish_locals.keys())
        added_names = finish_names - self.start_names
        for k in added_names:
            self.assignments[k] = finish_locals[k]
