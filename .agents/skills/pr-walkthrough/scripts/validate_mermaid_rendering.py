#!/usr/bin/env python3
"""Validate Mermaid diagrams in a generated PR walkthrough.

This script performs two checks:

- Static extraction/linting of Mermaid sources embedded in the walkthrough HTML.
- Optional browser rendering validation via Playwright, which catches Mermaid
  runtime parse errors and diagrams that fail to produce SVG output.

Use `--require-browser` when a browser-capable environment is available. If the
browser check is required and unavailable, the script exits non-zero so the
walkthrough is not reported as ready without rendered-diagram validation.
"""

from __future__ import annotations

import argparse
import html
import re
import sys
from dataclasses import dataclass
from html.parser import HTMLParser
from pathlib import Path
from typing import Iterable


KNOWN_DIAGRAM_PREFIXES = (
    "flowchart",
    "graph",
    "sequenceDiagram",
    "classDiagram",
    "stateDiagram",
    "stateDiagram-v2",
    "erDiagram",
    "journey",
    "gantt",
    "pie",
    "mindmap",
    "timeline",
    "quadrantChart",
    "requirementDiagram",
    "gitGraph",
)


@dataclass
class MermaidSource:
    index: int
    source: str


class MermaidExtractor(HTMLParser):
    def __init__(self) -> None:
        super().__init__()
        self.sources: list[str] = []
        self._capture_depth = 0
        self._parts: list[str] = []

    def handle_starttag(self, tag: str, attrs: list[tuple[str, str | None]]) -> None:
        attrs_dict = dict(attrs)
        classes = set((attrs_dict.get("class") or "").split())
        if tag == "div" and "mermaid" in classes:
            self._capture_depth = 1
            self._parts = []
        elif self._capture_depth:
            self._capture_depth += 1

    def handle_endtag(self, tag: str) -> None:
        if not self._capture_depth:
            return
        self._capture_depth -= 1
        if self._capture_depth == 0:
            self.sources.append(html.unescape("".join(self._parts)).strip())
            self._parts = []

    def handle_data(self, data: str) -> None:
        if self._capture_depth:
            self._parts.append(data)

    def handle_entityref(self, name: str) -> None:
        if self._capture_depth:
            self._parts.append(f"&{name};")

    def handle_charref(self, name: str) -> None:
        if self._capture_depth:
            self._parts.append(f"&#{name};")


def extract_sources(html_text: str) -> list[MermaidSource]:
    parser = MermaidExtractor()
    parser.feed(html_text)
    return [MermaidSource(index=i + 1, source=source) for i, source in enumerate(parser.sources)]


def first_nonempty_line(source: str) -> str:
    for line in source.splitlines():
        stripped = line.strip()
        if stripped:
            return stripped
    return ""


def lint_state_diagram(source: str) -> Iterable[str]:
    first = first_nonempty_line(source)
    if not first.startswith("stateDiagram"):
        return []

    allowed_prefixes = (
        "stateDiagram",
        "direction ",
        "[*]",
        "state ",
        "note ",
        "classDef ",
        "class ",
        "hide empty description",
        "choice ",
        "fork ",
        "join ",
        "--",
    )
    errors: list[str] = []
    for line_number, raw_line in enumerate(source.splitlines(), start=1):
        line = raw_line.strip()
        if not line or line.startswith("%%"):
            continue
        if "->" in line or "-->" in line or ":" in line:
            continue
        if line.startswith(allowed_prefixes):
            continue
        errors.append(
            f"line {line_number}: suspicious standalone stateDiagram token {line!r}; "
            "use a transition, `state <name>`, or a note"
        )
    return errors


def static_lint(sources: list[MermaidSource], html_text: str) -> list[str]:
    errors: list[str] = []
    if "mermaid@latest" in html_text.lower() or "/mermaid/latest" in html_text.lower():
        errors.append("HTML uses an unpinned Mermaid `latest` runtime")
    if not sources:
        return errors

    for item in sources:
        first = first_nonempty_line(item.source)
        if not first:
            errors.append(f"diagram {item.index}: empty Mermaid source")
            continue
        if not any(first.startswith(prefix) for prefix in KNOWN_DIAGRAM_PREFIXES):
            errors.append(f"diagram {item.index}: unknown Mermaid diagram header {first!r}")
        for message in lint_state_diagram(item.source):
            errors.append(f"diagram {item.index}: {message}")
    return errors


