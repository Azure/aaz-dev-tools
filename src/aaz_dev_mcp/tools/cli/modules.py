"""CLI module tools (get/update/select)."""

from __future__ import annotations

from mcp.server.fastmcp import FastMCP


def register(mcp: FastMCP) -> None:
    @mcp.tool()
    def get_main_module(module_name: str) -> dict:
        """Load the current azure-cli main module's command profile."""
        from ...services.cli import modules
        return modules.get_module("main", module_name)

    @mcp.tool()
    def get_extension_module(module_name: str) -> dict:
        """Load the current azure-cli-extensions module's command profile."""
        from ...services.cli import modules
        return modules.get_module("extension", module_name)

    @mcp.tool()
    def update_main_module(
        module_name: str,
        profiles: dict,
        by_patch: bool = True,
    ) -> dict:
        """Generate CLI code for an azure-cli main module from a profiles dict.

        See the `select_command_versions` tool for a higher-level helper that
        builds `profiles` from a flat command -> version map.
        """
        from ...services.cli import modules
        return modules.update_module(
            "main", module_name, profiles, by_patch=by_patch)

    @mcp.tool()
    def update_extension_module(
        module_name: str,
        profiles: dict,
        by_patch: bool = True,
    ) -> dict:
        """Generate CLI code for an azure-cli-extensions module from a
        profiles dict."""
        from ...services.cli import modules
        return modules.update_module(
            "extension", module_name, profiles, by_patch=by_patch)

    @mcp.tool()
    def select_command_versions(
        target: str,
        module_name: str,
        command_versions: dict,
        profile: str = "latest",
        by_patch: bool = True,
    ) -> dict:
        """Pick specific versions for specific commands and generate CLI code.

        - target: 'main' (azure-cli) or 'extension' (azure-cli-extensions)
        - module_name: CLI module name, e.g. 'consumption'
        - command_versions: map of full command path -> API version. Example::

              {
                "consumption budget create": "2024-08-01",
                "consumption budget delete": "2024-08-01"
              }

        - profile: CLI profile name, default 'latest'
        - by_patch: True (default) merges with existing commands; False
          overwrites the whole profile.

        All commands are marked registered=True.
        """
        from ...services.cli import modules
        return modules.select_command_versions(
            target=target,
            module_name=module_name,
            profile=profile,
            command_versions=command_versions,
            by_patch=by_patch,
        )
