param([ValidateSet(3407,2027,9103)][int]$Seed=3407,[switch]$Resume,[switch]$Preflight)
$ErrorActionPreference='Stop'
Set-Location (Resolve-Path (Join-Path $PSScriptRoot '..\..'))
$env:PYTHONPATH="$(Get-Location)\design;$(Get-Location)"
$argsTrain=@('-B','-m','pastnet_ixi_wavelet.run','--seed',"$Seed",'--out',(Join-Path $PSScriptRoot "runs\full_wavelet3_ixi_seed$Seed"))
if($Resume){$argsTrain+='--resume'}
if($Preflight){$argsTrain+='--preflight'}
New-Item -ItemType Directory -Force (Join-Path $PSScriptRoot 'logs') | Out-Null
Start-Transcript -Path (Join-Path $PSScriptRoot ('logs\train_'+(Get-Date -Format 'yyyyMMdd_HHmmss')+'.txt')) | Out-Null
try {
    & D:\conda\envs\MRI\python.exe @argsTrain
    if($LASTEXITCODE -ne 0){throw 'IXI training failed; read transcript and resume same run.'}
} finally { Stop-Transcript | Out-Null }
