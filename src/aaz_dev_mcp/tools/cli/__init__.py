"""CLI-domain tool registrations."""

from __future__ import annotations

from mcp.server.fastmcp import FastMCP

from . import modules as _modules


def register(mcp: FastMCP) -> None:
    _modules.register(mcp)
