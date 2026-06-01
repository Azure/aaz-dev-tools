"""Validate LLM-extracted issue requests and render preview comments."""

from __future__ import annotations

import argparse
import base64
import json
import re
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

from .spec_discovery import (
    discover_resources,
    normalize_provider,
    summarize_resources,
    validate_api_version,
)


MARKER_PREFIX = "aaz-codegen-preview:v1:"


def parse_llm_response(path: str | Path) -> dict[str, Any]:
    raw = json.loads(Path(path).read_text(encoding="utf-8"))
    content = None
    if isinstance(raw, dict):
        choices = raw.get("choices") or []
        if choices:
            content = ((choices[0].get("message") or {}).get("content"))
        content = content or raw.get("response") or raw.get("content")
    if not content:
        raise ValueError("GitHub Models response did not contain message content.")
    return _parse_json_content(content)


def build_preview(
    event: dict[str, Any],
    extracted: dict[str, Any],
    swagger_path: str | Path,
) -> tuple[dict[str, Any], str]:
    issue = event.get("issue") or {}
    issue_number = issue.get("number")
    errors: list[str] = []
    questions: list[str] = [
        str(q).strip()
        for q in (extracted.get("questions") or [])
        if str(q).strip()
    ]

    provider = normalize_provider(extracted.get("resource_provider"))
    api_version = validate_api_version(extracted.get("api_version"))
    swagger_module = _empty_to_none(extracted.get("swagger_module"))
    cli_module = _empty_to_none(extracted.get("cli_module"))
    target = _empty_to_none(extracted.get("target")) or "main"
    profile = _empty_to_none(extracted.get("profile")) or "latest"
    spec_source = _empty_to_none(extracted.get("spec_source")) or "main"

    if not provider:
        errors.append("Could not extract a resource provider.")
        questions.append("Which Azure resource provider should be generated?")
    if not api_version:
        errors.append("Could not extract a valid API version.")
        questions.append("Which API version should be generated?")
    if target not in {"main", "extension"}:
        errors.append(f"Unsupported target `{target}`. Use `main` or `extension`.")
    elif target == "extension":
        errors.append("Extension target is not supported by the v1 GitHub Actions runner.")
    if spec_source != "main":
        errors.append(
            "Only `azure-rest-api-specs` main is supported in v1. "
            f"Requested spec source: `{spec_source}`."
        )

    discovery = None
    if provider and api_version and spec_source == "main":
        discovery = discover_resources(
            swagger_path=swagger_path,
            resource_provider=provider,
            api_version=api_version,
            swagger_module=swagger_module,
        )
        errors.extend(discovery.errors)
        if not swagger_module and len(discovery.modules) == 1:
            swagger_module = discovery.modules[0]
        if not cli_module and swagger_module:
            cli_module = swagger_module

    if not swagger_module:
        errors.append("Could not infer the swagger module.")
        questions.append("Which azure-rest-api-specs module should be used?")
    if not cli_module:
        errors.append("Could not infer the Azure CLI module.")
        questions.append("Which azure-cli command module should be generated?")

    resources = discovery.resources if discovery else []
    request = {
        "resource_provider": provider,
        "api_version": api_version,
        "swagger_module": swagger_module,
        "cli_module": cli_module,
        "target": target,
        "profile": profile,
        "spec_source": spec_source,
        "confidence": extracted.get("confidence") or "low",
        "notes": extracted.get("notes"),
    }
    valid = not errors and bool(resources)
    state = {
        "schema": "aaz-codegen-preview/v1",
        "created_at": datetime.now(timezone.utc).isoformat(),
        "issue_number": issue_number,
        "valid": valid,
        "request": request,
        "resource_count": len(resources),
        "resource_hash": discovery.resource_hash if discovery else None,
        "errors": _dedupe(errors),
        "questions": _dedupe(questions),
    }
    return state, render_preview_markdown(state, resources)


def render_preview_markdown(state: dict[str, Any], resources: list[Any]) -> str:
    marker = encode_state_marker(state)
    request = state["request"]
    lines = [
        marker,
        "## AAZ Codegen Preview",
        "",
        f"Status: **{'ready' if state['valid'] else 'needs clarification'}**",
        "",
        "| Field | Value |",
        "| --- | --- |",
    ]
    for key in [
        "resource_provider",
        "api_version",
        "swagger_module",
        "cli_module",
        "target",
        "profile",
        "spec_source",
        "confidence",
    ]:
        value = request.get(key)
        lines.append(f"| `{key}` | `{value or ''}` |")

    if state["errors"]:
        lines.extend(["", "### Blocking Issues"])
        lines.extend(f"- {err}" for err in state["errors"])
    if state["questions"]:
        lines.extend(["", "### Questions"])
        lines.extend(f"- {question}" for question in state["questions"])

    lines.extend(
        [
            "",
            "### Discovered Resources",
            "",
            summarize_resources(resources),
            "",
        ]
    )
    if state["valid"]:
        lines.append("Comment `/codegen` on this issue to run codegen from this preview.")
    else:
        lines.append("Update the issue with the missing details, then re-run the preview by editing the issue or reapplying `codegen:request`.")
    return "\n".join(lines) + "\n"


def encode_state_marker(state: dict[str, Any]) -> str:
    data = json.dumps(state, sort_keys=True, separators=(",", ":")).encode("utf-8")
    return f"<!-- {MARKER_PREFIX}{base64.b64encode(data).decode('ascii')} -->"


def decode_state_from_comment(body: str) -> dict[str, Any] | None:
    pattern = re.compile(r"<!--\s*" + re.escape(MARKER_PREFIX) + r"([A-Za-z0-9+/=]+)\s*-->")
    match = pattern.search(body or "")
    if not match:
        return None
    try:
        data = base64.b64decode(match.group(1)).decode("utf-8")
        state = json.loads(data)
    except (ValueError, json.JSONDecodeError):
        return None
    if state.get("schema") != "aaz-codegen-preview/v1":
        return None
    return state


def _parse_json_content(content: str) -> dict[str, Any]:
    content = content.strip()
    if content.startswith("```"):
        content = re.sub(r"^```(?:json)?\s*", "", content)
        content = re.sub(r"\s*```$", "", content)
    try:
        result = json.loads(content)
    except json.JSONDecodeError:
        match = re.search(r"\{.*\}", content, flags=re.DOTALL)
        if not match:
            raise
        result = json.loads(match.group(0))
    if not isinstance(result, dict):
        raise ValueError("LLM extraction response must be a JSON object.")
    return result


def _empty_to_none(value: Any) -> str | None:
    if value is None:
        return None
    value = str(value).strip()
    if not value or value.upper() == "N/A" or value.lower() == "null":
        return None
    return value


def _dedupe(values: list[str]) -> list[str]:
    seen = set()
    result = []
    for value in values:
        if value not in seen:
            result.append(value)
            seen.add(value)
    return result


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--event", required=True)
    parser.add_argument("--llm-response", required=True)
    parser.add_argument("--swagger-path", required=True)
    parser.add_argument("--out", required=True)
    parser.add_argument("--state", required=True)
    args = parser.parse_args()

    event = json.loads(Path(args.event).read_text(encoding="utf-8"))
    extracted = parse_llm_response(args.llm_response)
    state, markdown = build_preview(event, extracted, args.swagger_path)
    Path(args.out).write_text(markdown, encoding="utf-8")
    Path(args.state).write_text(json.dumps(state, indent=2), encoding="utf-8")


if __name__ == "__main__":
    main()
