param([ValidateSet(3407,2027,9103)][int]$Seed=3407,[switch]$Resume)
$ErrorActionPreference='Stop'
Set-Location (Resolve-Path (Join-Path $PSScriptRoot '..\..'))
$env:PYTHONPATH="$(Get-Location)\design;$(Get-Location)"
$python='D:\conda\envs\MRI\python.exe'
$run=Join-Path $PSScriptRoot "runs\full_soft_tail_seed${Seed}_vram20"
$trainArgs=@('-B','-m','pastnet_softtail.run','train','--variant','soft_tail','--seed',"$Seed",'--out',$run,'--micro-batch-size','2','--checkpoint-blocks','5')
if($Resume){$trainArgs+='--resume'}
& $python @trainArgs
if($LASTEXITCODE -ne 0){throw "Training failed: $LASTEXITCODE"}
if(-not (Test-Path (Join-Path $run 'efficiency.json'))){
    & $python -B -m pastnet_softtail.efficiency --variant soft_tail --checkpoint (Join-Path $run 'best.pth') --out (Join-Path $run 'efficiency.json')
    if($LASTEXITCODE -ne 0){throw 'Efficiency failed'}
}
Write-Host 'Completed. Review validation gate before additional seeds.'
