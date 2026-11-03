"""Find the latest valid AAZ codegen preview comment for an issue."""

from __future__ import annotations

import argparse
import json
import os
import sys
import urllib.request
from pathlib import Path
from typing import Any

from .preview_issue_codegen import decode_state_from_comment


def find_latest_preview(event: dict[str, Any], token: str) -> dict[str, Any]:
    issue = event.get("issue") or {}
    comments_url = issue.get("comments_url")
    if not comments_url:
        raise RuntimeError("Issue event did not contain comments_url.")

    comments = _github_get_json(comments_url, token)
    previews = []
    for comment in comments:
        state = decode_state_from_comment(comment.get("body") or "")
        if not state:
            continue
        state["_comment_id"] = comment.get("id")
        state["_comment_url"] = comment.get("html_url")
        state["_comment_created_at"] = comment.get("created_at")
        previews.append(state)

    if not previews:
        raise RuntimeError("No AAZ codegen preview comment was found.")
    previews.sort(key=lambda item: item.get("_comment_created_at") or "")
    latest = previews[-1]
    if not latest.get("valid"):
        raise RuntimeError("Latest AAZ codegen preview is not valid.")
    return latest


def _github_get_json(url: str, token: str) -> Any:
    request = urllib.request.Request(
        url,
        headers={
            "Accept": "application/vnd.github+json",
            "Authorization": f"Bearer {token}",
            "X-GitHub-Api-Version": "2022-11-28",
        },
    )
    with urllib.request.urlopen(request, timeout=30) as response:
        return json.loads(response.read().decode("utf-8"))


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--event", required=True)
    parser.add_argument("--out", required=True)
    args = parser.parse_args()

    token = os.environ.get("GH_TOKEN") or os.environ.get("GITHUB_TOKEN")
    if not token:
        print("GH_TOKEN or GITHUB_TOKEN is required.", file=sys.stderr)
        raise SystemExit(2)

    event = json.loads(Path(args.event).read_text(encoding="utf-8"))
    preview = find_latest_preview(event, token)
    Path(args.out).write_text(json.dumps(preview, indent=2), encoding="utf-8")


if __name__ == "__main__":
    main()

