"""Workspace lifecycle operations: thin wrappers around WorkspaceManager.

Mirrors the backend ``command/controller/workspace_manager.py`` surface that
deals with the workspace itself (create/load/list/save) and its command tree
(rename nodes/leaves, set help, add swagger resources, generate to aaz).
"""

from __future__ import annotations

import os
from typing import Iterable, Optional

import aaz_dev  # noqa: F401  (injects src/aaz_dev onto sys.path)
from command.controller.workspace_manager import WorkspaceManager
from swagger.utils.tools import swagger_resource_path_to_resource_id
from utils import exceptions


def list_workspaces() -> list[dict]:
    return WorkspaceManager.list_workspaces()


def create_workspace(
    name: str,
    plane: str,
    mod_names: str,
    resource_provider: str,
    source: str,
) -> dict:
    """Create a new workspace. Raises ResourceConflict if it already exists.

    WorkspaceManager.new already enforces "fails if exists" via a
    ResourceConflict check on the ws.json path (workspace_manager.py:52-54).
    """
    manager = WorkspaceManager.new(
        name=name,
        plane=plane,
        mod_names=mod_names,
        resource_provider=resource_provider,
        source=source,
    )
    manager.save()
    return _ws_summary(manager)


def load_workspace(name: str) -> dict:
    manager = WorkspaceManager(name)
    manager.load()
    return _ws_summary(manager)


def add_swagger_resources(
    name: str,
    module: str,
    version: str,
    resource_paths: Iterable[str],
) -> dict:
    """Add resources to a workspace's command tree by swagger path.

    ``resource_paths`` are raw swagger paths (e.g.
    ``/subscriptions/{subscriptionId}/providers/Microsoft.Consumption/budgets``);
    they are normalized to resource ids using the same helper the Flask layer
    uses.
    """
    manager = WorkspaceManager(name)
    manager.load()
    resources = [
        {"id": swagger_resource_path_to_resource_id(p)}
        for p in resource_paths
    ]
    if not resources:
        raise exceptions.InvalidAPIUsage("resource_paths must not be empty")
    manager.add_new_resources_by_swagger(
        mod_names=module,
        version=version,
        resources=resources,
    )
    manager.save()
    return {"added": [r["id"] for r in resources]}


def set_node_help(
    name: str,
    node_names: list[str],
    help: Optional[dict] = None,
    stage: Optional[str] = None,
) -> dict:
    """Update help and/or stage on a command-tree node (group).

    ``node_names`` should NOT include the root "aaz" prefix; pass the
    user-visible names, e.g. ``["consumption", "budget"]``.
    """
    manager = WorkspaceManager(name)
    manager.load()
    node = None
    if help is not None:
        node = manager.update_command_tree_node_help(*node_names, help=help)
    if stage is not None:
        node = manager.update_command_tree_node_stage(*node_names, stage=stage)
    if node is None:
        raise exceptions.InvalidAPIUsage(
            "set_node_help requires at least one of 'help' or 'stage'")
    manager.save()
    return node.to_primitive()


def set_command_help(
    name: str,
    leaf_names: list[str],
    help: Optional[dict] = None,
    stage: Optional[str] = None,
) -> dict:
    """Update help and/or stage on a command-tree leaf (command).

    ``leaf_names`` excludes the implicit 'aaz' root, e.g.
    ``["consumption", "budget", "create"]``.
    """
    manager = WorkspaceManager(name)
    manager.load()
    leaf = None
    if help is not None:
        leaf = manager.update_command_tree_leaf_help(*leaf_names, help=help)
    if stage is not None:
        leaf = manager.update_command_tree_leaf_stage(*leaf_names, stage=stage)
    if leaf is None:
        raise exceptions.InvalidAPIUsage(
            "set_command_help requires at least one of 'help' or 'stage'")
    manager.save()
    return leaf.to_primitive()


def generate_to_aaz(name: str) -> dict:
    """Export the workspace's command tree into the aaz repo."""
    manager = WorkspaceManager(name)
    manager.load()
    manager.generate_to_aaz()
    return {"workspace": name, "status": "generated"}


def rename_command_group(
    name: str,
    node_names: list[str],
    new_node_names: list[str],
) -> dict:
    """Rename a command-tree group (node).

    ``node_names`` and ``new_node_names`` exclude the implicit 'aaz' root.
    Example: rename ``['consumption', 'usage-detail']`` to
    ``['consumption', 'usage']``.
    """
    manager = WorkspaceManager(name)
    manager.load()
    if not node_names or not new_node_names:
        raise exceptions.InvalidAPIUsage(
            "node_names and new_node_names must be non-empty")
    node = manager.rename_command_tree_node(
        *node_names, new_node_names=new_node_names)
    manager.save()
    return node.to_primitive() if node is not None else {
        "from": node_names, "to": new_node_names, "noop": True}


def rename_command(
    name: str,
    leaf_names: list[str],
    new_leaf_names: list[str],
) -> dict:
    """Rename a command-tree leaf (command).

    ``leaf_names`` and ``new_leaf_names`` exclude the implicit 'aaz' root.
    Example: rename ``['consumption', 'pricesheet', 'default', 'show']`` to
    ``['consumption', 'pricesheet', 'show']``.
    """
    manager = WorkspaceManager(name)
    manager.load()
    if not leaf_names or not new_leaf_names:
        raise exceptions.InvalidAPIUsage(
            "leaf_names and new_leaf_names must be non-empty")
    leaf = manager.rename_command_tree_leaf(
        *leaf_names, new_leaf_names=new_leaf_names)
    manager.save()
    return leaf.to_primitive() if leaf is not None else {
        "from": leaf_names, "to": new_leaf_names, "noop": True}


def _ws_summary(manager: WorkspaceManager) -> dict:
    result = manager.ws.to_primitive()
    result["folder"] = manager.folder
    if os.path.exists(manager.path):
        result["updated"] = os.path.getmtime(manager.path)
    return result
