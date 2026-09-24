"""Build a small GitHub issue event payload for CI smoke tests."""

from __future__ import annotations

import argparse
import json
from pathlib import Path


def build_issue_event(
    *,
    title: str,
    body: str,
    number: int,
    repo: str,
    comments_url: str | None = None,
) -> dict:
    if comments_url is None and number:
        comments_url = f"https://api.github.com/repos/{repo}/issues/{number}/comments"

    return {
        "issue": {
            "number": number,
            "title": title,
            "body": body,
            "comments_url": comments_url,
            "labels": [{"name": "codegen:request"}],
            "pull_request": None,
        },
        "repository": {
            "full_name": repo,
        },
    }


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--title", required=True)
    parser.add_argument("--body", required=True)
    parser.add_argument("--number", type=int, default=0)
    parser.add_argument("--repo", required=True)
    parser.add_argument("--comments-url")
    parser.add_argument("--out", required=True)
    args = parser.parse_args()

    event = build_issue_event(
        title=args.title,
        body=args.body,
        number=args.number,
        repo=args.repo,
        comments_url=args.comments_url,
    )
    Path(args.out).write_text(json.dumps(event, indent=2), encoding="utf-8")


if __name__ == "__main__":
    main()
