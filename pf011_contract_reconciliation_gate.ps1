Set-Location 'D:\CRM'
$ErrorActionPreference='Stop'

$baseline=(git rev-parse origin/master).Trim()
$head=(git rev-parse HEAD).Trim()
git merge-base --is-ancestor $baseline $head
if($LASTEXITCODE -ne 0){throw 'FAIL: protected baseline is not an ancestor'}

$files=@(
'Documentation\10-EFS-V1-Ready\ELU-RTM-001-Master-Requirements-Index.md',
'Documentation\11-Engineering\ELU-DDD-PF.md',
'Documentation\11-Engineering\ELU-ERD-PF.md',
'Documentation\11-Engineering\ELU-API-PF.md',
'Documentation\11-Engineering\ELU-UI-PF.md',
'Documentation\11-Engineering\ELU-TST-PF.md'
)

foreach($f in $files){if(!(Test-Path $f)){throw "FAIL: missing $f"}}

foreach($f in @(
'Backend\app\db\migrate_pf011.py',
'Database\03_PlatformFoundation\020_settings_pf011.sql'
)){if(Test-Path $f){throw "FAIL: implementation artifact exists: $f"}}

$checks=@{
$files[0]=@('1.9','PF-011 System Configuration','BR-PF-077','BR-PF-084','tenant_settings','platform_setting','setting_catalogue')
$files[1]=@('1.1','PF-011','tenant_settings','tenant_preference','tenant_notification_preference','tenant_module_default','tenant_holiday_calendar','platform_setting','setting_catalogue')
$files[2]=@('1.1','PF-011','tenant_settings','tenant_preference','tenant_notification_preference','tenant_module_default','tenant_holiday_calendar','platform_setting','setting_catalogue')
$files[3]=@('1.4','PF-011','/api/v1/settings','/api/v1/settings/preferences','/api/v1/settings/notifications','/api/v1/settings/module-defaults','/api/v1/settings/holidays','/api/v1/settings/reset','/api/v1/settings/catalogue','/api/v1/platform/settings','settings.read','settings.configure','platform_settings.read','platform_settings.configure','If-Match')
$files[4]=@('1.2','PF-011','/settings/preferences','/settings/notifications','/settings/module-defaults','/settings/holidays','/settings/catalogue','/platform/settings','is_editable=false','300-second')
$files[5]=@('1.6','PF-011','TC-PF-011-01','TC-PF-011-24','AC-PF-011-01','AC-PF-011-06','BR-PF-077','BR-PF-084')
}

foreach($f in $files){
  $raw=[IO.File]::ReadAllText($f,[Text.Encoding]::UTF8)
  foreach($n in $checks[$f]){
    if($raw.IndexOf($n,[StringComparison]::OrdinalIgnoreCase) -lt 0){throw "FAIL: $f missing [$n]"}
  }
}

$s=git status --short --untracked-files=all
$e=@(
' M Documentation/10-EFS-V1-Ready/ELU-RTM-001-Master-Requirements-Index.md',
' M Documentation/11-Engineering/ELU-API-PF.md',
' M Documentation/11-Engineering/ELU-DDD-PF.md',
' M Documentation/11-Engineering/ELU-ERD-PF.md',
' M Documentation/11-Engineering/ELU-TST-PF.md',
' M Documentation/11-Engineering/ELU-UI-PF.md',
'?? pf011_adr017_correction_gate.ps1',
'?? pf011_contract_reconciliation_author_gate.ps1',
'?? pf011_contract_reconciliation_gate.ps1',
'?? pf011_core_implementation_gate.ps1'
)
if(($s -join [Environment]::NewLine) -ne ($e -join [Environment]::NewLine)){throw 'FAIL: unexpected worktree'}

Write-Host 'PASS: PF-011 downstream contracts reconciled and verified'
Write-Host 'STATUS: READY FOR HUMAN APPROVAL BEFORE IMPLEMENTATION'
Write-Host 'NO IMPLEMENTATION / NO MIGRATION / NO COMMIT / NO PUSH'
