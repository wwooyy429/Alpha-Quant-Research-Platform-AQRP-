$ErrorActionPreference='Stop'
$browserRecord=Get-Content -LiteralPath 'C:/Users/11638/AppData/Local/AQRP/reviews/p6-g2-recheck-3017a09-independent-20261024/BROWSER_START.json' -Raw | ConvertFrom-Json
$ownedInterpreter=$browserRecord.argv[0]
$ownedPort=$browserRecord.argv[-1]
$ownedProcesses=@(Get-CimInstance Win32_Process | Where-Object {
 $_.CommandLine -and $_.CommandLine.Contains($ownedInterpreter) -and (
 ($_.CommandLine.Contains('-m aqrp.ui.launch') -and $_.CommandLine.Contains($browserRecord.workspace)) -or
 ($_.CommandLine.Contains('-m streamlit run') -and $_.CommandLine.Contains('--server.port='+$ownedPort) -and $_.CommandLine.Contains('--server.address=127.0.0.1')))
})
if ($ownedProcesses.Count -lt 1) {throw 'No own UI process identified'}
$ownedProcesses | Select-Object ProcessId,ParentProcessId,CommandLine,CreationDate | ConvertTo-Json -Depth 5 | Set-Content -LiteralPath 'C:/Users/11638/AppData/Local/AQRP/reviews/p6-g2-recheck-3017a09-independent-20261024/BROWSER_PROCESS_IDENTITY.json' -Encoding utf8
$ownedIds=@($ownedProcesses.ProcessId)
$orderedIds=@()
while ($orderedIds.Count -lt $ownedIds.Count) {
 $leaves=@($ownedProcesses | Where-Object { $orderedIds -notcontains $_.ProcessId -and @($ownedProcesses | Where-Object { $orderedIds -notcontains $_.ProcessId }).ParentProcessId -notcontains $_.ProcessId })
 if ($leaves.Count -eq 0) {throw 'Unexpected own process cycle'}
 foreach ($leaf in $leaves) {$orderedIds+= $leaf.ProcessId}
}
foreach ($ownedId in $orderedIds) {
 $live=Get-CimInstance Win32_Process -Filter "ProcessId=$ownedId"
 if ($live) {
  if (-not $live.CommandLine.Contains($ownedInterpreter)) {throw 'Process identity changed'}
  Stop-Process -Id $ownedId -ErrorAction Stop
 }
}
$remaining=@(Get-CimInstance Win32_Process | Where-Object { $ownedIds -contains $_.ProcessId })
if ($remaining.Count -ne 0) {throw 'Own process remains'}
$connection=New-Object System.Net.Sockets.TcpClient
try {$connection.Connect('127.0.0.1',[int]$ownedPort);throw 'Own port still listening'}
catch [System.Net.Sockets.SocketException] {$refused=$true}
finally {$connection.Dispose()}
[ordered]@{stopped_owned_process_ids=$orderedIds;remaining=0;port_refused=$refused;utc=(Get-Date).ToUniversalTime().ToString('o');scope='Own temporary loopback synthetic engineering UI only'} | ConvertTo-Json | Set-Content -LiteralPath 'C:/Users/11638/AppData/Local/AQRP/reviews/p6-g2-recheck-3017a09-independent-20261024/BROWSER_STOP.json' -Encoding utf8
Write-Output 'Own loopback UI stopped and port refused'
