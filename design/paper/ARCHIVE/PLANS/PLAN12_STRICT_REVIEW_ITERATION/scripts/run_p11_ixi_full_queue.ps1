param(
    [ValidateSet('hat', 'swinir', 'i3net', 'saint', 'cycleinr')]
    [string[]]$Models = @('hat', 'swinir', 'i3net', 'saint', 'cycleinr'),
    [int]$Bootstrap = 5000,
    [int]$TargetsPerCase = 5,
    [string]$Suffix = 'full'
)

$ErrorActionPreference = 'Stop'
$workspace = 'D:\MRI'
$python = 'D:\conda\envs\MRI\python.exe'
$replication = Join-Path $workspace 'design\paper\PLAN11_CLAIM_STRENGTHENING\scripts\p11_ixi_five_arch_clean.py'
$identity = Join-Path $workspace 'design\paper\PLAN11_CLAIM_STRENGTHENING\scripts\p11_matched_geometry_identity.py'

Set-Location -LiteralPath $workspace

Write-Output ("QUEUE_START {0:o}" -f (Get-Date))
Write-Output ("MODELS {0}" -f ($Models -join ','))

foreach ($model in $Models) {
    Write-Output ("MODEL_START model={0} time={1:o}" -f $model, (Get-Date))
    & $python -B $replication `
        --models $model `
        --targets-per-case $TargetsPerCase `
        --bootstrap $Bootstrap `
        --device cuda `
        --suffix $Suffix `
        --resume
    if ($LASTEXITCODE -ne 0) {
        throw "P11-E02 failed for model=$model with exit code $LASTEXITCODE"
    }
    Write-Output ("MODEL_DONE model={0} time={1:o}" -f $model, (Get-Date))
}

Write-Output ("IDENTITY_START {0:o}" -f (Get-Date))
& $python -B $identity `
    --input-suffix $Suffix `
    --output-suffix $Suffix `
    --bootstrap $Bootstrap
if ($LASTEXITCODE -ne 0) {
    throw "P11-E03 failed with exit code $LASTEXITCODE"
}

Write-Output ("QUEUE_DONE {0:o}" -f (Get-Date))
