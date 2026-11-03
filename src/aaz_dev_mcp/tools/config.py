"""``configure`` tool — wires repo paths used by aaz-dev-tools."""

from __future__ import annotations

from typing import Optional

from mcp.server.fastmcp import FastMCP


def register(mcp: FastMCP) -> None:
    @mcp.tool()
    def configure(
        aaz_path: Optional[str] = None,
        swagger_path: Optional[str] = None,
        cli_path: Optional[str] = None,
        cli_extension_path: Optional[str] = None,
        workspace_folder: Optional[str] = None,
    ) -> dict:
        """Configure repository paths used by aaz-dev-tools.

        All arguments are optional; only the ones provided are updated. Pass
        no arguments to inspect the current values. Paths are validated for
        existence; invalid paths raise an error.

        - aaz_path: clone of github.com/Azure/aaz
        - swagger_path: clone of github.com/Azure/azure-rest-api-specs
        - cli_path: clone of github.com/Azure/azure-cli
        - cli_extension_path: clone of github.com/Azure/azure-cli-extensions
        - workspace_folder: where ws.json files are stored
          (default ~/.aaz/workspaces)
        """
        from ..config import apply_config
        try:
            return apply_config(
                aaz_path=aaz_path,
                swagger_path=swagger_path,
                cli_path=cli_path,
                cli_extension_path=cli_extension_path,
                workspace_folder=workspace_folder,
            )
        except ValueError as e:
            return {"error": str(e)}
