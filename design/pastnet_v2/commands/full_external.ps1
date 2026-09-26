param(
    [Parameter(Mandatory=$true)][ValidateSet('ixi','ningxia')][string]$Dataset,
    [string]$Lock='design\pastnet_v2\results\candidate_lock.json'
)
$ErrorActionPreference='Stop'
Set-Location D:\MRI
$py='D:\conda\envs\MRI\python.exe'
$env:PYTHONPATH='D:\MRI\design;D:\MRI'
$locked=Get-Content -LiteralPath $Lock -Raw -Encoding UTF8 | ConvertFrom-Json
$variant=$locked.variant
$folds=if($Dataset -eq 'ningxia'){0..7}else{@(0)}
$candidateOutputs=@()
$controlOutputs=@()
foreach($fold in $folds){
    $foldName='fold_{0:D2}' -f $fold
    $manifest="design\pastnet_v2\manifests\$Dataset\$foldName.json"
    if(-not (Test-Path -LiteralPath $manifest)){
        & $py -B -m pastnet_v2.prepare --dataset $Dataset --fold $fold
        if($LASTEXITCODE -ne 0){throw 'Manifest preparation failed.'}
    }
    foreach($seed in @(3407,2027,9103)){
        foreach($model in @('control',$variant)){
            $out="design\pastnet_v2\runs\${Dataset}_${foldName}_${model}_seed${seed}"
            $arguments=@('-B','-m','pastnet_v2.run','train','--manifest',$manifest,'--variant',$model,
                '--seed',"$seed",'--lock',$Lock,'--out',$out)
            if(Test-Path -LiteralPath "$out\last.pth"){$arguments+='--resume'}
            if(-not (Test-Path -LiteralPath "$out\completion.json")){
                & $py @arguments
                if($LASTEXITCODE -ne 0){throw 'External training failed.'}
            }
            $evaluation="$out\test_locked"
            if(-not (Test-Path -LiteralPath "$evaluation\evaluation_manifest.json")){
                & $py -B -m pastnet_v2.run evaluate --manifest $manifest --variant $model --seed $seed --lock $Lock --checkpoint "$out\best.pth" --split test --out $evaluation
                if($LASTEXITCODE -ne 0){throw 'Locked external evaluation failed.'}
            }
            if($model -eq 'control'){$controlOutputs+=$evaluation}else{$candidateOutputs+=$evaluation}
        }
    }
}
$candidateList="design\pastnet_v2\results\${Dataset}_candidate_tests.txt"
$controlList="design\pastnet_v2\results\${Dataset}_control_tests.txt"
$candidateOutputs | Set-Content -LiteralPath $candidateList -Encoding UTF8
$controlOutputs | Set-Content -LiteralPath $controlList -Encoding UTF8
& $py -B -m pastnet_v2.external_report --candidate-list $candidateList --parent-list $controlList --out "design\pastnet_v2\results\${Dataset}_paired_final.json"
if($LASTEXITCODE -ne 0){throw 'External paired report failed.'}
