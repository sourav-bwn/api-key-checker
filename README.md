# API Key Checker

Instantly validate API keys across 20+ AI/developer providers - in the browser
or from your terminal. No server, no sign-up: keys are only ever sent to the
provider they belong to.

## Web checker

Open `checker.html` (or visit the deployed site) and paste a key. The provider
is auto-detected from the key format and the key is tested against that
provider's API. Some providers block browser calls with CORS; when that
happens the checker shows the equivalent `curl` command, or you can use the
CLI below.

## CLI (no CORS issues)

```bash
python3 check_key.py <API_KEY>
```

Prints `VALID` / `INVALID` with the HTTP status for each provider whose
pattern matches the key. When several prefixes nest (for example `sk-ant-`
inside `sk-`), only the most specific provider is tested so a valid key is
never reported invalid by a look-alike provider.

## Tests

No network or real keys needed (HTTP calls are stubbed):

```bash
python3 -m unittest discover -s tests   # CLI checker
node --test tests/*.test.js             # browser checker (or: npm test)
```

## How detection works

Each provider declares a key prefix (e.g. `sk-ant-`, `gsk_`, `AIza`,
`nvapi-`). A key is only tested against the most specific matching providers.
`INVALID` means the provider itself rejected the key (401/403, or 400 for
Google API keys); any other response means the provider accepted it.
