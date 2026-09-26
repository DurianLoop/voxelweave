param([switch]$Preflight)
$ErrorActionPreference='Stop'
Set-Location (Resolve-Path (Join-Path $PSScriptRoot '..\..'))
$env:PYTHONPATH="$(Get-Location)\design;$(Get-Location)"
$python='D:\conda\envs\MRI\python.exe'
$arguments=@('-B','-m','i3net_amp_recovery.run')
if($Preflight){$arguments+='--preflight'}
$logs=Join-Path $PSScriptRoot 'logs'
New-Item -ItemType Directory -Force $logs | Out-Null
$log=Join-Path $logs ("resume_"+(Get-Date -Format 'yyyyMMdd_HHmmss')+'.txt')
Start-Transcript -Path $log | Out-Null
try {
    & $python @arguments
    if($LASTEXITCODE -ne 0){throw "Resume failed: $LASTEXITCODE. Terminal log: $log"}
    if($Preflight){return}
    $run='D:\MRI\design\i3net_repaired_reference\runs\full_i3net_repaired_seed3407_vram20'
    if(-not (Test-Path (Join-Path $run 'efficiency.json'))){
        & $python -B -m i3net_repaired_reference.efficiency --checkpoint (Join-Path $run 'best.pth') --out (Join-Path $run 'efficiency.json')
        if($LASTEXITCODE -ne 0){throw 'Efficiency failed'}
    }
    Write-Host 'Completed. AMP skip counts are recorded under run/recovery_audit.'
} finally { Stop-Transcript | Out-Null }
