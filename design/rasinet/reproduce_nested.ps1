param(
    [ValidateSet("from-precomputed", "recompute-features")]
    [string]$Mode = "from-precomputed",
    [string]$Python = "D:\conda\envs\MRI\python.exe"
)

$ErrorActionPreference = "Stop"
$RepoRoot = (Resolve-Path (Join-Path $PSScriptRoot "..\..")).Path
$env:PYTHONPATH = (Resolve-Path (Join-Path $RepoRoot "design")).Path
Set-Location $RepoRoot

if ($Mode -eq "recompute-features") {
    & $Python -u -B -m rasinet.nested_precompute --scope development --workers 2
    & $Python -u -B -m rasinet.nested_precompute --scope ningxia --workers 2
    & $Python -u -B -m rasinet.cross_scale_physical
}

& $Python -u -B -m rasinet.nested_selection --stage public
& $Python -u -B -m rasinet.nested_selection --stage nested
& $Python -u -B -m rasinet.nested_selection_robust
& $Python -u -B -m rasinet.nested_analysis
& $Python -u -B -m rasinet.nested_transfer_analysis
& $Python -u -B -m rasinet.generate_nested_paper_assets
& $Python -u -B -m unittest tests.test_rasinet_nested_optimization

Set-Location (Join-Path $RepoRoot "design\rasinet\paper_updated")
pdflatex -interaction=nonstopmode -halt-on-error paper_icassp_regular_nested_optimized.tex
bibtex paper_icassp_regular_nested_optimized
pdflatex -interaction=nonstopmode -halt-on-error paper_icassp_regular_nested_optimized.tex
pdflatex -interaction=nonstopmode -halt-on-error paper_icassp_regular_nested_optimized.tex
pdflatex -interaction=nonstopmode -halt-on-error paper_extended_nested_optimized.tex
bibtex paper_extended_nested_optimized
pdflatex -interaction=nonstopmode -halt-on-error paper_extended_nested_optimized.tex
pdflatex -interaction=nonstopmode -halt-on-error paper_extended_nested_optimized.tex
