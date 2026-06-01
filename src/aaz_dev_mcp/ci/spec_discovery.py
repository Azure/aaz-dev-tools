"""Lightweight OpenAPI resource discovery for issue-driven codegen."""

from __future__ import annotations

import hashlib
import json
import re
from dataclasses import dataclass
from pathlib import Path
from typing import Iterable


PROVIDER_RE = re.compile(
    r"Microsoft\.[A-Za-z0-9]+(?:[A-Za-z0-9_.-]*[A-Za-z0-9])?",
    re.IGNORECASE,
)
API_VERSION_RE = re.compile(r"^\d{4}-\d{2}-\d{2}(?:-[A-Za-z0-9-]+)?$")


@dataclass(frozen=True)
class DiscoveredResource:
    module: str
    provider: str
    api_version: str
    file_path: str
    path: str


@dataclass(frozen=True)
class DiscoveryResult:
    resources: list[DiscoveredResource]
    modules: list[str]
    errors: list[str]

    @property
    def resource_paths(self) -> list[str]:
        return sorted({r.path for r in self.resources})

    @property
    def resource_hash(self) -> str:
        joined = "\n".join(self.resource_paths)
        return hashlib.sha256(joined.encode("utf-8")).hexdigest()


def normalize_provider(value: str | None) -> str | None:
    if not value:
        return None
    value = value.strip().strip("`")
    match = PROVIDER_RE.search(value)
    if not match:
        return value or None
    provider = match.group(0)
    if provider.lower().startswith("microsoft."):
        provider = "Microsoft." + provider.split(".", 1)[1]
    return provider


def validate_api_version(value: str | None) -> str | None:
    if not value:
        return None
    value = value.strip().strip("`")
    return value if API_VERSION_RE.match(value) else None


def discover_resources(
    swagger_path: str | Path,
    resource_provider: str,
    api_version: str,
    swagger_module: str | None = None,
) -> DiscoveryResult:
    """Find swagger paths for a provider and API version.

    This intentionally avoids importing the full aaz-dev swagger model layer so
    the preview workflow can cheaply validate issue text before codegen.
    """
    swagger_root = Path(swagger_path)
    spec_root = swagger_root / "specification"
    errors: list[str] = []
    if not spec_root.is_dir():
        return DiscoveryResult(
            resources=[],
            modules=[],
            errors=[f"Swagger specification folder not found: {spec_root}"],
        )

    provider = normalize_provider(resource_provider)
    version = validate_api_version(api_version)
    if not provider:
        errors.append("Missing or invalid resource provider.")
    if not version:
        errors.append(f"Invalid API version: {api_version!r}")
    if errors:
        return DiscoveryResult(resources=[], modules=[], errors=errors)

    provider_dirs = _find_provider_dirs(spec_root, provider, swagger_module)
    if not provider_dirs:
        module_text = f" in module `{swagger_module}`" if swagger_module else ""
        return DiscoveryResult(
            resources=[],
            modules=[],
            errors=[f"Resource provider `{provider}` not found{module_text}."],
        )

    resources: list[DiscoveredResource] = []
    for provider_dir in provider_dirs:
        module = provider_dir.relative_to(spec_root).parts[0]
        for json_file in provider_dir.rglob("*.json"):
            resources.extend(
                _read_swagger_resources(
                    json_file=json_file,
                    spec_root=spec_root,
                    module=module,
                    provider=provider,
                    api_version=version,
                )
            )

    modules = sorted({r.module for r in resources})
    if swagger_module and modules and modules != [swagger_module]:
        errors.append(
            "Discovered resources outside requested module "
            f"`{swagger_module}`: {', '.join(modules)}"
        )
    if not resources:
        errors.append(
            f"No OpenAPI resources found for `{provider}` at `{version}`."
        )
    elif not swagger_module and len(modules) > 1:
        errors.append(
            "Provider/version matched multiple swagger modules: "
            + ", ".join(f"`{m}`" for m in modules)
        )

    return DiscoveryResult(
        resources=sorted(
            resources,
            key=lambda r: (r.module, r.file_path, r.path),
        ),
        modules=modules,
        errors=errors,
    )


def summarize_resources(resources: Iterable[DiscoveredResource], limit: int = 80) -> str:
    rows = []
    for idx, resource in enumerate(resources):
        if idx >= limit:
            rows.append(f"- ... truncated after {limit} resources")
            break
        rows.append(f"- `{resource.path}`")
    return "\n".join(rows) if rows else "_No resources discovered._"


def _find_provider_dirs(
    spec_root: Path,
    resource_provider: str,
    swagger_module: str | None,
) -> list[Path]:
    roots = [spec_root / swagger_module] if swagger_module else spec_root.iterdir()
    provider_lower = resource_provider.lower()
    matches: list[Path] = []
    for root in roots:
        if not root.is_dir():
            continue
        resource_manager = root / "resource-manager"
        if not resource_manager.is_dir():
            continue
        for path in resource_manager.rglob("*"):
            if path.is_dir() and path.name.lower() == provider_lower:
                matches.append(path)
    return sorted(set(matches))


def _read_swagger_resources(
    json_file: Path,
    spec_root: Path,
    module: str,
    provider: str,
    api_version: str,
) -> list[DiscoveredResource]:
    try:
        body = json.loads(json_file.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError):
        return []

    if body.get("swagger") != "2.0":
        return []
    if body.get("info", {}).get("version") != api_version:
        return []

    paths = set()
    paths.update((body.get("paths") or {}).keys())
    paths.update((body.get("x-ms-paths") or {}).keys())
    provider_lower = provider.lower()
    resources = []
    for path in sorted(paths):
        if provider_lower not in path.lower():
            continue
        resources.append(
            DiscoveredResource(
                module=module,
                provider=provider,
                api_version=api_version,
                file_path=str(json_file.relative_to(spec_root)),
                path=path,
            )
        )
    return resources
