$ErrorActionPreference = 'Stop'

$paperRoot = (Resolve-Path 'D:\MRI\design\paper').Path
if ($paperRoot -ne 'D:\MRI\design\paper') {
    throw "Unexpected paper root: $paperRoot"
}

function Ensure-Dir([string]$relativePath) {
    $path = Join-Path $paperRoot $relativePath
    New-Item -ItemType Directory -Force -Path $path | Out-Null
    return $path
}

function Move-Checked([string]$sourceRelative, [string]$destinationRelative) {
    $source = Join-Path $paperRoot $sourceRelative
    $destination = Join-Path $paperRoot $destinationRelative
    if (-not (Test-Path -LiteralPath $source)) {
        throw "Missing source: $source"
    }
    if (Test-Path -LiteralPath $destination) {
        throw "Destination already exists: $destination"
    }
    $destinationParent = Split-Path -Parent $destination
    New-Item -ItemType Directory -Force -Path $destinationParent | Out-Null
    Move-Item -LiteralPath $source -Destination $destination
}

Ensure-Dir 'ARCHIVE' | Out-Null
Ensure-Dir 'ARCHIVE\PLANS\00_FOUNDATION' | Out-Null
Ensure-Dir 'ARCHIVE\PLANS\PLAN02_TO_PLAN04' | Out-Null
Ensure-Dir 'ARCHIVE\PLANS\PLAN05' | Out-Null
Ensure-Dir 'ARCHIVE\PLANS\PLAN06' | Out-Null
Ensure-Dir 'ARCHIVE\PLANS\PLAN07' | Out-Null
Ensure-Dir 'ARCHIVE\PLANS\PLAN08' | Out-Null
Ensure-Dir 'ARCHIVE\RESEARCH_RECORDS\FOUNDATION_AND_NOTES' | Out-Null
Ensure-Dir 'ARCHIVE\RESEARCH_RECORDS\REPORTS_AND_AUDITS' | Out-Null
Ensure-Dir 'ARCHIVE\RESEARCH_RECORDS\TOOLS_AND_OUTPUTS' | Out-Null
Ensure-Dir 'DOCUMENTATION\CURRENT' | Out-Null
Ensure-Dir 'DOCUMENTATION\HISTORY' | Out-Null
Ensure-Dir 'CVPR\archive' | Out-Null
Ensure-Dir 'TMI\archive' | Out-Null

# Previous manuscript versions.
Move-Checked 'CVPR\CVPR_RECOVERED' 'CVPR\archive\CVPR_RECOVERED'
Move-Checked 'CVPR\CVPR_UPGRADE' 'CVPR\archive\CVPR_UPGRADE'
Move-Checked 'TMI\TMI_MANUSCRIPT' 'TMI\archive\TMI_MANUSCRIPT'
Move-Checked 'TMI\TMI_MANUSCRIPT_MASTER' 'TMI\archive\TMI_MANUSCRIPT_MASTER'
Move-Checked 'TMI\TMI_MANUSCRIPT_SUBMISSION' 'TMI\archive\TMI_MANUSCRIPT_SUBMISSION'
Move-Checked 'TMI\TMI_MANUSCRIPT_SUBMISSION_FINAL' 'TMI\archive\TMI_MANUSCRIPT_SUBMISSION_FINAL'

# Existing packaged snapshots.
Move-Checked 'ARCHIVE_PACKAGES' 'ARCHIVE\PACKAGES'

# Plan foundation.
Move-Checked 'goal.md' 'ARCHIVE\PLANS\00_FOUNDATION\goal.md'
Move-Checked 'PLAN.md' 'ARCHIVE\PLANS\00_FOUNDATION\PLAN.md'

# Plans 2--4 shared one historical working directory, so scripts and outputs stay together.
$earlyPlanItems = @(
    'plan2.md','PLAN2_EXECUTION_SUMMARY.md','plan2_outputs',
    'plan2_boundary_analysis.py','plan2_common_mode_mechanism.py','plan2_confirmatory_analysis.py',
    'plan2_context_controls.py','plan2_geometry_audit.py','plan2_localization_analysis.py',
    'plan2_localization_ningxia.py','plan2_localization_statistics.py','plan2_synthesis_analysis.py','plan2_tta_comparator.py',
    'plan3.md','PLAN3_MILESTONE_REPORT.md','PLAN3_RESEARCH_REPORT.md','plan3_outputs',
    'plan3_anchor_curvature.py','plan3_anchor_witness.py','plan3_asymmetric_context_synthetic.py',
    'plan3_bias_diversity_decomposition.py','plan3_boundary_variance.py','plan3_context_geometry.py',
    'plan3_diversity_validation.py','plan3_hat_tta.py','plan3_ixi_prereconstruction.py','plan3_joint_witness.py',
    'plan3_model_family_analysis.py','plan3_motion_proxy.py','plan3_ningxia_tta.py','plan3_prereconstruction_triangle.py',
    'plan3_scale_control.py','plan3_scaling_decomposition.py','plan3_spectral_spatial.py','plan3_tta_joint_analysis.py','plan3_variance_bootstrap.py',
    'plan4.md','PLAN_4_REPORT.md','PLAN4_LITERATURE_AND_NOVELTY.md','plan4_outputs',
    'plan4_adaptive_acquisition_test.py','plan4_adaptive_baselines.py','plan4_analytical_disjoint.py',
    'plan4_curvature_spacing_analysis.py','plan4_curvature_spacing_panel.py','plan4_disjoint_anchor_intervention.py',
    'plan4_disjoint_ningxia.py','plan4_interleaved_x2_reliability.py','plan4_max_shared_control.py',
    'plan4_overlap_levels_analysis.py','plan4_overlap_paired_test.py','plan4_reproducibility_audit.py'
)
foreach ($item in $earlyPlanItems) {
    Move-Checked $item (Join-Path 'ARCHIVE\PLANS\PLAN02_TO_PLAN04' $item)
}

