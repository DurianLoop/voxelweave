param([ValidateSet('pair','blind','latent')][string]$Variant='pair',[ValidateSet(3407,2027,9103)][int]$Seed=3407,[switch]$Preflight)
$ErrorActionPreference='Stop'
$runArgs=@('-B','-u',(Join-Path $PSScriptRoot 'launch.py'),'--variant',$Variant,'--seed',"$Seed")
if($Preflight){$runArgs+='--preflight'}
& D:\conda\envs\MRI\python.exe @runArgs
if($LASTEXITCODE -ne 0){throw 'Startup/training failed; read the complete stdout_stderr log in ixi_latent_bridge/logs.'}
