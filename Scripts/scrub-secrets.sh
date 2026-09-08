#!/usr/bin/env bash
# History scrub for leaked DeepSeek keys using git-filter-repo.
#
# WARNING: rewrites history and requires a coordinated FORCE-PUSH. Run only
# after rotating the keys at the DeepSeek console and with team sign-off.
#
# Usage (from repo root D:/CRM):
#   SECRET1='sk-<old-key-1>' SECRET2='sk-<old-key-2>' bash Scripts/scrub-secrets.sh
#
# It never embeds keys in the file; pass them via env vars. The keys identified
# in this repo's history/working tree were:
#   - sk-f484a1d7...  (committed in 5b643ca, removed in 9ac9fd3)  -> already pushed
#   - sk-0a1d51c8...  (uncommitted working tree only; rotate defensively)
# Replace them with the exact full values you want scrubbed.

set -euo pipefail

REPO_ROOT="$(cd "$(dirname "$0")/.." && pwd)"
cd "$REPO_ROOT"

: "${SECRET1:=}"
: "${SECRET2:=}"

if [[ -z "$SECRET1" && -z "$SECRET2" ]]; then
  echo "No secrets provided. Set SECRET1 / SECRET2 env vars." >&2
  exit 1
fi

# 1) Safety backup
BACKUP="${REPO_ROOT%/}-crm-repo-backup.git"
if [[ ! -d "$BACKUP" ]]; then
  echo "Creating mirror backup at $BACKUP ..."
  git clone --mirror . "$BACKUP"
else
  echo "Backup already exists at $BACKUP (skipping)."
fi

# 2) Prepare replacement rules (avoid leaking to shell history by using a temp file)
TMP_RULES="$(mktemp)"
trap 'rm -f "$TMP_RULES"' EXIT
[[ -n "$SECRET1" ]] && printf '%s==>[REDACTED]\n' "$SECRET1" >>"$TMP_RULES"
[[ -n "$SECRET2" ]] && printf '%s==>[REDACTED]\n' "$SECRET2" >>"$TMP_RULES"
echo "Replacement rules prepared ($(wc -l <"$TMP_RULES") rule(s))."

# 3) Rewrite history (requires git-filter-repo)
echo "Running git filter-repo ..."
git filter-repo --replace-text "$TMP_RULES"

# 4) Force push (coordinate with team first!)
echo ""
echo "History rewritten. Now review, then force push:"
echo "  git push --force --all"
echo "  git push --force --tags"
echo "Then have all collaborators re-clone."
