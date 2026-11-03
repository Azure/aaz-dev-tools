"""Example management on workspace command leaves.

Mirrors backend ``command/controller/workspace_manager.py`` example operations
plus ``swagger/controller/example_generator.py`` for swagger-derived examples.
"""

from __future__ import annotations

import aaz_dev  # noqa: F401  (injects src/aaz_dev onto sys.path)
from command.controller.workspace_manager import WorkspaceManager
from utils import exceptions


def _find_leaf(manager: WorkspaceManager, command: list[str]):
    if not command or len(command) < 2:
        raise exceptions.InvalidAPIUsage(
            "command path must include at least one group and a leaf")
    *node_names, leaf_name = command
    leaf = manager.find_command_tree_leaf(*node_names, leaf_name)
    if not leaf:
        raise exceptions.ResourceNotFind(
            f"Command not found: {' '.join(command)}")
    return leaf


def list_command_examples(name: str, command: list[str]) -> list[dict]:
    """Return the current examples on a leaf command."""
    manager = WorkspaceManager(name)
    manager.load()
    leaf = _find_leaf(manager, command)
    return [e.to_primitive() for e in (leaf.examples or [])]


def set_command_examples(
    name: str,
    command: list[str],
    examples: list[dict],
) -> list[dict]:
    """Replace the full example list on a leaf command.

    Each example must have ``{"name": str, "commands": [str, ...]}``.
    Pass an empty list to clear examples.
    """
    manager = WorkspaceManager(name)
    manager.load()
    leaf = _find_leaf(manager, command)
    leaf = manager.update_command_tree_leaf_examples(*leaf.names, examples=examples)
    manager.save()
    return [e.to_primitive() for e in (leaf.examples or [])]


def add_command_example(
    name: str,
    command: list[str],
    example_name: str,
    commands: list[str],
) -> list[dict]:
    """Append a single manual example to a leaf command.

    - example_name: short label shown in CLI help
    - commands: list of CLI invocation strings, e.g.
      ['consumption budget create -n my-budget --amount 100 ...']
    """
    if not example_name or not commands:
        raise exceptions.InvalidAPIUsage(
            "example_name and commands must be non-empty")
    manager = WorkspaceManager(name)
    manager.load()
    leaf = _find_leaf(manager, command)
    existing = [e.to_primitive() for e in (leaf.examples or [])]
    existing.append({"name": example_name, "commands": list(commands)})
    leaf = manager.update_command_tree_leaf_examples(*leaf.names, examples=existing)
    manager.save()
    return [e.to_primitive() for e in (leaf.examples or [])]


def add_examples_from_swagger(
    name: str,
    command: list[str],
    replace: bool = False,
) -> list[dict]:
    """Generate examples from the OpenAPI specification ('By OpenAPI Specification'
    button in the UI) and persist them on the leaf.

    - replace=False (default): append generated examples to any existing ones.
    - replace=True: drop existing examples first.
    """
    manager = WorkspaceManager(name)
    manager.load()
    leaf = _find_leaf(manager, command)
    cfg_editor = manager.load_cfg_editor_by_command(leaf)
    cfg_command = cfg_editor.find_command(*leaf.names)
    if not cfg_command:
        raise exceptions.ResourceNotFind(
            f"Command config not found: {' '.join(command)}")

    generated = manager.generate_examples_by_swagger(leaf, cfg_command)
    generated_dicts = [e.to_primitive() for e in generated]

    if replace:
        merged = generated_dicts
    else:
        merged = [e.to_primitive() for e in (leaf.examples or [])]
        merged.extend(generated_dicts)

    leaf = manager.update_command_tree_leaf_examples(*leaf.names, examples=merged)
    manager.save()
    return [e.to_primitive() for e in (leaf.examples or [])]
