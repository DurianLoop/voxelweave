$ErrorActionPreference = 'Stop'
$source = 'D:\MRI\design\paper\TMI\TMI_MANUSCRIPT'
$target = 'D:\MRI\design\paper\TMI\TMI_MANUSCRIPT_MASTER'
Copy-Item -LiteralPath (Join-Path $source 'IEEEtran.cls') -Destination (Join-Path $target 'IEEEtran.cls') -Force
Copy-Item -LiteralPath (Join-Path $source 'references.bib') -Destination (Join-Path $target 'references.bib') -Force
Copy-Item -LiteralPath (Join-Path $source 'main.tex') -Destination (Join-Path $target 'main.tex') -Force
Get-ChildItem -LiteralPath (Join-Path $source 'figures') -File | ForEach-Object {
    Copy-Item -LiteralPath $_.FullName -Destination (Join-Path (Join-Path $target 'figures') $_.Name) -Force
}
Write-Host 'TMI master assets copied.'
