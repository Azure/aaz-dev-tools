"""Workspace lifecycle + command-tree edit tools."""

from __future__ import annotations

from typing import Optional

from mcp.server.fastmcp import FastMCP


def register(mcp: FastMCP) -> None:
    @mcp.tool()
    def list_workspaces() -> list[dict]:
        """List existing workspaces in the configured workspace folder."""
        from ...services.command import workspaces
        return workspaces.list_workspaces()

    @mcp.tool()
    def create_workspace(
        name: str,
        mod_names: str,
        resource_provider: str,
        plane: str = "mgmt-plane",
        source: str = "OpenAPI",
    ) -> dict:
        """Create a new workspace. Errors if a workspace with this name
        already exists.

        - name: workspace name (becomes the folder name on disk)
        - mod_names: swagger module path under specification/, e.g.
          'consumption' or 'compute/Microsoft.Compute'
        - resource_provider: the ARM RP name, e.g. 'Microsoft.Consumption'
        - plane: 'mgmt-plane' (default) or 'data-plane'
        - source: 'OpenAPI' (default) or 'TypeSpec'
        """
        from ...services.command import workspaces
        return workspaces.create_workspace(
            name=name,
            plane=plane,
            mod_names=mod_names,
            resource_provider=resource_provider,
            source=source,
        )

    @mcp.tool()
    def load_workspace(name: str) -> dict:
        """Load an existing workspace and return its command tree.

        Returns the workspace's command tree as a dict.
        """
        from ...services.command import workspaces
        return workspaces.load_workspace(name)

    @mcp.tool()
    def add_swagger_resources(
        name: str,
        module: str,
        version: str,
        resource_paths: list[str],
    ) -> dict:
        """Add Azure REST API swagger resources to a workspace.

        The resource_paths are the raw URL templates from the swagger spec,
        e.g. '/subscriptions/{subscriptionId}/providers/Microsoft.Consumption/budgets'.
        They are normalized to resource ids automatically.

        - name: workspace name
        - module: swagger module (e.g. 'consumption')
        - version: API version (e.g. '2024-08-01')
        - resource_paths: list of swagger paths
        """
        from ...services.command import workspaces
        return workspaces.add_swagger_resources(
            name=name,
            module=module,
            version=version,
            resource_paths=resource_paths,
        )

    @mcp.tool()
    def set_node_help(
        name: str,
        node_names: list[str],
        help: Optional[dict] = None,
        stage: Optional[str] = None,
    ) -> dict:
        """Update help text and/or stage on a command-group node.

        - name: workspace name
        - node_names: path to the group, e.g. ['consumption', 'budget']
          (do NOT include the implicit 'aaz' root)
        - help: dict with 'short' and optional 'lines'; e.g.
          {'short': 'Manage consumption budgets.'}
        - stage: one of 'Stable', 'Preview', 'Experimental'
        """
        from ...services.command import workspaces
        return workspaces.set_node_help(
            name=name, node_names=node_names, help=help, stage=stage)

    @mcp.tool()
    def set_command_help(
        name: str,
        leaf_names: list[str],
        help: Optional[dict] = None,
        stage: Optional[str] = None,
    ) -> dict:
        """Update help text and/or stage on a leaf command.

        - name: workspace name
        - leaf_names: full command path, e.g. ['consumption', 'budget', 'create']
          (do NOT include the implicit 'aaz' root)
        - help: dict with 'short' and optional 'lines'
        - stage: one of 'Stable', 'Preview', 'Experimental'
        """
        from ...services.command import workspaces
        return workspaces.set_command_help(
            name=name, leaf_names=leaf_names, help=help, stage=stage)

    @mcp.tool()
    def generate_to_aaz(name: str) -> dict:
        """Export the workspace's command tree into the configured aaz repo
        (writes JSON/XML under the Commands/ tree)."""
        from ...services.command import workspaces
        return workspaces.generate_to_aaz(name)

    @mcp.tool()
    def rename_command_group(
        name: str,
        node_names: list[str],
        new_node_names: list[str],
    ) -> dict:
        """Rename a command-tree group (e.g. rename 'consumption usage-detail'
        to 'consumption usage'). Both lists exclude the implicit 'aaz' root.

        - name: workspace name
        - node_names: current group path, e.g. ['consumption', 'usage-detail']
        - new_node_names: target path, e.g. ['consumption', 'usage']
        """
        from ...services.command import workspaces
        return workspaces.rename_command_group(
            name=name, node_names=node_names, new_node_names=new_node_names)

    @mcp.tool()
    def rename_command(
        name: str,
        leaf_names: list[str],
        new_leaf_names: list[str],
    ) -> dict:
        """Rename a command-tree leaf (e.g. rename
        'consumption pricesheet default show' to 'consumption pricesheet show').
        Both lists exclude the implicit 'aaz' root.

        - name: workspace name
        - leaf_names: current command path
        - new_leaf_names: target command path
        """
        from ...services.command import workspaces
        return workspaces.rename_command(
            name=name, leaf_names=leaf_names, new_leaf_names=new_leaf_names)
