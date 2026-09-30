Set-Location 'D:\CRM'
$ErrorActionPreference='Stop'
$p='Documentation\ADR-017-PF011-Specification-Reconciliation.md'
$before=(Get-Content $p -Raw)
if($before -notmatch '\| Final Decision \| Proposed: reconcile PF-011 through the governed specification chain before implementation\.'){throw 'FAIL: expected Final Decision text not found'}
if((git status --short) -notmatch '^\?\? pf011_'){throw 'FAIL: unexpected worktree state'}
$after=$before -replace '\| Final Decision \| Proposed: reconcile PF-011','| Final Decision | Reconcile PF-011'
[IO.File]::WriteAllText((Resolve-Path $p),$after,(New-Object Text.UTF8Encoding($false)))
$diff=(git diff -- $p)
if($diff -notmatch '^-.*Final Decision \| Proposed: reconcile PF-011'){throw 'FAIL: expected deletion missing'}
if($diff -notmatch '^\+.*Final Decision \| Reconcile PF-011'){throw 'FAIL: expected addition missing'}
if(($diff -split "`n" | Where-Object {$_ -match '^[+-]' -and $_ -notmatch '^(---|\+\+\+)'}).Count -ne 2){throw 'FAIL: unexpected diff size'}
git diff --check -- $p
git add -- $p
git diff --cached --check
$cached=(git diff --cached -- $p)
if(($cached -split "`n" | Where-Object {$_ -match '^[+-]' -and $_ -notmatch '^(---|\+\+\+)'}).Count -ne 2){throw 'FAIL: staged diff is not exact'}
git commit -m 'docs(pf011): correct accepted ADR-017 decision wording'
if($LASTEXITCODE -ne 0){throw 'FAIL: commit failed'}
Write-Host 'PASS: ADR-017 correction committed'
Write-Host 'NO PUSH'
