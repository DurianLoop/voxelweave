param(
    [Parameter(Mandatory=$true)]
    [ValidateSet('control','geometry','correspondence','frequency','risk','context')]
    [string]$Variant,
    [ValidateSet(3407,2027,9103)][int]$Seed=3407,
    [string]$Gate='',
    [switch]$Resume
)
$ErrorActionPreference='Stop'
Set-Location D:\MRI
$py='D:\conda\envs\MRI\python.exe'
$env:PYTHONPATH='D:\MRI\design;D:\MRI'
$out="design\pastnet_v2\runs\full_${Variant}_seed${Seed}_vram20"
$arguments=@('-B','-m','pastnet_v2.run','train','--variant',$Variant,'--seed',"$Seed",'--out',$out)
if($Gate){$arguments+=@('--gate',$Gate)}
if($Resume){$arguments+='--resume'}
& $py @arguments
if($LASTEXITCODE -ne 0){throw 'Training failed; do not continue to evaluation.'}
if(-not (Test-Path -LiteralPath "$out\efficiency.json")){
    & $py -B -m pastnet_v2.efficiency --variant $Variant --checkpoint "$out\best.pth" --out "$out\efficiency.json"
    if($LASTEXITCODE -ne 0){throw 'Efficiency measurement failed.'}
}