def browser_validate(html_path: Path, timeout_ms: int) -> tuple[bool, str]:
    try:
        from playwright.sync_api import sync_playwright
    except Exception as exc:
        return False, f"Playwright is unavailable: {exc}"

    url = html_path.resolve().as_uri()
    with sync_playwright() as playwright:
        browser = None
        launch_errors: list[str] = []
        for label, kwargs in (
            ("bundled Chromium", {}),
            ("system Chrome", {"channel": "chrome"}),
            ("system Chromium", {"channel": "chromium"}),
        ):
            try:
                browser = playwright.chromium.launch(**kwargs)
                break
            except Exception as exc:
                launch_errors.append(f"{label}: {exc}")
        if browser is None:
            return False, "Unable to launch a Playwright browser. " + " | ".join(launch_errors)
        try:
            page = browser.new_page()
            page.goto(url, wait_until="domcontentloaded", timeout=timeout_ms)
            page.wait_for_function(
                """
                () => document.body.classList.contains('mermaid-ready') ||
                      document.body.classList.contains('mermaid-has-errors') ||
                      Array.from(document.querySelectorAll('.mermaid-artifact')).some(
                        (figure) => figure.classList.contains('mermaid-failed')
                      )
                """,
                timeout=timeout_ms,
            )
            result = page.evaluate(
                """
                () => Array.from(document.querySelectorAll('.mermaid-artifact')).map((figure, index) => {
                  const node = figure.querySelector('.mermaid');
                  const text = node ? node.textContent || '' : '';
                  return {
                    index: index + 1,
                    rendered: figure.classList.contains('mermaid-rendered'),
                    failed: figure.classList.contains('mermaid-failed'),
                    hasSvg: Boolean(node && node.querySelector('svg')),
                    error: figure.dataset.mermaidError || '',
                    textHasError: /Syntax error|Parse error|Lexical error|mermaid version/i.test(text),
                  };
                })
                """
            )
        except Exception as exc:
            return False, f"browser validation failed while loading or inspecting the page: {exc}"
        finally:
            browser.close()

    failures = [
        item
        for item in result
        if item["failed"] or not item["rendered"] or not item["hasSvg"] or item["textHasError"]
    ]
    if failures:
        details = "; ".join(
            f"diagram {item['index']} rendered={item['rendered']} hasSvg={item['hasSvg']} "
            f"failed={item['failed']} error={item['error'] or 'rendered error text'}"
            for item in failures
        )
        return False, details
    return True, f"browser rendered {len(result)} Mermaid diagram(s) successfully"


def main() -> int:
    parser = argparse.ArgumentParser(description="Validate Mermaid rendering in a PR walkthrough HTML file.")
    parser.add_argument("--html", required=True, type=Path, help="Path to .warp/pr-walkthrough/index.html")
    parser.add_argument(
        "--require-browser",
        action="store_true",
        help="Fail if browser rendering validation via Playwright cannot be performed.",
    )
    parser.add_argument("--timeout-ms", type=int, default=15000, help="Browser validation timeout.")
    args = parser.parse_args()

    html_path = args.html
    html_text = html_path.read_text()
    sources = extract_sources(html_text)
    print(f"Found {len(sources)} Mermaid diagram source(s).")

    errors = static_lint(sources, html_text)
    if errors:
        for error in errors:
            print(f"FAIL - {error}")
        return 1

    if not sources:
        print("No Mermaid diagrams found; render validation is not needed.")
        return 0

    ok, message = browser_validate(html_path, args.timeout_ms)
    if ok:
        print(f"PASS - {message}")
        return 0

    prefix = "FAIL" if args.require_browser else "WARN"
    print(f"{prefix} - {message}")
    return 1 if args.require_browser else 0


if __name__ == "__main__":
    raise SystemExit(main())
