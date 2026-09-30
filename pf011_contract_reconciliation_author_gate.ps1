Set-Location 'D:\CRM'
$ErrorActionPreference='Stop'

$baseline=(git rev-parse origin/master).Trim()
$head=(git rev-parse HEAD).Trim()

git merge-base --is-ancestor $baseline $head; if($LASTEXITCODE -ne 0){throw 'FAIL: protected baseline is not an ancestor'}

$files=@(
'Documentation\11-Engineering\ELU-DDD-PF.md',
'Documentation\11-Engineering\ELU-ERD-PF.md',
'Documentation\11-Engineering\ELU-API-PF.md',
'Documentation\11-Engineering\ELU-UI-PF.md',
'Documentation\11-Engineering\ELU-TST-PF.md'
)

foreach($p in $files){if(!(Test-Path $p)){throw "FAIL: missing $p"}}

foreach($p in @(
'Backend\app\db\migrate_pf011.py',
'Database\03_PlatformFoundation\020_settings_pf011.sql'
)){if(Test-Path $p){throw "FAIL: implementation artifact exists: $p"}}

$checks=@{
'Documentation\11-Engineering\ELU-DDD-PF.md'=@(
'PF-011','tenant_settings','tenant_preference','tenant_notification_preference',
'tenant_module_default','tenant_holiday_calendar','platform_setting','setting_catalogue'
)
'Documentation\11-Engineering\ELU-ERD-PF.md'=@(
'PF-011','tenant_settings','tenant_preference','tenant_notification_preference',
'tenant_module_default','tenant_holiday_calendar','platform_setting','setting_catalogue'
)
'Documentation\11-Engineering\ELU-API-PF.md'=@(
'PF-011','/api/v1/settings','/api/v1/settings/preferences',
'/api/v1/settings/notifications','/api/v1/settings/module-defaults',
'/api/v1/settings/holidays','/api/v1/settings/reset',
'/api/v1/settings/catalogue','/api/v1/platform/settings'
)
'Documentation\11-Engineering\ELU-UI-PF.md'=@(
'PF-011','/settings'
)
'Documentation\11-Engineering\ELU-TST-PF.md'=@(
'PF-011','AC-PF-011-01','AC-PF-011-02','AC-PF-011-03',
'AC-PF-011-04','AC-PF-011-05','AC-PF-011-06'
)
}

foreach($p in $checks.Keys){
  $raw=Get-Content $p -Raw
  foreach($needle in $checks[$p]){
    if($raw.IndexOf($needle,[System.StringComparison]::OrdinalIgnoreCase) -lt 0){
      Write-Host "BLOCK: $p missing [$needle]"
    }
  }
}

Write-Host 'PASS: reconciliation gate authored'
Write-Host 'STATUS: downstream contracts still require governed reconciliation'
Write-Host 'NO IMPLEMENTATION / NO MIGRATION / NO COMMIT / NO PUSH'