Move-Checked 'plan5.md' 'ARCHIVE\PLANS\PLAN05\plan5.md'
foreach ($item in @('plan6.md','PLAN6_FINAL_AUDIT.md','PLAN6_HYPOTHESES_AND_EXPERIMENTS.md','PLAN6_REVIEWER_RED_TEAM.md')) {
    Move-Checked $item (Join-Path 'ARCHIVE\PLANS\PLAN06' $item)
}
Move-Checked 'plan7.md' 'ARCHIVE\PLANS\PLAN07\plan7.md'
Move-Checked 'PLAN7_ACCEPTANCE_OPTIMIZATION' 'ARCHIVE\PLANS\PLAN07\PLAN7_ACCEPTANCE_OPTIMIZATION'
Move-Checked 'plan8.md' 'ARCHIVE\PLANS\PLAN08\plan8.md'
Move-Checked 'CVPR_plan8_final_report.md' 'ARCHIVE\PLANS\PLAN08\CVPR_plan8_final_report.md'

# Current overview documents.
Move-Checked 'FINAL_COMPREHENSIVE_REPORT_ZH.md' 'DOCUMENTATION\CURRENT\FINAL_COMPREHENSIVE_REPORT_ZH.md'
Move-Checked 'CONVERSATION_DECISION_PATH_ZH_20260821.md' 'DOCUMENTATION\HISTORY\CONVERSATION_DECISION_PATH_ZH_20260821.md'
Move-Checked 'README.md' 'DOCUMENTATION\HISTORY\README_20260827.md'

$foundationDocs = @(
    'ACTIVE_RESEARCH.md','CASE_INFLUENCE_ANALYSIS.md','CLAIM_EVIDENCE_MATRIX.md','CLAIMS.md',
    'CONSENSUS_ERROR_RESEARCH.md','CURRENT_BEST_CLAIM.md','ERROR_TAXONOMY.md','EXPERIMENT_NOTES.md',
    'EXPERIMENTS.md','FIGURE_INDEX.md','FROZEN_METHOD.md','HYPOTHESES.md','HYPOTHESIS_PORTFOLIO.md',
    'INNOVATION_SCORECARD.md','IXI_X2_FROZEN_EVALUATION.md','LITERATURE.md','MECHANISM_REPORT.md',
    'PAPER_OUTLINE.md','REPRODUCIBILITY.md','RESEARCH_FRONTIER.md','RESEARCH_LOG.md','RESEARCH_STATE.md',
    'STATISTICAL_VALIDITY.md','THEORY.md','TMI_ERROR_TAXONOMY.md'
)
foreach ($item in $foundationDocs) {
    Move-Checked $item (Join-Path 'ARCHIVE\RESEARCH_RECORDS\FOUNDATION_AND_NOTES' $item)
}

$reportDocs = @(
    'AUDIT_REPORT.md','FALSIFICATION_REPORT.md','FINAL_RESEARCH_REPORT.md','NOVELTY_AUDIT.md',
    'PAPER_EXPANSION_GAP_AUDIT.md','PROJECT_EXHAUSTION_AUDIT.md','PUBLICATION_READINESS_REPORT.md',
    'REVIEWER_REDTEAM.md','SUBMISSION_STRATEGY.md','TWO_PAPERS_PROGRESS_REPORT.md','TWO_PAPERS_PROGRESS_REPORT_20260813.md'
)
foreach ($item in $reportDocs) {
    Move-Checked $item (Join-Path 'ARCHIVE\RESEARCH_RECORDS\REPORTS_AND_AUDITS' $item)
}

Move-Checked 'audit_evidence.py' 'ARCHIVE\RESEARCH_RECORDS\TOOLS_AND_OUTPUTS\audit_evidence.py'
Move-Checked 'audit_outputs' 'ARCHIVE\RESEARCH_RECORDS\TOOLS_AND_OUTPUTS\audit_outputs'

Move-Checked 'reorganize_paper_20260907.ps1' 'ARCHIVE\REORGANIZATION\reorganize_paper_20260907.ps1'

Write-Output 'REORGANIZATION_COMPLETE'
