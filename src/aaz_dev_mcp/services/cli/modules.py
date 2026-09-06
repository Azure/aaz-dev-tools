"""CLI module operations: wraps AzMainManager / AzExtensionManager."""

from __future__ import annotations

from typing import Any, Mapping, Optional

import aaz_dev  # noqa: F401  (injects src/aaz_dev onto sys.path)
from cli.controller.az_module_manager import AzMainManager, AzExtensionManager
from cli.model.view import CLIModule
from utils import exceptions


def _manager(target: str):
    if target == "main":
        return AzMainManager()
    if target == "extension":
        return AzExtensionManager()
    raise exceptions.InvalidAPIUsage(
        f"target must be 'main' or 'extension', got {target!r}")


def get_module(target: str, module_name: str) -> dict:
    """Load the CLI view of a module (the current profile/command tree)."""
    mgr = _manager(target)
    module = mgr.load_module(module_name)
    return module.to_primitive()


def update_module(
    target: str,
    module_name: str,
    profiles: Mapping[str, Any],
    by_patch: bool = True,
) -> dict:
    """Generate CLI code for a module.

    ``profiles`` is the same shape the Flask PUT/PATCH route consumes; e.g.::

        {
          "latest": {
            "name": "latest",
            "commandGroups": {
              "consumption": {
                "names": ["consumption"],
                "commandGroups": {
                  "budget": {
                    "names": ["consumption", "budget"],
                    "commands": {
                      "create": {
                        "names": ["consumption", "budget", "create"],
                        "registered": true,
                        "version": "2024-08-01"
                      }
                    }
                  }
                }
              }
            }
          }
        }

    ``by_patch=True`` (default) merges with the existing module instead of
    overwriting; that matches the PATCH route the UI uses.
    """
    mgr = _manager(target)
    module = CLIModule({"name": module_name, "profiles": profiles})
    module = mgr.update_module(module_name, module.profiles, by_patch=by_patch)
    return module.to_primitive()


def select_command_versions(
    target: str,
    module_name: str,
    profile: str,
    command_versions: Mapping[str, str],
    by_patch: bool = True,
) -> dict:
    """Higher-level helper: pick a version for each named command and
    generate code.

    ``command_versions`` maps space-separated command paths (without the leaf
    being a wait command) to their desired API version, e.g.::

        {
            "consumption budget create": "2024-08-01",
            "consumption budget delete": "2024-08-01",
        }

    All commands are marked ``registered=True``. The resulting profile is
    passed to :func:`update_module` with ``by_patch=True`` so untouched
    commands in the module are preserved.
    """
    command_groups: dict = {}
    for cmd_path, version in command_versions.items():
        parts = cmd_path.strip().split()
        if len(parts) < 2:
            raise exceptions.InvalidAPIUsage(
                f"command path must have at least one group + leaf: {cmd_path!r}")
        group_names = parts[:-1]
        leaf_name = parts[-1]

        cur = command_groups
        for depth, name in enumerate(group_names, start=1):
            full_names = parts[: depth]
            if name not in cur:
                cur[name] = {
                    "names": full_names,
                    "commandGroups": {},
                    "commands": {},
                }
            cur = cur[name]
            # descend into the nested commandGroups dict for next iteration
            if depth < len(group_names):
                cur = cur["commandGroups"]

        cur.setdefault("commands", {})[leaf_name] = {
            "names": parts,
            "registered": True,
            "version": version,
        }

    # prune empty commandGroups/commands placeholders for cleanliness
    _prune(command_groups)

    profiles = {
        profile: {
            "name": profile,
            "commandGroups": command_groups,
        }
    }
    return update_module(target, module_name, profiles, by_patch=by_patch)


def _prune(groups: dict) -> None:
    for group in groups.values():
        sub = group.get("commandGroups")
        if sub:
            _prune(sub)
        if sub == {} or sub is None:
            group.pop("commandGroups", None)
        if not group.get("commands"):
            group.pop("commands", None)
