param([Parameter(Mandatory=$true)][string]$Name,[Parameter(Mandatory=$true)][string]$Script,[string[]]$ScriptArgs=@())
$ErrorActionPreference='Stop'
$auditPython='C:\Users\11638\AppData\Local\AQRP\runtime\Python31316\python.exe'
$auditOut=$PSScriptRoot
$record=[ordered]@{start=(Get-Date).ToString('o');cwd=(Get-Location).Path;executable=$auditPython;args=@('-I',$Script)+$ScriptArgs}
& $auditPython -I $Script @ScriptArgs 1> (Join-Path $auditOut "$Name.stdout.log") 2> (Join-Path $auditOut "$Name.stderr.log")
$record.exit_code=$LASTEXITCODE
$record.end=(Get-Date).ToString('o')
$record | ConvertTo-Json -Depth 6 | Set-Content -LiteralPath (Join-Path $auditOut "$Name.command.json") -Encoding utf8
Get-Content -LiteralPath (Join-Path $auditOut "$Name.stdout.log")
if($record.exit_code -ne 0){ Get-Content -LiteralPath (Join-Path $auditOut "$Name.stderr.log"); exit $record.exit_code }

