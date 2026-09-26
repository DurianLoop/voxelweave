"""Fair x4 SwinIR comparison of PC-v1, TTA variance, and committee score."""

from __future__ import annotations

import json
import sys
from pathlib import Path

import pandas as pd

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[1]
OUT = HERE / "plan2_outputs"
sys.path.insert(0, str(ROOT / "design"))
from rasinet.icassp_statistics import ranking_metrics  # noqa: E402


def main() -> None:
    pc = pd.read_csv(ROOT / "design" / "rasinet" / "outputs" / "nested_optimization" / "cross_scale_consistency_per_case.csv")
    pc = pc[pc.dataset.eq("fastmri") & pc.scale.eq(4) & pc.target_model.eq("swinir")][["case", "common_error", "consistency"]]
    tta = pd.read_csv(ROOT / "design" / "rasinet" / "outputs" / "tta_fastmri_unified" / "per_case.csv")[["case", "case_score"]]
    base = pd.read_csv(ROOT / "design" / "rasinet" / "outputs" / "multiscale" / "per_case_scores.csv")
    base = base[base.dataset.eq("fastmri") & base.scale.eq(4) & base.target.eq("swinir") & base.method.eq("target_median")][["case_id", "case_score"]]
    base.columns = ["case", "baseline"]
    merged = pc.merge(tta.rename(columns={"case_score": "tta"}), on="case").merge(base, on="case")
    merged = merged.rename(columns={"consistency": "physical_consistency"})
    merged.to_csv(OUT / "fastmri_x4_swinir_comparator_per_case.csv", index=False)
    result = {method: ranking_metrics(merged.common_error, merged[method]) for method in ("baseline", "tta", "physical_consistency")}
    (OUT / "fastmri_x4_swinir_comparator.json").write_text(json.dumps(result, indent=2), encoding="utf-8")
    print(json.dumps(result, indent=2))


if __name__ == "__main__":
    main()
