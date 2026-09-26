param([ValidateSet(3407,2027,9103)][int]$Seed=3407,[switch]$Resume)
$ErrorActionPreference='Stop'
Set-Location D:\MRI
$py='D:\conda\envs\MRI\python.exe'
$env:PYTHONPATH='D:\MRI\design;D:\MRI'
$out="design\pastnet_v2_independent\runs\full_correspondence_only_seed${Seed}_vram20"
$arguments=@('-B','-m','pastnet_v2_independent.run','train','--variant','correspondence_only',
    '--seed',"$Seed",'--out',$out,'--micro-batch-size','2','--checkpoint-blocks','10')
if($Resume){$arguments+='--resume'}
& $py @arguments
if($LASTEXITCODE -ne 0){throw 'Independent full failed.'}
if(-not (Test-Path -LiteralPath "$out\efficiency.json")){
    & $py -B -m pastnet_v2_independent.efficiency --variant correspondence_only --checkpoint "$out\best.pth" --out "$out\efficiency.json"
    if($LASTEXITCODE -ne 0){throw 'Efficiency measurement failed.'}
}
