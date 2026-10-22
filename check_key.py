#!/usr/bin/env python3
"""API Key Checker - Validate API keys from the command line (no CORS issues).
Usage: python3 check_key.py <API_KEY>
"""

import sys
import json
from urllib.request import Request, urlopen
from urllib.error import URLError, HTTPError

PROVIDERS = [
    {
        "name": "OpenAI",
        "prefix": "sk-",
        "test_key": lambda k: k.startswith("sk-"),
        "method": "GET",
        "endpoint": "https://api.openai.com/v1/models",
        "headers": lambda k: {"Authorization": f"Bearer {k}"},
        "validate": lambda r, c: c not in (401, 403),
    },
    {
        "name": "Anthropic",
        "prefix": "sk-ant-",
        "test_key": lambda k: k.startswith("sk-ant-"),
        "method": "POST",
        "endpoint": "https://api.anthropic.com/v1/messages",
        "headers": lambda k: {"x-api-key": k, "anthropic-version": "2023-06-01", "Content-Type": "application/json"},
        "body": {"model": "claude-3-haiku-20240307", "max_tokens": 1, "messages": [{"role": "user", "content": "hi"}]},
        "validate": lambda r, c: c not in (401, 403),
    },
    {
        "name": "Google Gemini",
        "prefix": "AIza",
        "test_key": lambda k: k.startswith("AIza"),
        "method": "GET",
        "endpoint": lambda k: f"https://generativelanguage.googleapis.com/v1/models?key={k}",
        # Google answers an invalid API key with HTTP 400 (API_KEY_INVALID),
        # not 401 - without it every bad Gemini key showed as VALID.
        "validate": lambda r, c: c not in (400, 401, 403),
    },
    {
        "name": "Groq",
        "prefix": "gsk_",
        "test_key": lambda k: k.startswith("gsk_"),
        "method": "GET",
        "endpoint": "https://api.groq.com/openai/v1/models",
        "headers": lambda k: {"Authorization": f"Bearer {k}"},
        "validate": lambda r, c: c not in (401, 403),
    },
    {
        "name": "Hugging Face",
        "prefix": "hf_",
        "test_key": lambda k: k.startswith("hf_"),
        "method": "GET",
        "endpoint": "https://huggingface.co/api/models",
        "headers": lambda k: {"Authorization": f"Bearer {k}"},
        "validate": lambda r, c: c not in (401, 403),
    },
    {
        "name": "Cohere",
        "prefix": "co",
        "test_key": lambda k: k.startswith("co"),
        "method": "GET",
        "endpoint": "https://api.cohere.ai/v1/models",
        "headers": lambda k: {"Authorization": f"Bearer {k}", "Content-Type": "application/json"},
        "validate": lambda r, c: c not in (401, 403),
    },
    {
        "name": "Together AI",
        "prefix": "tgp-",
        "test_key": lambda k: k.startswith("tgp-"),
        "method": "GET",
        "endpoint": "https://api.together.xyz/v1/models",
        "headers": lambda k: {"Authorization": f"Bearer {k}"},
        "validate": lambda r, c: c not in (401, 403),
    },
    {
        "name": "Mistral",
        "prefix": "xi-",
        "test_key": lambda k: k.startswith("xi-"),
        "method": "GET",
        "endpoint": "https://api.mistral.ai/v1/models",
        "headers": lambda k: {"Authorization": f"Bearer {k}"},
        "validate": lambda r, c: c not in (401, 403),
    },
    {
        "name": "Perplexity",
        "prefix": "pplx-",
        "test_key": lambda k: k.startswith("pplx-"),
        "method": "GET",
        "endpoint": "https://api.perplexity.ai/models",
        "headers": lambda k: {"Authorization": f"Bearer {k}"},
        "validate": lambda r, c: c not in (401, 403),
    },
    {
        "name": "Replicate",
        "prefix": "r8_",
        "test_key": lambda k: k.startswith("r8_"),
        "method": "GET",
        "endpoint": "https://api.replicate.com/v1/models",
        "headers": lambda k: {"Authorization": f"Key {k}"},
        "validate": lambda r, c: c not in (401, 403),
    },
    {
        "name": "ElevenLabs",
        "prefix": "sk_",
        "test_key": lambda k: k.startswith("sk_"),
        "method": "GET",
        "endpoint": "https://api.elevenlabs.io/v1/user",
        "headers": lambda k: {"xi-api-key": k},
        "validate": lambda r, c: c not in (401, 403),
    },
    {
        "name": "OpenRouter",
        "prefix": "sk-or-",
        "test_key": lambda k: k.startswith("sk-or-"),
        "method": "GET",
        "endpoint": "https://openrouter.ai/api/v1/models",
        "headers": lambda k: {"Authorization": f"Bearer {k}"},
        "validate": lambda r, c: c not in (401, 403),
    },
    {
        "name": "GitHub",
        "prefix": "ghp_",
        "test_key": lambda k: k.startswith("ghp_") or k.startswith("github_pat_"),
        "method": "GET",
        "endpoint": "https://api.github.com/user",
        "headers": lambda k: {"Authorization": f"Bearer {k}", "User-Agent": "API-Key-Checker"},
        "validate": lambda r, c: c not in (401, 403),
    },
    {
        "name": "GitLab",
        "prefix": "glpat-",
        "test_key": lambda k: k.startswith("glpat-"),
        "method": "GET",
        "endpoint": "https://gitlab.com/api/v4/user",
        "headers": lambda k: {"Authorization": f"Bearer {k}"},
        "validate": lambda r, c: c not in (401, 403),
    },
    {
        "name": "DeepSeek",
        "prefix": "sk-",
        "test_key": lambda k: k.startswith("sk-"),
        "method": "GET",
        "endpoint": "https://api.deepseek.com/v1/models",
        "headers": lambda k: {"Authorization": f"Bearer {k}"},
        "validate": lambda r, c: c not in (401, 403),
    },
    {
        "name": "NVIDIA",
        "prefix": "nvapi-",
        "test_key": lambda k: k.startswith("nvapi-"),
        "method": "POST",
        "endpoint": "https://integrate.api.nvidia.com/v1/chat/completions",
        "headers": lambda k: {"Authorization": f"Bearer {k}", "Content-Type": "application/json"},
        "body": {"model": "moonshotai/kimi-k2.6", "messages": [{"role": "user", "content": "test"}], "max_tokens": 1},
        "validate": lambda r, c: c not in (401, 403),
    },
]


