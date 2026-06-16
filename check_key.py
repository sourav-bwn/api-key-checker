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
        "test_key": lambda k: k.startswith("sk-"),
        "method": "GET",
        "endpoint": "https://api.openai.com/v1/models",
        "headers": lambda k: {"Authorization": f"Bearer {k}"},
        "validate": lambda r, c: c not in (401, 403),
    },
    {
        "name": "Anthropic",
        "test_key": lambda k: k.startswith("sk-ant-"),
        "method": "POST",
        "endpoint": "https://api.anthropic.com/v1/messages",
        "headers": lambda k: {"x-api-key": k, "anthropic-version": "2023-06-01", "Content-Type": "application/json"},
        "body": {"model": "claude-3-haiku-20240307", "max_tokens": 1, "messages": [{"role": "user", "content": "hi"}]},
        "validate": lambda r, c: c not in (401, 403),
    },
    {
        "name": "Google Gemini",
        "test_key": lambda k: k.startswith("AIza"),
        "method": "GET",
        "endpoint": lambda k: f"https://generativelanguage.googleapis.com/v1/models?key={k}",
        "validate": lambda r, c: c not in (401, 403),
    },
    {
        "name": "Groq",
        "test_key": lambda k: k.startswith("gsk_"),
        "method": "GET",
        "endpoint": "https://api.groq.com/openai/v1/models",
        "headers": lambda k: {"Authorization": f"Bearer {k}"},
        "validate": lambda r, c: c not in (401, 403),
    },
    {
        "name": "Hugging Face",
        "test_key": lambda k: k.startswith("hf_"),
        "method": "GET",
        "endpoint": "https://huggingface.co/api/models",
        "headers": lambda k: {"Authorization": f"Bearer {k}"},
        "validate": lambda r, c: c not in (401, 403),
    },
    {
        "name": "Cohere",
        "test_key": lambda k: k.startswith("co"),
        "method": "GET",
        "endpoint": "https://api.cohere.ai/v1/models",
        "headers": lambda k: {"Authorization": f"Bearer {k}", "Content-Type": "application/json"},
        "validate": lambda r, c: c not in (401, 403),
    },
    {
        "name": "Together AI",
        "test_key": lambda k: k.startswith("tgp-"),
        "method": "GET",
        "endpoint": "https://api.together.xyz/v1/models",
        "headers": lambda k: {"Authorization": f"Bearer {k}"},
        "validate": lambda r, c: c not in (401, 403),
    },
    {
        "name": "Mistral",
        "test_key": lambda k: k.startswith("xi-"),
        "method": "GET",
        "endpoint": "https://api.mistral.ai/v1/models",
        "headers": lambda k: {"Authorization": f"Bearer {k}"},
        "validate": lambda r, c: c not in (401, 403),
    },
    {
        "name": "Perplexity",
        "test_key": lambda k: k.startswith("pplx-"),
        "method": "GET",
        "endpoint": "https://api.perplexity.ai/models",
        "headers": lambda k: {"Authorization": f"Bearer {k}"},
        "validate": lambda r, c: c not in (401, 403),
    },
    {
        "name": "Replicate",
        "test_key": lambda k: k.startswith("r8_"),
        "method": "GET",
        "endpoint": "https://api.replicate.com/v1/models",
        "headers": lambda k: {"Authorization": f"Key {k}"},
        "validate": lambda r, c: c not in (401, 403),
    },
    {
        "name": "ElevenLabs",
        "test_key": lambda k: k.startswith("sk_"),
        "method": "GET",
        "endpoint": "https://api.elevenlabs.io/v1/user",
        "headers": lambda k: {"xi-api-key": k},
        "validate": lambda r, c: c not in (401, 403),
    },
    {
        "name": "OpenRouter",
        "test_key": lambda k: k.startswith("sk-or-"),
        "method": "GET",
        "endpoint": "https://openrouter.ai/api/v1/models",
        "headers": lambda k: {"Authorization": f"Bearer {k}"},
        "validate": lambda r, c: c not in (401, 403),
    },
    {
        "name": "GitHub",
        "test_key": lambda k: k.startswith("ghp_") or k.startswith("github_pat_"),
        "method": "GET",
        "endpoint": "https://api.github.com/user",
        "headers": lambda k: {"Authorization": f"Bearer {k}", "User-Agent": "API-Key-Checker"},
        "validate": lambda r, c: c not in (401, 403),
    },
    {
        "name": "GitLab",
        "test_key": lambda k: k.startswith("glpat-"),
        "method": "GET",
        "endpoint": "https://gitlab.com/api/v4/user",
        "headers": lambda k: {"Authorization": f"Bearer {k}"},
        "validate": lambda r, c: c not in (401, 403),
    },
    {
        "name": "DeepSeek",
        "test_key": lambda k: k.startswith("sk-"),
        "method": "GET",
        "endpoint": "https://api.deepseek.com/v1/models",
        "headers": lambda k: {"Authorization": f"Bearer {k}"},
        "validate": lambda r, c: c not in (401, 403),
    },
    {
        "name": "NVIDIA",
        "test_key": lambda k: k.startswith("nvapi-"),
        "method": "POST",
        "endpoint": "https://integrate.api.nvidia.com/v1/chat/completions",
        "headers": lambda k: {"Authorization": f"Bearer {k}", "Content-Type": "application/json"},
        "body": {"model": "moonshotai/kimi-k2.6", "messages": [{"role": "user", "content": "test"}], "max_tokens": 1},
        "validate": lambda r, c: c not in (401, 403),
    },
]


def check_key(key):
    matched = [p for p in PROVIDERS if p["test_key"](key)]
    if not matched:
        print("Could not auto-detect provider. Try these patterns:")
        for p in PROVIDERS:
            print(f"  {p['name']:15s} {p['test_key'].__doc__ or ''}")
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
