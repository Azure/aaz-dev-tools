"""FastMCP server entrypoint for aaz-dev-mcp.

Run via the ``aaz-dev-mcp`` console script (installed by pyproject) or with
``python -m aaz_dev_mcp.server``.

The server speaks the Model Context Protocol over stdio. All log output goes
to stderr so it doesn't corrupt the JSON-RPC stream on stdout.
"""

from __future__ import annotations

import logging
import sys


def _configure_logging() -> None:
    logging.basicConfig(
        level=logging.INFO,
        stream=sys.stderr,
        format="%(asctime)s %(levelname)s %(name)s: %(message)s",
    )


def main() -> None:
    _configure_logging()

    # Import lazily so logging is set up before any aaz-dev module logs.
    from mcp.server.fastmcp import FastMCP
    from .tools import register_tools

    mcp = FastMCP("aaz-dev")
    register_tools(mcp)
    # FastMCP.run() defaults to stdio transport.
    mcp.run()


if __name__ == "__main__":
    main()
