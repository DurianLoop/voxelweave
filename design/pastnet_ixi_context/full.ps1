param([ValidateSet('pair','local','extended')][string]$Variant='pair',[ValidateSet(3407,2027,9103)][int]$Seed=3407,[switch]$Resume,[switch]$Preflight)
$ErrorActionPreference='Stop'
Set-Location (Resolve-Path (Join-Path $PSScriptRoot '..\..'))
$env:PYTHONPATH="$(Get-Location)\design;$(Get-Location)"
$variants=if($Variant -eq 'pair'){@('local','extended')}else{@($Variant)}
New-Item -ItemType Directory -Force (Join-Path $PSScriptRoot 'logs') | Out-Null
Start-Transcript -Path (Join-Path $PSScriptRoot ('logs\'+$Variant+'_'+(Get-Date -Format 'yyyyMMdd_HHmmss')+'.txt')) | Out-Null
try {
    foreach($arm in $variants){
        $trainArgs=@('-B','-m','pastnet_ixi_context.run','--variant',$arm,'--seed',"$Seed",'--out',(Join-Path $PSScriptRoot "runs\full_${arm}_seed$Seed"))
        if($Resume){$trainArgs+='--resume'}
        if($Preflight){$trainArgs+='--preflight'}
        # Pair resume may reach an arm that has not started yet.
        if($Resume -and -not (Test-Path (Join-Path $PSScriptRoot "runs\full_${arm}_seed$Seed\manifest.json"))){$trainArgs=$trainArgs | Where-Object {$_ -ne '--resume'}}
        & D:\conda\envs\MRI\python.exe @trainArgs
        if($LASTEXITCODE -ne 0){throw "IXI STC $arm failed; preserve files and resume."}
    }
    if($Variant -eq 'pair' -and -not $Preflight){
        & D:\conda\envs\MRI\python.exe -B -m pastnet_ixi_context.report --seed $Seed
        if($LASTEXITCODE -ne 0){throw 'Validation report failed'}
    }
} finally {Stop-Transcript | Out-Null}
