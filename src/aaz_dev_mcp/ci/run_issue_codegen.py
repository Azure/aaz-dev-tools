"""Run deterministic AAZ codegen from a validated issue preview."""

from __future__ import annotations

import argparse
import json
import re
from pathlib import Path
from typing import Any

from .spec_discovery import discover_resources


def run_codegen_from_preview(
    preview: dict[str, Any],
    swagger_path: str,
    aaz_path: str,
    cli_path: str | None,
    cli_extension_path: str | None,
    workspace_folder: str,
    by_patch: bool,
    skip_cli: bool = False,
) -> dict[str, Any]:
    request = preview["request"]
    discovery = discover_resources(
        swagger_path=swagger_path,
        resource_provider=request["resource_provider"],
        api_version=request["api_version"],
        swagger_module=request["swagger_module"],
        resource_paths=request.get("resource_paths"),
    )
    if discovery.errors:
        raise RuntimeError("; ".join(discovery.errors))
    if preview.get("resource_hash") and discovery.resource_hash != preview["resource_hash"]:
        raise RuntimeError(
            "Discovered resources changed since preview. Re-run codegen preview first."
        )

    from aaz_dev_mcp.config import apply_config
    from aaz_dev_mcp.services.cli import modules
    from aaz_dev_mcp.services.command import workspaces

    apply_config(
        aaz_path=aaz_path,
        swagger_path=swagger_path,
        cli_path=cli_path,
        cli_extension_path=cli_extension_path,
        workspace_folder=workspace_folder,
    )

    workspace_name = _workspace_name(
        issue_number=preview.get("issue_number"),
        provider=request["resource_provider"],
        api_version=request["api_version"],
    )
    workspaces.create_workspace(
        name=workspace_name,
        plane="mgmt-plane",
        mod_names=request["swagger_module"],
        resource_provider=request["resource_provider"],
        source="OpenAPI",
    )
    workspaces.add_swagger_resources(
        name=workspace_name,
        module=request["swagger_module"],
        version=request["api_version"],
        resource_paths=discovery.resource_paths,
    )
    command_versions = _workspace_command_versions(
        workspace_name=workspace_name,
        api_version=request["api_version"],
    )
    workspaces.generate_to_aaz(workspace_name)
    if not skip_cli:
        modules.select_command_versions(
            target=request.get("target") or "main",
            module_name=request["cli_module"],
            profile=request.get("profile") or "latest",
            command_versions=command_versions,
            by_patch=by_patch,
        )
    return {
        "workspace": workspace_name,
        "request": request,
        "resource_count": len(discovery.resources),
        "command_count": len(command_versions),
        "commands": sorted(command_versions.keys()),
        "by_patch": by_patch,
        "cli_generated": not skip_cli,
    }


def render_summary(result: dict[str, Any]) -> str:
    request = result["request"]
    lines = [
        "## AAZ Codegen Run",
        "",
        f"- Workspace: `{result['workspace']}`",
        f"- Resource provider: `{request['resource_provider']}`",
        f"- API version: `{request['api_version']}`",
        f"- Swagger module: `{request['swagger_module']}`",
        f"- CLI module: `{request['cli_module']}`",
        f"- Target: `{request.get('target') or 'main'}`",
        f"- Profile: `{request.get('profile') or 'latest'}`",
        f"- Resources: `{result['resource_count']}`",
        f"- Commands: `{result['command_count']}`",
        f"- by_patch: `{result['by_patch']}`",
        f"- Azure CLI generated: `{result['cli_generated']}`",
        "",
        "### Commands",
    ]
    lines.extend(f"- `{command}`" for command in result["commands"])
    return "\n".join(lines) + "\n"


def _workspace_command_versions(workspace_name: str, api_version: str) -> dict[str, str]:
    import aaz_dev  # noqa: F401
    from command.controller.workspace_manager import WorkspaceManager

    manager = WorkspaceManager(workspace_name)
    manager.load()
    command_versions = {}
    for leaf in manager.iter_command_tree_leaves():
        command_versions[" ".join(leaf.names)] = api_version
    if not command_versions:
        raise RuntimeError("Workspace did not produce any command leaves.")
    return command_versions


def _workspace_name(issue_number: int | None, provider: str, api_version: str) -> str:
    prefix = f"issue-{issue_number}-" if issue_number else ""
    text = f"{prefix}{provider}-{api_version}".lower()
    text = re.sub(r"[^a-z0-9._-]+", "-", text)
    return text.strip("-")[:80]


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--preview", required=True)
    parser.add_argument("--swagger-path", required=True)
    parser.add_argument("--aaz-path", required=True)
    parser.add_argument("--cli-path")
    parser.add_argument("--cli-extension-path")
    parser.add_argument("--workspace-folder", required=True)
    parser.add_argument("--summary", required=True)
    parser.add_argument("--json-out", required=True)
    parser.add_argument("--by-patch", choices=["true", "false"], default="true")
    parser.add_argument("--skip-cli", choices=["true", "false"], default="false")
    args = parser.parse_args()

    preview = json.loads(Path(args.preview).read_text(encoding="utf-8"))
    result = run_codegen_from_preview(
        preview=preview,
        swagger_path=args.swagger_path,
        aaz_path=args.aaz_path,
        cli_path=args.cli_path,
        cli_extension_path=args.cli_extension_path,
        workspace_folder=args.workspace_folder,
        by_patch=args.by_patch == "true",
        skip_cli=args.skip_cli == "true",
    )
    Path(args.summary).write_text(render_summary(result), encoding="utf-8")
    Path(args.json_out).write_text(json.dumps(result, indent=2), encoding="utf-8")


if __name__ == "__main__":
    main()
