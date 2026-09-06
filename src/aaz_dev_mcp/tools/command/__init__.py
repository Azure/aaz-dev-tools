"""Command-domain tool registrations."""

from __future__ import annotations

from mcp.server.fastmcp import FastMCP

from . import workspaces as _workspaces
from . import arguments as _arguments
from . import examples as _examples


def register(mcp: FastMCP) -> None:
    _workspaces.register(mcp)
    _arguments.register(mcp)
    _examples.register(mcp)
