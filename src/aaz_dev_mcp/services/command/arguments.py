"""Argument editing on workspace command leaves.

Mirrors backend ``command/controller/workspace_cfg_editor.py`` argument
operations: patch, flatten, unflatten.
"""

from __future__ import annotations

from typing import Any, Optional

import aaz_dev  # noqa: F401  (injects src/aaz_dev onto sys.path)
from command.controller.workspace_manager import WorkspaceManager
from utils import exceptions


def _load_cfg_editor_for_command(manager: WorkspaceManager, command: list[str]):
    """Resolve a command path (no 'aaz' root) to (cfg_editor, *node_names, leaf_name)."""
    if not command or len(command) < 2:
        raise exceptions.InvalidAPIUsage(
            "command path must include at least one group and a leaf")
    *node_names, leaf_name = command
    leaf = manager.find_command_tree_leaf(*node_names, leaf_name)
    if not leaf:
        raise exceptions.ResourceNotFind(
            f"Command not found: {' '.join(command)}")
    cfg_editor = manager.load_cfg_editor_by_command(leaf)
    return cfg_editor, node_names, leaf_name


def update_argument(
    name: str,
    command: list[str],
    arg_var: str,
    options: Optional[list[str]] = None,
    singular_options: Optional[list[str]] = None,
    help: Optional[dict] = None,
    stage: Optional[str] = None,
    hide: Optional[bool] = None,
    group: Optional[str] = None,
    clear_group: bool = False,
    default: Any = "__unset__",
    required: Optional[bool] = None,  # currently unused; reserved
) -> dict:
    """Patch a single argument of a leaf command.

    Mirrors PATCH /Workspaces/<ws>/.../Arguments/<arg_var> in the editor API.

    - command: full command path without the 'aaz' root, e.g.
      ['consumption', 'budget', 'create'].
    - arg_var: argument variable, e.g. '$Path.budgetName' or
      '$parameters.properties.timePeriod'. Inspect with the editor UI or
      look at the workspace's cfg.json.
    - options: replace the argument's option list (e.g. ['name', 'n', 'budget-name']
      to add aliases to --budget-name).
    - singular_options: only valid for array / cls args; used by the UI when
      promoting a multi-value option to also accept a singular form.
    - help: {'short': str, 'lines': [str], 'refCommands': [str]}.
    - stage: 'Stable' | 'Preview' | 'Experimental'.
    - hide: bool. (Cannot hide required arguments.)
    - group: arg group name. Pass a non-empty string to set; pass
      ``clear_group=True`` to remove the arg from any named group
      (it then appears in the default un-named group).
    - clear_group: if True, set ``arg.group`` back to None. Takes
      precedence over ``group``. Use this instead of passing an empty
      string, which some MCP transports mangle.
    - default: pass any JSON value, or null to clear; omit (sentinel) to leave alone.
    """
    manager = WorkspaceManager(name)
    manager.load()
    cfg_editor, node_names, leaf_name = _load_cfg_editor_for_command(manager, command)
    arg, _ = cfg_editor.find_arg_by_var(*node_names, leaf_name, arg_var=arg_var)
    if not arg:
        raise exceptions.ResourceNotFind(
            f"Argument not found on {' '.join(command)}: {arg_var}")

    kwargs: dict[str, Any] = {}
    if options is not None:
        kwargs["options"] = options
    if singular_options is not None:
        kwargs["singularOptions"] = singular_options
    if help is not None:
        kwargs["help"] = help
    if stage is not None:
        kwargs["stage"] = stage
    if hide is not None:
        kwargs["hide"] = hide
    if clear_group:
        kwargs["group"] = None
    elif group is not None:
        kwargs["group"] = group
    if default != "__unset__":
        kwargs["default"] = default
    if not kwargs:
        raise exceptions.InvalidAPIUsage(
            "update_argument requires at least one field to change")

    cfg_editor.update_arg_by_var(*node_names, leaf_name, arg_var=arg_var, **kwargs)
    manager.save()
    arg, _ = cfg_editor.find_arg_by_var(*node_names, leaf_name, arg_var=arg_var)
    return arg.to_primitive()


def flatten_argument(
    name: str,
    command: list[str],
    arg_var: str,
    sub_args_options: Optional[dict[str, list[str]]] = None,
) -> dict:
    """Flatten an object argument into its sub-arguments.

    Mirrors POST /Workspaces/<ws>/.../Arguments/<arg_var>/Flatten.

    Example: flatten ``$parameters.properties.timePeriod`` on
    ``consumption budget create`` so that the user sees ``--start-date``
    and ``--end-date`` directly instead of ``--time-period``.

    - command: full command path without the 'aaz' root.
    - arg_var: object argument variable to flatten.
    - sub_args_options: optional ``{sub_arg_var: [option, ...]}`` mapping
      to rename the flattened sub-arguments.
    """
    manager = WorkspaceManager(name)
    manager.load()
    cfg_editor, node_names, leaf_name = _load_cfg_editor_for_command(manager, command)
    arg, _ = cfg_editor.find_arg_by_var(*node_names, leaf_name, arg_var=arg_var)
    if not arg:
        raise exceptions.ResourceNotFind(
            f"Argument not found on {' '.join(command)}: {arg_var}")
    cfg_editor.flatten_arg(
        *node_names, leaf_name, arg_var=arg_var, sub_args_options=sub_args_options)
    manager.save()
    return {
        "command": command,
        "flattened": arg_var,
        "sub_args_options": sub_args_options or {},
    }


def unflatten_argument(
    name: str,
    command: list[str],
    arg_var: str,
    options: list[str],
    help: dict,
    sub_args_options: Optional[dict[str, list[str]]] = None,
) -> dict:
    """Inverse of flatten_argument: re-wrap sub-args under a single object arg."""
    manager = WorkspaceManager(name)
    manager.load()
    cfg_editor, node_names, leaf_name = _load_cfg_editor_for_command(manager, command)
    cfg_editor.unflatten_arg(
        *node_names, leaf_name, arg_var=arg_var,
        options=options, help=help, sub_args_options=sub_args_options)
    manager.save()
    arg, _ = cfg_editor.find_arg_by_var(*node_names, leaf_name, arg_var=arg_var)
    return arg.to_primitive()