def pick_providers(key):
    """Providers whose pattern matches the key, minus less-specific ones.

    Several prefixes nest (sk-ant- and sk-or- both start with sk-). Without
    this filter a valid Anthropic key was also tested as OpenAI and DeepSeek
    and reported INVALID by both - a false alarm for a perfectly good key."""
    matched = [p for p in PROVIDERS if p["test_key"](key)]
    keep = []
    for p in matched:
        mine = p["prefix"]
        more_specific = any(
            other is not p and other["prefix"] != mine and other["prefix"].startswith(mine)
            for other in matched
        )
        if not more_specific:
            keep.append(p)
    return keep


def check_key(key):
    matched = pick_providers(key)
    if not matched:
        print("Could not auto-detect provider. Try these patterns:")
        for p in PROVIDERS:
            print(f"  {p['name']:15s} {p['prefix']}...")
        return

    for provider in matched:
        name = provider["name"]
        try:
            endpoint = provider["endpoint"](key) if callable(provider["endpoint"]) else provider["endpoint"]
            headers = provider.get("headers", lambda k: {})(key) or {}
            body = provider.get("body")

            data = json.dumps(body).encode() if body else None
            req = Request(endpoint, data=data, headers=headers, method=provider["method"])

            try:
                resp = urlopen(req, timeout=10)
                code = resp.status
            except HTTPError as e:
                code = e.code

            valid = provider["validate"](None, code)
            icon = "\u2705" if valid else "\u274c"
            status = "VALID" if valid else "INVALID"
            print(f"  {icon} {name}: {status} (HTTP {code})")
        except Exception as e:
            print(f"  \u26a0\ufe0f  {name}: ERROR - {e}")


if __name__ == "__main__":
    if len(sys.argv) < 2:
        print(f"Usage: python3 {sys.argv[0]} <API_KEY>")
        print("Example: python3 check_key.py sk-xxxxxxxxxxxx")
        sys.exit(1)
    check_key(sys.argv[1])
