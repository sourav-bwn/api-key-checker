"""Offline tests for check_key.py. No network: urlopen is stubbed."""
import contextlib
import importlib.util
import io
import json
import os
import sys
import unittest
from urllib.error import HTTPError

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
import check_key


class PickProvidersTests(unittest.TestCase):
    def names(self, key):
        return [p["name"] for p in check_key.pick_providers(key)]

    def test_anthropic_key_only_matches_anthropic(self):
        # sk-ant- also starts with sk-; OpenAI/DeepSeek must not claim it and
        # report a valid Anthropic key as INVALID.
        self.assertEqual(self.names("sk-ant-api03-abcdef1234567890"), ["Anthropic"])

    def test_openrouter_key_only_matches_openrouter(self):
        self.assertEqual(self.names("sk-or-v1-abcdef1234567890"), ["OpenRouter"])

    def test_generic_openai_style_key_keeps_ambiguous_providers(self):
        names = self.names("sk-abcdef1234567890abcdef")
        self.assertIn("OpenAI", names)
        self.assertIn("DeepSeek", names)
        self.assertNotIn("Anthropic", names)

    def test_groq_gemini_github_nvidia(self):
        self.assertEqual(self.names("gsk_abc"), ["Groq"])
        self.assertEqual(self.names("AIzaSyabc"), ["Google Gemini"])
        self.assertEqual(self.names("ghp_abc"), ["GitHub"])
        self.assertEqual(self.names("nvapi-abc"), ["NVIDIA"])

    def test_unknown_key_matches_nothing(self):
        self.assertEqual(self.names("zzz-nothing"), [])


class ValidateTests(unittest.TestCase):
    def by_name(self, name):
        return next(p for p in check_key.PROVIDERS if p["name"] == name)

    def test_gemini_rejects_http_400(self):
        # Google answers an invalid API key with 400 API_KEY_INVALID.
        v = self.by_name("Google Gemini")["validate"]
        self.assertFalse(v(None, 400), "a bad Gemini key returns 400 and must be INVALID")
        self.assertTrue(v(None, 200))
        self.assertTrue(v(None, 429), "quota errors still mean the key is real")
        self.assertFalse(v(None, 403))

    def test_replicate_uses_bearer_scheme(self):
        # Replicate documents Bearer (current) and Token (legacy); "Key" is not
        # a supported scheme and would 401 a perfectly good key.
        h = self.by_name("Replicate")["headers"]("r8_abc")
        self.assertEqual(h["Authorization"], "Bearer r8_abc")

    def test_standard_providers_reject_401_403_only(self):
        for name in ("OpenAI", "Groq", "DeepSeek", "OpenRouter"):
            v = self.by_name(name)["validate"]
            self.assertFalse(v(None, 401), name)
            self.assertTrue(v(None, 200), name)


class CliOutputTests(unittest.TestCase):
    def run_cli(self, key, statuses):
        """statuses: dict of provider name -> HTTP code (or None for network error)."""
        real_urlopen = check_key.urlopen

        class FakeResp:
            def __init__(self, code):
                self.status = code

        def fake_urlopen(req, timeout=10):
            url = req.full_url
            for p in check_key.PROVIDERS:
                ep = p["endpoint"] if isinstance(p["endpoint"], str) else p["endpoint"](key)
                if url == ep:
                    code = statuses.get(p["name"], 200)
                    if code >= 400:
                        raise HTTPError(url, code, "err", {}, None)
                    return FakeResp(code)
            raise AssertionError(f"unexpected URL {url}")

        check_key.urlopen = fake_urlopen
        try:
            buf = io.StringIO()
            with contextlib.redirect_stdout(buf):
                check_key.check_key(key)
            return buf.getvalue()
        finally:
            check_key.urlopen = real_urlopen

    def test_valid_anthropic_key_not_reported_invalid_elsewhere(self):
        out = self.run_cli("sk-ant-api03-abcdef1234567890", {"Anthropic": 200})
        self.assertIn("Anthropic: VALID", out)
        self.assertNotIn("OpenAI", out, "an Anthropic key must not be tested as OpenAI")
        self.assertNotIn("DeepSeek", out)

    def test_invalid_gemini_key_shows_invalid(self):
        out = self.run_cli("AIzaSybad", {"Google Gemini": 400})
        self.assertIn("Google Gemini: INVALID (HTTP 400)", out)

    def test_help_lists_real_prefixes(self):
        out = self.run_cli("zzz-nothing", {})
        self.assertIn("OpenAI", out)
        self.assertIn("sk-...", out, "the help must print the actual key patterns")
        self.assertIn("nvapi-...", out)


if __name__ == "__main__":
    unittest.main()
