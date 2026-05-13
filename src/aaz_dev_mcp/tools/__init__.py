"""FastMCP tool registrations.

Mirrors the ``services/`` layout: every domain submodule exposes a
``register(mcp)`` entry point that wires its ``@mcp.tool()`` callables.
``register_tools`` simply dispatches to each domain in turn.
"""

from __future__ import annotations

from mcp.server.fastmcp import FastMCP

from . import config as _config
from .command import register as _register_command
from .cli import register as _register_cli


def register_tools(mcp: FastMCP) -> None:
    _config.register(mcp)
    _register_command(mcp)
    _register_cli(mcp)
