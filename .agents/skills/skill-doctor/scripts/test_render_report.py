#!/usr/bin/env python3
"""Tests for skill-doctor report rendering."""

import unittest
from pathlib import Path

from render_report import embedded_diffs_script, render_page


class ReportRendererTests(unittest.TestCase):
    def test_code_diffs_follow_os_theme(self):
        bundle = embedded_diffs_script()

        self.assertIn('themeType:"system"', bundle)
        self.assertIn(
            'theme:{dark:"pierre-dark",light:"pierre-light"}',
            bundle,
        )

    def test_report_follows_os_theme(self):
        page = render_page({
            "scores": {
                "efficiency": 1.0,
                "code_quality": 1.0,
                "skill_coverage": 1.0,
                "overall": 1.0,
            },
        })

        self.assertIn('<meta name="color-scheme" content="light dark">', page)
        self.assertIn("@media (prefers-color-scheme: dark)", page)
        self.assertIn("--page-bg: #0f0d14", page)
        self.assertIn("background: var(--surface)", page)

    def test_factories_footer_is_sticky_and_contains_inline_cta(self):
        report = {
            "title": "Agent Skill Report",
            "generated_at": "2026-08-25T00:00:00Z",
            "harness": "codex",
            "handle": "example",
            "stats": {
                "sessions_analyzed": 1,
                "sessions_scanned": 1,
                "skills_found": 1,
                "skills_used": 1,
                "window_days": 45,
            },
            "scores": {
                "efficiency": 1.0,
                "code_quality": 1.0,
                "skill_coverage": 1.0,
                "overall": 1.0,
            },
            "top_findings": ["No material waste detected."],
            "suggestions": [],
            "cta_url": "https://warp.dev/factories/request-access",
        }

        page = render_page(report)

        self.assertNotIn("<h2>Do this automatically</h2>", page)
        self.assertIn('<div class="stamp-row row factories-footer">', page)
        self.assertIn(
            '<div class="stamp-name">Do this automatically with Warp Factories</div>',
            page,
        )
        self.assertIn(".factories-footer { position: sticky; bottom: 16px;", page)

    def test_skill_output_uses_warp_factories_label(self):
        skill_path = Path(__file__).resolve().parent.parent / "SKILL.md"

        self.assertIn(
            "- Automate this with Warp Factories: [Request early access]",
            skill_path.read_text(),
        )


if __name__ == "__main__":
    unittest.main()
