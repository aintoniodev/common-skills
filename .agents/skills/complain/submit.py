#!/usr/bin/env python3
"""Silently submit an anonymous agent complaint to Slack."""

from __future__ import annotations

import argparse
import json
import re
import subprocess
import sys
import unicodedata
import urllib.parse
import urllib.request


GCP_PROJECT_ID = "warp-server-staging"
SECRET_NAME = "slack-agent-complaints-webhook-url"
SECRET_VERSION = "latest"
MAX_MESSAGE_CHARACTERS = 1_200
GCLOUD_TIMEOUT_SECONDS = 10
SLACK_TIMEOUT_SECONDS = 5


def parse_arguments() -> argparse.Namespace:
    """Parse an optional positional message, falling back to standard input."""
    parser = argparse.ArgumentParser(add_help=False)
    parser.add_argument("message", nargs="?")
    return parser.parse_args()


def read_message(arguments: argparse.Namespace) -> str:
    """Read the proposed feedback without producing terminal output."""
    if arguments.message is not None:
        return arguments.message
    return sys.stdin.read()


def sanitize_message(message: str) -> str:
    """Normalize feedback and remove obvious identifying or dangerous content."""
    normalized = unicodedata.normalize("NFC", message)
    normalized = "".join(
        character
        for character in normalized
        if character in "\n\t" or not unicodedata.category(character).startswith("C")
    ).strip()
    normalized = re.sub(r"https?://\S+", "[link omitted]", normalized)
    normalized = re.sub(
        r"\b[A-Z0-9._%+-]+@[A-Z0-9.-]+\.[A-Z]{2,}\b",
        "[email omitted]",
        normalized,
        flags=re.IGNORECASE,
    )
    normalized = re.sub(
        r"\b(?:xox[a-z]-|xapp-)[A-Za-z0-9-]+",
        "[credential omitted]",
        normalized,
    )
    normalized = normalized.replace("<!", "<\u200b!")
    normalized = normalized.replace("@", "@\u200b")
    if len(normalized) > MAX_MESSAGE_CHARACTERS:
        normalized = normalized[: MAX_MESSAGE_CHARACTERS - 1].rstrip() + "…"
    return normalized


def configuration_is_ready() -> bool:
    """Return whether the non-secret Secret Manager identifiers are configured."""
    return not (
        GCP_PROJECT_ID.startswith("REPLACE_WITH_")
        or SECRET_NAME.startswith("REPLACE_WITH_")
    )


def read_webhook_url() -> str | None:
    """Read the webhook URL from Secret Manager without exposing it."""
    completed = subprocess.run(
        [
            "gcloud",
            "secrets",
            "versions",
            "access",
            SECRET_VERSION,
            "--secret",
            SECRET_NAME,
            "--project",
            GCP_PROJECT_ID,
        ],
        capture_output=True,
        text=True,
        timeout=GCLOUD_TIMEOUT_SECONDS,
        check=False,
    )
    if completed.returncode != 0:
        return None
    webhook_url = completed.stdout.strip()
    parsed = urllib.parse.urlparse(webhook_url)
    if parsed.scheme != "https" or parsed.hostname != "hooks.slack.com":
        return None
    return webhook_url


def post_to_slack(webhook_url: str, message: str) -> None:
    """Post a formatted Slack message without exposing the webhook response."""
    payload = {
        "text": message,
        "blocks": [
            {
                "type": "section",
                "text": {
                    "type": "mrkdwn",
                    "text": message,
                    "verbatim": True,
                },
            }
        ],
    }
    request = urllib.request.Request(
        webhook_url,
        data=json.dumps(payload).encode("utf-8"),
        headers={
            "Content-Type": "application/json; charset=utf-8",
            "User-Agent": "feedbackd/0.1",
        },
        method="POST",
    )
    with urllib.request.urlopen(request, timeout=SLACK_TIMEOUT_SECONDS) as response:
        response.read(32)


def main() -> int:
    """Attempt one silent submission and never interfere with the parent task."""
    try:
        message = sanitize_message(read_message(parse_arguments()))
        if not message or not configuration_is_ready():
            return 0
        webhook_url = read_webhook_url()
        if webhook_url is None:
            return 0
        post_to_slack(webhook_url, message)
    except Exception:
        pass
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

