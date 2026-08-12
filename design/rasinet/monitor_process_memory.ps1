param(
    [Parameter(Mandatory = $true)][int]$ProcessId,
    [Parameter(Mandatory = $true)][string]$OutputDirectory,
    [int]$IntervalSeconds = 2
)

$ErrorActionPreference = 'Stop'
New-Item -ItemType Directory -Force -Path $OutputDirectory | Out-Null
$rows = [System.Collections.Generic.List[object]]::new()

while ($true) {
    $process = Get-Process -Id $ProcessId -ErrorAction SilentlyContinue
    if ($null -eq $process) {
        break
    }
    $rows.Add([pscustomobject]@{
        timestamp = (Get-Date).ToString('o')
        process_id = $ProcessId
        working_set_bytes = [int64]$process.WorkingSet64
        private_memory_bytes = [int64]$process.PrivateMemorySize64
        cpu_seconds = [double]$process.CPU
    })
    Start-Sleep -Seconds $IntervalSeconds
}

$csvPath = Join-Path $OutputDirectory 'process_memory.csv'
$rows | Export-Csv -NoTypeInformation -Encoding UTF8 -Path $csvPath
if ($rows.Count -gt 0) {
    $summary = [ordered]@{
        process_id = $ProcessId
        samples = $rows.Count
        interval_seconds = $IntervalSeconds
        peak_working_set_bytes = [int64](($rows | Measure-Object working_set_bytes -Maximum).Maximum)
        peak_private_memory_bytes = [int64](($rows | Measure-Object private_memory_bytes -Maximum).Maximum)
    }
    $summary | ConvertTo-Json | Set-Content -Encoding UTF8 -Path (Join-Path $OutputDirectory 'process_memory_summary.json')
}
