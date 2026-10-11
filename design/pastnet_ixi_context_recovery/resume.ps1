param([ValidateSet('pair','local','extended')][string]$Variant='pair',[ValidateSet(3407,2027,9103)][int]$Seed=3407,[switch]$Preflight,[switch]$LogProbe)
$ErrorActionPreference='Stop'
Set-Location (Resolve-Path (Join-Path $PSScriptRoot '..\..'))
$env:PYTHONPATH="$(Get-Location)\design;$(Get-Location)"
$runArgs=@('-B','-u',(Join-Path $PSScriptRoot 'bootstrap.py'),'--variant',$Variant,'--seed',"$Seed")
if($Preflight){$runArgs+='--preflight'}
if($LogProbe){$runArgs+='--log-probe'}
& D:\conda\envs\MRI\python.exe @runArgs
if($LASTEXITCODE -ne 0){throw 'Startup or training failed; complete Python traceback is saved under pastnet_ixi_context_recovery/startup_logs.'}
