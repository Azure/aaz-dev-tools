"""Path configuration helpers.

The aaz-dev-tools backend reads paths from a global :class:`utils.config.Config`
class. This module exposes a single :func:`apply_config` that mutates those
class attributes, surfacing the validating setters' ``ValueError`` to the
caller (the MCP ``configure`` tool).

Environment variables already honored by the upstream Config at import time:
    AAZ_PATH                  -> aaz repo checkout
    AAZ_SWAGGER_PATH          -> azure-rest-api-specs checkout
    AAZ_CLI_PATH              -> azure-cli checkout
    AAZ_CLI_EXTENSION_PATH    -> azure-cli-extensions checkout
    AAZ_DEV_WORKSPACE_FOLDER  -> where ws.json files live (default ~/.aaz/workspaces)
"""

from __future__ import annotations

from typing import Optional

# Importing ``aaz_dev`` first injects ``src/aaz_dev`` onto sys.path (see its
# __init__.py), which makes the bare-namespace ``utils``/``command``/``cli``/
# ``swagger`` imports used throughout the backend resolvable.
import aaz_dev  # noqa: F401
from utils.config import Config


def apply_config(
    aaz_path: Optional[str] = None,
    swagger_path: Optional[str] = None,
    cli_path: Optional[str] = None,
    cli_extension_path: Optional[str] = None,
    workspace_folder: Optional[str] = None,
) -> dict:
    """Update Config in place. Returns the resulting paths.

    Each setter validates that the path exists and raises ``ValueError``
    otherwise; the caller (MCP tool) should turn that into a tool error.
    """
    # The setters use Click's callback signature (cls, ctx, param, value).
    # We pass None for ctx/param since we're not in a Click context.
    if aaz_path is not None:
        Config.validate_and_setup_aaz_path(None, None, aaz_path)
    if swagger_path is not None:
        Config.validate_and_setup_swagger_path(None, None, swagger_path)
    if cli_path is not None:
        Config.validate_and_setup_cli_path(None, None, cli_path)
    if cli_extension_path is not None:
        Config.validate_and_setup_cli_extension_path(None, None, cli_extension_path)
    if workspace_folder is not None:
        Config.validate_and_setup_aaz_dev_workspace_folder(None, None, workspace_folder)
    return current_config()


def current_config() -> dict:
    return {
        "aaz_path": Config.AAZ_PATH,
        "swagger_path": Config.SWAGGER_PATH,
        "cli_path": Config.CLI_PATH,
        "cli_extension_path": Config.CLI_EXTENSION_PATH,
        "workspace_folder": Config.AAZ_DEV_WORKSPACE_FOLDER,
    }
