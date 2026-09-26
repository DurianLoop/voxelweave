$ErrorActionPreference = "Stop"

$inventoryRoot = Join-Path $PSScriptRoot "asset_inventory"
$weights = Import-Csv -LiteralPath (Join-Path $inventoryRoot "weights_classified.csv")
$duplicateRows = Import-Csv -LiteralPath (Join-Path $inventoryRoot "weights_large_exact_duplicates.csv") -ErrorAction SilentlyContinue

function Get-CanonicalPriority {
    param([Parameter(Mandatory = $true)][string]$Path)

    if ($Path -like "D:\SAM\assets\checkpoints\*") { return 0 }
    if ($Path -like "D:\MRI\*") { return 1 }
    if ($Path -like "D:\CoughKD\*") { return 2 }
    if ($Path -like "D:\SAM\runs\*") { return 3 }
    if ($Path -like "D:\SAM\*") { return 4 }
    return 9
}

$duplicateActionByPath = @{}
if ($duplicateRows) {
    foreach ($group in ($duplicateRows | Group-Object SHA256)) {
        $ordered = $group.Group | Sort-Object `
            @{ Expression = { Get-CanonicalPriority -Path $_.Path } }, `
            @{ Expression = { $_.Path } }
        $canonicalPath = $ordered[0].Path
        foreach ($row in $ordered) {
            if ($row.Path -eq $canonicalPath) {
                $duplicateActionByPath[$row.Path] = "canonical_exact_duplicate_group"
            }
            else {
                $duplicateActionByPath[$row.Path] = "skip_exact_duplicate"
            }
        }
    }
}

$plan = foreach ($weight in $weights) {
    if ($weight.Class -eq "core_master_source") {
        $action = "represented_by_core_archive"
    }
    elseif ($duplicateActionByPath.ContainsKey($weight.Path)) {
        $action = $duplicateActionByPath[$weight.Path]
    }
    else {
        $action = "copy"
    }

    switch ($weight.Project) {
        "MRI" { $sourceRoot = "D:\MRI" }
        "SAM" { $sourceRoot = "D:\SAM" }
        "CoughKD" { $sourceRoot = "D:\CoughKD" }
        default { $sourceRoot = "C:\Users\user\Downloads" }
    }
    $relativePath = $weight.Path.Substring($sourceRoot.Length).TrimStart("\")

    [pscustomobject]@{
        Action             = $action
        Project            = $weight.Project
        SourcePath         = $weight.Path
        SizeBytes          = [int64]$weight.SizeBytes
        TargetRelativePath = "ResearchVault\models\$($weight.Project)\$relativePath"
    }
}

$coreArchive = @(
    [pscustomobject]@{
        Action             = "copy"
        Project            = "MRI_CORE_ARCHIVE"
        SourcePath         = "D:\MRI\exports\experiment_master_table_weights_2026-09-20.zip"
        SizeBytes          = (Get-Item -LiteralPath "D:\MRI\exports\experiment_master_table_weights_2026-09-20.zip").Length
        TargetRelativePath = "ResearchVault\models\MRI_CORE_ARCHIVE\experiment_master_table_weights_2026-09-20.zip"
    },
    [pscustomobject]@{
        Action             = "copy"
        Project            = "MRI_CORE_ARCHIVE"
        SourcePath         = "D:\MRI\exports\experiment_master_table_weights_2026-09-20.zip.sha256"
        SizeBytes          = (Get-Item -LiteralPath "D:\MRI\exports\experiment_master_table_weights_2026-09-20.zip.sha256").Length
        TargetRelativePath = "ResearchVault\models\MRI_CORE_ARCHIVE\experiment_master_table_weights_2026-09-20.zip.sha256"
    }
)

$completePlan = @($coreArchive) + @($plan)
$completePlan |
    Export-Csv -LiteralPath (Join-Path $inventoryRoot "weights_copy_plan.csv") -NoTypeInformation -Encoding UTF8

$completePlan |
    Group-Object Action |
    ForEach-Object {
        [pscustomobject]@{
            Action  = $_.Name
            Files   = $_.Count
            SizeGiB = [math]::Round((($_.Group | Measure-Object SizeBytes -Sum).Sum) / 1GB, 2)
        }
    } |
    Sort-Object Action |
    Format-Table -AutoSize
