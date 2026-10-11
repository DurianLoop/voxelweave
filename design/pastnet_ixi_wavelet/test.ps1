param([ValidateSet(3407,2027,9103)][int]$Seed=3407)
$ErrorActionPreference='Stop'
Set-Location (Resolve-Path (Join-Path $PSScriptRoot '..\..'))
$env:PYTHONPATH="$(Get-Location)\design;$(Get-Location)"
& D:\conda\envs\MRI\python.exe -B -m pastnet_ixi_wavelet.test --run (Join-Path $PSScriptRoot "runs\full_wavelet3_ixi_seed$Seed") --out (Join-Path $PSScriptRoot "results\test115_seed$Seed")
if($LASTEXITCODE -ne 0){throw 'Frozen IXI evaluation failed'}
