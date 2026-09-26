param([ValidateSet('crossview','per_anchor')][string]$Variant='crossview',
      [ValidateSet(3407,2027,9103)][int]$Seed=3407,[switch]$Resume)
$ErrorActionPreference='Stop'
Set-Location (Resolve-Path (Join-Path $PSScriptRoot '..\..'))
$env:PYTHONPATH="$(Get-Location)\design;$(Get-Location)"
$python='D:\conda\envs\MRI\python.exe'
$run=Join-Path $PSScriptRoot "runs\full_${Variant}_seed${Seed}_vram20"
$trainArgs=@('-B','-m','pastnet_v2_crossview.run','train','--variant',$Variant,'--seed',"$Seed",'--out',$run,'--micro-batch-size','2','--checkpoint-blocks','6')
if($Resume){$trainArgs+='--resume'}
& $python @trainArgs
if($LASTEXITCODE -ne 0){throw "Training failed: $LASTEXITCODE"}
if(-not (Test-Path (Join-Path $run 'efficiency.json'))){
    & $python -B -m pastnet_v2_crossview.efficiency --variant $Variant --checkpoint (Join-Path $run 'best.pth') --out (Join-Path $run 'efficiency.json')
    if($LASTEXITCODE -ne 0){throw 'Efficiency failed'}
}
Write-Host "Completed $Variant seed $Seed; review validation before another full."
