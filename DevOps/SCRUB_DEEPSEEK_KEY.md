# Scrub DeepSeek API Key from Git history and rotate

If a DeepSeek API key was accidentally committed, follow these steps to remove it from history and rotate the key.

WARNING: Rewriting git history rewrites commits and changes commit hashes — coordinate with your team before pushing these changes.

1) Rotate the key immediately at the provider (DeepSeek) and create a new key. Do NOT use the old key again.

2) Locally remove the secret from working files (already done: `.continue/config.yaml` now uses `apiKeyEnv`).

3) Use `git filter-repo` (preferred) to remove the secret from all history. Example:

```bash
# Install git-filter-repo if not present
python3 -m pip install git-filter-repo

# Run from repo root (make a backup first)
git clone --mirror . repo-backup.git
python3 -m git_filter_repo --replace-text <(echo "sk-[0-9A-Za-z]\{8,\}==> [REDACTED]")
# Note: adjust pattern above to match the committed key
```

Alternative: use BFG Repo-Cleaner:

```bash
# Create a file containing the secret or pattern to remove (secrets.txt)
# secrets.txt content example:
# sk-REDACTED_REPLACE_WITH_YOUR_KEY

java -jar bfg.jar --delete-files secrets.txt
# then follow BFG instructions (git reflog expire, git gc)
```

4) Force-push rewritten history to remote:

```bash
git push --force --all
git push --force --tags
```

5) Ask all collaborators to re-clone the repository (recommended) or follow the BFG recovery steps.

6) Update CI / secret stores to use the rotated key and verify CI runs.

7) Add a pre-commit check to prevent accidental commits of API keys. The repo now ships two guards:
   - `.pre-commit-config.yaml` — `gitleaks` (preferred). Enable with:
     ```bash
     pip install pre-commit
     pre-commit install
     ```
   - `.githooks/pre-commit` — dependency-free fallback scanning staged diff for `sk-…`/`apiKey`/private keys. Enable with:
     ```bash
     git config core.hooksPath .githooks
     ```
   Either will block a commit that introduces an obvious secret; use `git commit --no-verify` only for deliberate, reviewed exceptions.

If you want, I can prepare a ready-to-run `git-filter-repo` script tailored to the exact key we found and optionally open a PR with the `DevOps/SCRUB_DEEPSEEK_KEY.md` file. Let me know whether to proceed with automated scrub (I will not force-push without explicit approval).