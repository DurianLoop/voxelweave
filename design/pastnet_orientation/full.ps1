param([ValidateSet(3407,2027,9103)][int]$Seed=3407,[switch]$Resume,[switch]$Preflight)
$ErrorActionPreference='Stop'
Set-Location (Resolve-Path (Join-Path $PSScriptRoot '..\..'))
$env:PYTHONPATH="$(Get-Location)\design;$(Get-Location)"
$python='D:\conda\envs\MRI\python.exe'
$run=Join-Path $PSScriptRoot "runs\full_orientation_seed${Seed}_vram20"
$trainArgs=@('-B','-m','pastnet_orientation.run','train','--variant','orientation','--seed',"$Seed",'--out',$run,'--micro-batch-size','2','--checkpoint-blocks','5')
if($Resume){$trainArgs+='--resume'}
if($Preflight){$trainArgs+='--preflight'}
& $python @trainArgs
if($LASTEXITCODE -ne 0){throw "Training failed: $LASTEXITCODE"}
if($Preflight){return}
if(-not (Test-Path (Join-Path $run 'efficiency.json'))){
    & $python -B -m pastnet_orientation.efficiency --variant orientation --checkpoint (Join-Path $run 'best.pth') --out (Join-Path $run 'efficiency.json')
    if($LASTEXITCODE -ne 0){throw 'Efficiency failed'}
}
Write-Host 'Completed. Validation gate review is required before additional seeds.'
