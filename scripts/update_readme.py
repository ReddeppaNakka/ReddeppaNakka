#!/usr/bin/env python3
"""Refresh the auto-generated blocks in README.md.

Rewrites the content between the RECENT_ACTIVITY and LAST_UPDATED marker pairs
using the public GitHub events API. Runs from .github/workflows/update-readme.yml.

Only the text between markers is touched; the rest of the README is never parsed.

Two behaviours worth knowing about:

  * The timestamp is only refreshed when the activity list itself changed. If it
    updated on every run the workflow would push a commit twice a day forever,
    manufacturing contribution squares for work nobody did.

  * The public events API omits `payload.size` on PushEvent for unauthenticated
    callers, so commit counts are rendered only when the API actually supplies
    them. A missing count prints nothing rather than a misleading "0 commits".
"""

from __future__ import annotations

import json
import os
import re
import sys
import urllib.error
import urllib.request
from datetime import datetime, timezone
from pathlib import Path

USER = os.environ.get("GH_USERNAME", "ReddeppaNakka")
TOKEN = os.environ.get("GITHUB_TOKEN")
README = Path(__file__).resolve().parent.parent / "README.md"
MAX_ROWS = 5

VERB = {
    "PushEvent": "Pushed to",
    "CreateEvent": "Created",
    "IssuesEvent": "Opened an issue in",
    "WatchEvent": "Starred",
    "ForkEvent": "Forked",
    "ReleaseEvent": "Released",
    "PublicEvent": "Open-sourced",
}


def fetch_events() -> list[dict]:
    req = urllib.request.Request(
        f"https://api.github.com/users/{USER}/events/public?per_page=100",
        headers={
            "Accept": "application/vnd.github+json",
            "User-Agent": f"{USER}-profile-readme",
            **({"Authorization": f"Bearer {TOKEN}"} if TOKEN else {}),
        },
    )
    try:
        with urllib.request.urlopen(req, timeout=20) as resp:
            return json.load(resp)
    except (urllib.error.URLError, urllib.error.HTTPError, TimeoutError, json.JSONDecodeError) as exc:
        print(f"::warning::Could not reach the GitHub events API: {exc}", file=sys.stderr)
        return []


def describe(event: dict) -> tuple[str, str] | None:
    """Return (repo, sentence) for an event we know how to render, else None."""
    kind = event.get("type", "")
    repo = event.get("repo", {}).get("name", "")
    payload = event.get("payload", {})
    if not repo:
        return None

    if kind == "PullRequestEvent":
        action = payload.get("action", "")
        merged = payload.get("pull_request", {}).get("merged")
        if action == "merged" or merged:
            verb = "Merged a pull request in"
        elif action == "opened":
            verb = "Opened a pull request in"
        elif action == "closed":
            verb = "Closed a pull request in"
        else:
            return None
        return repo, verb

    if kind == "PushEvent":
        # `size` is absent for unauthenticated callers; only render a real number.
        n = payload.get("size")
        if n is None:
            n = payload.get("distinct_size")
        if n is None and isinstance(payload.get("commits"), list):
            n = len(payload["commits"])
        suffix = f" · {n} commit{'s' if n != 1 else ''}" if isinstance(n, int) and n > 0 else ""
        return repo, f"Pushed to{suffix}\x00"  # \x00 marks "suffix already inside verb"

    verb = VERB.get(kind)
    return (repo, verb) if verb else None


def render(events: list[dict]) -> str:
    """One row per repository, newest first. Repeated events on the same repo collapse."""
    rows: list[str] = []
    seen: set[str] = set()

    for event in events:
        described = describe(event)
        if not described:
            continue
        repo, verb = described
        if repo in seen:
            continue
        seen.add(repo)

        # Reattach a push suffix that was carried through the sentinel.
        verb, _, _ = verb.partition("\x00")
        when = datetime.strptime(event["created_at"], "%Y-%m-%dT%H:%M:%SZ")
        owned = repo.lower().startswith(f"{USER.lower()}/")
        tag = "" if owned else " <sub>`collaboration`</sub>"

        rows.append(
            f"- **{verb}** [`{repo}`](https://github.com/{repo})"
            f"{tag} <sub>{when:%d %b %Y}</sub>"
        )
        if len(rows) == MAX_ROWS:
            break

    return "\n".join(rows) if rows else "_No public activity in the last 90 days._"


def read_block(text: str, marker: str) -> str:
    match = re.search(
        rf"<!--\s*{marker}:start\s*-->(.*?)<!--\s*{marker}:end\s*-->", text, re.DOTALL
    )
    return match.group(1).strip() if match else ""


def splice(text: str, marker: str, body: str, pad: bool = True) -> str:
    pattern = re.compile(
        rf"(<!--\s*{marker}:start\s*-->)(.*?)(<!--\s*{marker}:end\s*-->)", re.DOTALL
    )
    if not pattern.search(text):
        sys.exit(f"Marker pair '{marker}' not found in README.md — aborting rather than guessing.")
    joiner = "\n" if pad else ""
    return pattern.sub(lambda m: f"{m.group(1)}{joiner}{body}{joiner}{m.group(3)}", text)


def main() -> None:
    original = README.read_text(encoding="utf-8")

    events = fetch_events()
    if not events:
        print("No events returned; leaving the README untouched.")
        return

    activity = render(events)

    if activity == read_block(original, "RECENT_ACTIVITY"):
        print("Activity is unchanged; not touching the timestamp or committing.")
        return

    stamp = datetime.now(timezone.utc).strftime("%d %b %Y, %H:%M UTC")
    updated = splice(original, "RECENT_ACTIVITY", activity)
    updated = splice(updated, "LAST_UPDATED", stamp, pad=False)

    README.write_text(updated, encoding="utf-8")
    print(f"README updated at {stamp}.")


if __name__ == "__main__":
    main()
