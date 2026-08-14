#!/usr/bin/env python3
"""Regression tests for the feedback webhook resolver in both submit.py scripts.

Covers the security-sensitive resolution order shared by the `suggestion-box`
and `complain` skills:

- a valid managed-secret env var takes precedence over the gcloud lookup;
- an absent, empty, blank, or invalid env var falls back to gcloud unchanged;
- strict HTTPS + exact-hostname validation rejects lookalike/userinfo hosts;
- the webhook value never appears in stdout, stderr, or diagnostics.

Run with: python3 -m unittest discover -s tests
These tests never perform real network I/O and never contact Slack.
"""

from __future__ import annotations

import importlib.util
import io
import os
import unittest
from contextlib import redirect_stderr, redirect_stdout
from pathlib import Path
from unittest import mock

REPO_ROOT = Path(__file__).resolve().parent.parent
SKILL_SCRIPTS = {
    "suggestion-box": REPO_ROOT / ".agents/skills/suggestion-box/submit.py",
    "complain": REPO_ROOT / ".agents/skills/complain/submit.py",
}

VALID_URL = "https://hooks.slack.com/services/T000/B000/xxxxSECRETxxxx"

# URLs that must be rejected: wrong scheme, lookalike hosts, and a userinfo
# prefix whose real host is an attacker domain (a naive substring check on
# "hooks.slack.com" would wrongly accept several of these).
INVALID_URLS = [
    "http://hooks.slack.com/services/T/B/x",          # not HTTPS
    "https://hooks.slack.com.evil.com/services/x",     # suffix lookalike
    "https://evilhooks.slack.com/services/x",          # prefix lookalike
    "https://not-hooks.slack.com/services/x",          # substring, wrong host
    "https://hooks.slack.com@evil.com/services/x",     # userinfo-prefixed host
    "https://slack.com/services/x",                    # different host
    "ftp://hooks.slack.com/services/x",                # wrong scheme
    "hooks.slack.com/services/x",                       # no scheme
    "not even a url",
]


def load_module(name: str, path: Path):
    spec = importlib.util.spec_from_file_location(
        f"submit_{name.replace('-', '_')}", path
    )
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


