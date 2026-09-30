$ErrorActionPreference='Stop'
Set-Location $PSScriptRoot

function Fail($m){ Write-Host "FAIL: $m" -ForegroundColor Red; exit 1 }
function Pass($m){ Write-Host "PASS: $m" -ForegroundColor Green }

Write-Host '=== PF-011 CORE IMPLEMENTATION GATE ==='

$head = git rev-parse HEAD
$origin = git rev-parse origin/master
if($head -ne $origin){ Fail "HEAD != origin/master: $head / $origin" }
$status = @(git status --porcelain | Where-Object { $_ -notmatch '^\?\? pf011_core_implementation_gate\.ps1$' }); if($status.Count -gt 0){ Fail ('Working tree has pre-existing changes: ' + ($status -join ' | ')) }
Pass "Clean baseline: $head"

$required = @(
 'Documentation\00_Project_Constitution.md',
 'Documentation\01-BFS-Platform-Foundation\ELU-BFS-PF-Platform-Foundation.md',
 'Documentation\11-Engineering\ELU-DDD-PF.md',
 'Documentation\11-Engineering\ELU-ERD-PF.md',
 'Documentation\11-Engineering\ELU-API-PF.md',
 'Documentation\11-Engineering\ELU-UI-PF.md',
 'Documentation\11-Engineering\ELU-TST-PF.md'
)
foreach($f in $required){
    if(!(Test-Path $f)){ Fail "Missing authoritative file: $f" }
}
Pass 'Authoritative specification files present'

$bfs = Get-Content 'Documentation\01-BFS-Platform-Foundation\ELU-BFS-PF-Platform-Foundation.md' -Raw
$ddd = Get-Content 'Documentation\11-Engineering\ELU-DDD-PF.md' -Raw

foreach($x in @(
 'BR-PF-077','BR-PF-078','BR-PF-079','BR-PF-080',
 'BR-PF-081','BR-PF-082','BR-PF-083','BR-PF-084',
 'AC-PF-011-01','AC-PF-011-02','AC-PF-011-03',
 'AC-PF-011-04','AC-PF-011-05','AC-PF-011-06'
)){
    if($bfs -notmatch [regex]::Escape($x)){ Fail "Missing BFS requirement: $x" }
}
Pass 'PF-011 BFS rules and acceptance criteria present'

foreach($x in @(
 'platform_setting | id, key UK, value, description',
 'setting_catalogue | id, setting_key UK, value_type, default_value, description',
 'tenant_preference | tenant_id, setting_key, setting_value',
 'tenant_notification_preference | tenant_id, event_code, channel, is_enabled',
 'tenant_module_default | tenant_id, module_domain, defaults_json',
 'tenant_holiday_calendar | tenant_id, holiday_date, name, is_working_day'
)){
    if($ddd -notmatch [regex]::Escape($x)){ Fail "DDD schema missing: $x" }
}
Pass 'DDD-authoritative PF-011 six-table schema present'

$entities = Get-Content 'Backend\app\models\pf\entities.py' -Raw
if($entities -notmatch 'class TenantSettings'){ Fail 'Existing TenantSettings ORM entity not found' }
if($entities -match 'class\s+TenantPreference'){ Fail 'PF-011 implementation already exists unexpectedly' }
Pass 'Existing tenant_settings detected; duplicate PF-011 tenant_settings prohibited'

$redis = Get-Content 'Backend\app\utils\redis_rate_limiter.py' -Raw
if($redis -notmatch 'get_redis_client'){ Fail 'Existing Redis client not found' }
Pass 'Existing Redis client available'

foreach($f in @(
 'Backend\app\utils\redis_rate_limiter.py',
 'Backend\app\models\pf\entities.py',
 'Backend\app\db\seed.py',
 'Backend\app\db\migrate_pf003a.py',
 'Backend\app\db\migrations\012_rls_pf003a.sql',
 'Backend\app\main.py'
)){
    if(Test-Path $f){
        $s = git status --porcelain -- $f
        if($s){ Fail "Protected baseline file modified: $f" }
    }
}
Pass 'Protected baseline files unchanged'

if(Test-Path 'Backend\app\db\migrations\020_settings_pf011.sql'){ Fail 'PF-011 migration already exists before implementation gate' }
if(Test-Path 'Backend\app\db\migrate_pf011.py'){ Fail 'PF-011 migration runner already exists before implementation gate' }
if(Test-Path 'Backend\app\services\pf\settings_service.py'){ Fail 'PF-011 settings service already exists before implementation gate' }
if(Test-Path 'Backend\app\api\v1\pf\settings.py'){ Fail 'PF-011 settings API already exists before implementation gate' }
Pass 'No PF-011 implementation artifacts present'

Write-Host ''
Write-Host '=== APPROVED PF-011 CONTRACT ==='
Write-Host 'LOCK: tenant_preference.is_editable=false => Platform Admin only'
Write-Host 'CACHE: existing Redis client; tenant-scoped key; TTL=300 seconds'
Write-Host 'CACHE: invalidate on successful write; DB fallback on Redis failure'
Write-Host 'AUDIT: existing write_audit_event(); before/after snapshots'
Write-Host 'EDITION: existing edition_feature/feature_catalogue mechanism'
Write-Host 'SCOPE: extend existing tenant_settings; add six DDD-authoritative tables'
Write-Host ''
Write-Host '=== GATE RESULT ==='
Pass 'PF-011 implementation preflight PASS'
Write-Host 'NO COMMIT'
Write-Host 'NO PUSH'
