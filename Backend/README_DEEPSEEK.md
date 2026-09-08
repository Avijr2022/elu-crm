DeepSeek Integration
====================

This document describes the DeepSeek integration added to the Backend and how to secure, configure, and use it.

Files added/changed
- `app/deepseek_client.py` — API client wrapper
- `app/api/v1/integrations/deepseek.py` — FastAPI endpoint (`/api/v1/integrations/deepseek/generate`)
- `app/utils/redis_rate_limiter.py` — Redis helpers for distributed rate limiting and token metrics
- `scripts/test_deepseek.py` — minimal token-check script

Configuration
- Set `DEEPSEEK_API_KEY` in the environment (Docker secrets, CI secrets, or user env).
- Optionally set `REDIS_URL` (default `redis://localhost:6379/0`) to enable distributed rate limiting and metrics.

Security / Key scrub guidance
1. Rotate the exposed key immediately (create a new key from DeepSeek console).
2. Remove the leaked key from Git history. Recommended approach (requires `git` and `git-filter-repo`):

```bash
# Install git-filter-repo if not present
pip install git-filter-repo

# Replace the key in the entire history
git filter-repo --invert-paths --path .continue/config.yaml --force
# Or use an email/key replacement:
git filter-repo --replace-text <(echo "sk-OLD-KEY==>REDACTED")

# Force push (coordinate with your team)
git push --force --all
git push --force --tags
```

If you prefer a simpler tool, consider the BFG Repo Cleaner (https://rtyley.github.io/bfg-repo-cleaner/).

Operational notes
- The endpoint enforces distributed global and per-tenant rate limits using Redis. For production, run a Redis instance accessible to all API nodes.
- Token usage is recorded daily into Redis hashes for billing/monitoring.
- The endpoint requires a valid JWT access token (uses existing `get_current_user` dependency).

Testing
- Quick local test (requires `DEEPSEEK_API_KEY` in env):
```powershell
$env:DEEPSEEK_API_KEY = 'sk-REPLACE'
python Backend/scripts/test_deepseek.py
```

Usage examples
-------------

1) Simple curl (DeepSeek generation):

```bash
curl -s -X POST https://api.deepseek.com/v1/responses \
	-H "Authorization: Bearer $DEEPSEEK_API_KEY" \
	-H "Content-Type: application/json" \
	-d '{"model":"deepseek-v4-flash","input":"Write a short email","max_tokens":50}'
```

2) Python (httpx) example using the `DeepSeekClient` wrapper:

```python
from app.deepseek_client import DeepSeekClient

client = DeepSeekClient()
if not client.has_api_key():
		raise RuntimeError('DEEPSEEK_API_KEY not set')

resp = client.generate('Summarize this ticket in one sentence', max_tokens=60)
print(resp)
```

3) Node (fetch) example:

```js
const fetch = require('node-fetch');

const resp = await fetch('https://api.deepseek.com/v1/responses', {
	method: 'POST',
	headers: {
		'Authorization': `Bearer ${process.env.DEEPSEEK_API_KEY}`,
		'Content-Type': 'application/json',
	},
	body: JSON.stringify({ model: 'deepseek-v4-flash', input: 'Write an email', max_tokens: 50 }),
});
const data = await resp.json();
console.log(data);
```

4) Allocation API example (curl) — allocate full or partial amount:

```bash
# Allocate full (no allocated_amount provided)
curl -X POST http://localhost:8000/fin/payment-receipts/<RECEIPT_ID>/allocate \
	-H "Authorization: Bearer $ACCESS_TOKEN" \
	-H "Content-Type: application/json" \
	-d '{"invoice_id":"<INVOICE_ID>"}'

# Allocate partial amount (e.g. 1000.50)
curl -X POST http://localhost:8000/fin/payment-receipts/<RECEIPT_ID>/allocate \
	-H "Authorization: Bearer $ACCESS_TOKEN" \
	-H "Content-Type: application/json" \
	-d '{"invoice_id":"<INVOICE_ID>", "allocated_amount":1000.50}'
```

Contact
- If you want, I can scrub the leaked key and add CI secrets guidance — confirm and I'll prepare a safe plan.
