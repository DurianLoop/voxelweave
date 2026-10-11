"""Use the validated converter on source-qualified test labels; no task scoring."""
from vs_seg_original_mask_cpu_development import ROOT, main

if __name__ == "__main__":
    main(prepared_path=ROOT / "literature/source_cache/vs_seg_full_volume_source_gate_2026-10-02/attempt_01.json",
         output_directory=ROOT / "experiments/vs_seg_full_volume_source_masks",
         plan_path=ROOT / "VS_SEG_FULL_VOLUME_HELDOUT_SOURCE_GATE_PLAN_2026-10-02.md")