class WebhookResolverTests(unittest.TestCase):
    def setUp(self):
        self.modules = {
            name: load_module(name, path) for name, path in SKILL_SCRIPTS.items()
        }

    def each_module(self):
        for name, module in self.modules.items():
            with self.subTest(skill=name):
                yield name, module

    # --- validation ------------------------------------------------------

    def test_is_valid_webhook_url_accepts_https_hooks_slack(self):
        for _name, module in self.each_module():
            self.assertTrue(module.is_valid_webhook_url(VALID_URL))

    def test_is_valid_webhook_url_rejects_lookalikes_and_bad_schemes(self):
        for _name, module in self.each_module():
            for bad in INVALID_URLS:
                self.assertFalse(
                    module.is_valid_webhook_url(bad),
                    msg=f"should reject {bad!r}",
                )

    def test_validate_webhook_url_raises_for_invalid(self):
        for _name, module in self.each_module():
            with self.assertRaises(module.SubmissionError):
                module.validate_webhook_url("https://evil.com/x", "configured secret")

    # --- env var reading -------------------------------------------------

    def test_env_absent_returns_none(self):
        for _name, module in self.each_module():
            with mock.patch.dict(os.environ, {}, clear=False):
                os.environ.pop(module.WEBHOOK_URL_ENV_VAR, None)
                self.assertIsNone(module.read_webhook_url_from_env())

    def test_env_empty_or_blank_returns_none(self):
        for _name, module in self.each_module():
            for blank in ["", "   ", "\t\n "]:
                with mock.patch.dict(
                    os.environ, {module.WEBHOOK_URL_ENV_VAR: blank}
                ):
                    self.assertIsNone(module.read_webhook_url_from_env())

    def test_env_invalid_returns_none(self):
        for _name, module in self.each_module():
            for bad in INVALID_URLS:
                with mock.patch.dict(os.environ, {module.WEBHOOK_URL_ENV_VAR: bad}):
                    self.assertIsNone(
                        module.read_webhook_url_from_env(),
                        msg=f"invalid env {bad!r} must yield None",
                    )

    def test_env_valid_is_returned_and_stripped(self):
        for _name, module in self.each_module():
            with mock.patch.dict(
                os.environ, {module.WEBHOOK_URL_ENV_VAR: f"  {VALID_URL}  "}
            ):
                self.assertEqual(module.read_webhook_url_from_env(), VALID_URL)

    # --- resolution order (precedence + fallback) ------------------------

    def test_valid_env_takes_precedence_over_gcloud(self):
        for _name, module in self.each_module():
            with mock.patch.dict(
                os.environ, {module.WEBHOOK_URL_ENV_VAR: VALID_URL}
            ), mock.patch.object(
                module,
                "read_webhook_url",
                side_effect=AssertionError("gcloud must not run"),
            ):
                self.assertEqual(module.resolve_webhook_url(), VALID_URL)

    def test_absent_env_falls_back_to_gcloud(self):
        for _name, module in self.each_module():
            with mock.patch.dict(os.environ, {}, clear=False), mock.patch.object(
                module, "read_webhook_url", return_value="GCLOUD_URL"
            ) as gcloud:
                os.environ.pop(module.WEBHOOK_URL_ENV_VAR, None)
                self.assertEqual(module.resolve_webhook_url(), "GCLOUD_URL")
                gcloud.assert_called_once()

    def test_empty_blank_invalid_env_all_fall_back_to_gcloud(self):
        cases = ["", "   ", *INVALID_URLS]
        for _name, module in self.each_module():
            for value in cases:
                with mock.patch.dict(
                    os.environ, {module.WEBHOOK_URL_ENV_VAR: value}
                ), mock.patch.object(
                    module, "read_webhook_url", return_value="GCLOUD_URL"
                ) as gcloud:
                    self.assertEqual(
                        module.resolve_webhook_url(),
                        "GCLOUD_URL",
                        msg=f"env {value!r} should fall back to gcloud",
                    )
                    gcloud.assert_called_once()

    # --- secret never leaks to output ------------------------------------

    def test_webhook_value_never_leaks_via_env_path(self):
        # Even if a downstream error message carries the URL, report_failure's
        # sanitization must keep it out of stdout/stderr; exit stays 0.
        for _name, module in self.each_module():
            stdout, stderr = io.StringIO(), io.StringIO()
            with mock.patch.dict(
                os.environ, {module.WEBHOOK_URL_ENV_VAR: VALID_URL}
            ), mock.patch.object(
                module,
                "post_to_slack",
                side_effect=module.SubmissionError(f"boom {VALID_URL}"),
            ), mock.patch(
                "sys.argv", ["submit.py", "hello"]
            ), redirect_stdout(stdout), redirect_stderr(stderr):
                rc = module.main()
            self.assertEqual(rc, 0)
            combined = stdout.getvalue() + stderr.getvalue()
            self.assertNotIn(VALID_URL, combined)
            self.assertNotIn("xxxxSECRETxxxx", combined)

    def test_webhook_value_never_leaks_via_gcloud_path(self):
        for _name, module in self.each_module():
            stdout, stderr = io.StringIO(), io.StringIO()
            with mock.patch.dict(os.environ, {}, clear=False), mock.patch.object(
                module, "read_webhook_url", return_value=VALID_URL
            ), mock.patch.object(
                module,
                "post_to_slack",
                side_effect=module.SubmissionError(f"boom {VALID_URL}"),
            ), mock.patch(
                "sys.argv", ["submit.py", "hello"]
            ), redirect_stdout(stdout), redirect_stderr(stderr):
                os.environ.pop(module.WEBHOOK_URL_ENV_VAR, None)
                rc = module.main()
            self.assertEqual(rc, 0)
            combined = stdout.getvalue() + stderr.getvalue()
            self.assertNotIn(VALID_URL, combined)
            self.assertNotIn("xxxxSECRETxxxx", combined)

    def test_main_uses_env_webhook_end_to_end(self):
        for _name, module in self.each_module():
            with mock.patch.dict(
                os.environ, {module.WEBHOOK_URL_ENV_VAR: VALID_URL}
            ), mock.patch.object(
                module,
                "read_webhook_url",
                side_effect=AssertionError("gcloud must not run"),
            ), mock.patch.object(
                module, "post_to_slack"
            ) as post, mock.patch(
                "sys.argv", ["submit.py", "hello from test"]
            ):
                rc = module.main()
            self.assertEqual(rc, 0)
            post.assert_called_once()
            self.assertEqual(post.call_args[0][0], VALID_URL)


if __name__ == "__main__":
    unittest.main()
