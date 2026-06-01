"""Build GitHub Models prompts from GitHub issue events."""

from __future__ import annotations

import argparse
import json
from pathlib import Path


DEFAULT_MODEL = "openai/gpt-4o-mini"


def build_prompt(event: dict) -> str:
    issue = event.get("issue") or {}
    title = issue.get("title") or ""
    body = issue.get("body") or ""

    return f"""Extract an AAZ Azure CLI code generation request from this GitHub issue.

Return JSON only. Do not wrap it in Markdown.

Schema:
{{
  "resource_provider": string | null,
  "api_version": string | null,
  "swagger_module": string | null,
  "cli_module": string | null,
  "target": "main" | "extension" | null,
  "profile": string | null,
  "spec_source": "main" | string | null,
  "confidence": "high" | "medium" | "low",
  "questions": string[],
  "notes": string | null
}}

Rules:
- resource_provider should be only the provider namespace, for example "Microsoft.Consumption".
- If the issue says "Microsoft.Compute/disks", set resource_provider to "Microsoft.Compute".
- api_version must look like "2024-08-01" or "2024-08-01-preview".
- swagger_module is the azure-rest-api-specs top-level module, for example "consumption".
- cli_module is the azure-cli command module, often the same as swagger_module.
- target defaults to "main" unless the issue clearly asks for an extension.
- profile defaults to "latest".
- spec_source defaults to "main" unless a branch or PR is explicitly requested.
- If required fields are missing, set them to null and add concise questions.
- Never invent a resource provider or API version.

Issue title:
{title}

Issue body:
{body}
"""


def build_payload(event: dict, model: str) -> dict:
    return {
        "model": model,
        "messages": [
            {
                "role": "system",
                "content": (
                    "You are a strict information extraction tool for Azure "
                    "CLI AAZ code generation requests. Output valid JSON only."
                ),
            },
            {"role": "user", "content": build_prompt(event)},
        ],
        "temperature": 0,
        "max_tokens": 1200,
    }


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--event", required=True)
    parser.add_argument("--out", required=True)
    parser.add_argument("--payload", action="store_true")
    parser.add_argument("--model", default=DEFAULT_MODEL)
    args = parser.parse_args()

    event = json.loads(Path(args.event).read_text(encoding="utf-8"))
    if args.payload:
        data = build_payload(event, args.model)
        Path(args.out).write_text(json.dumps(data, indent=2), encoding="utf-8")
    else:
        Path(args.out).write_text(build_prompt(event), encoding="utf-8")


if __name__ == "__main__":
    main()

